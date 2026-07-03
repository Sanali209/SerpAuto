# Reference: Mind API (Cognitive Layer)

## Обзор

Mind-слой SerpAuto отвечает за **когнитивную обработку** — принятие решений на основе восприятия. Реализован через Behaviour Trees (BT), систему намерений (Intents), LLM-адаптеры и меж-агентную коммуникацию (Swarm).

Архитектура: **BrainComponent** → **BehaviorTreeNode** (дерево) → **Intents** (намерения) → **ActionBuffer** (исполнение).

---

## Blackboard

`serpentine.mind.core`

Общая память для узлов дерева. Pydantic-модель с полем `data: Dict[str, Any]`.

```python
class Blackboard(BaseModel):
    data: Dict[str, Any] = Field(default_factory=dict)

    def set(self, key: str, value: Any): ...
    def get(self, key: str, default: Any = None): ...
    def has(self, key: str) -> bool: ...
    def clear(self): ...
```

Любой узел может читать/писать в blackboard. Ключи и значения — произвольные.

---

## Status

`serpentine.mind.core`

```python
class Status(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RUNNING = "RUNNING"
```

Каждый `tick()` BT-узла возвращает одно из трёх состояний. `RUNNING` используется для длительных операций (ожидание, LLM-запрос).

---

## BehaviorTreeNode (ABC)

`serpentine.mind.core`

Базовый класс для всех узлов:

```python
class BehaviorTreeNode(ABC):
    class Params(BaseModel):
        pass

    def __init__(self, params: Optional[BaseModel] = None):
        self.params = params or self.Params()
        self.status: Status = Status.FAILURE

    @abstractmethod
    async def tick(self, world: Any, entity: Any, blackboard: Blackboard) -> Status:
        pass

    def reset(self):
        self.status = Status.FAILURE
```

- `tick()` — асинхронный, принимает `world`, `entity` (EntityID), `blackboard`.
- `reset()` — сброс внутреннего состояния (для узлов с памятью: `WaitNode`, `Sequence`).

---

## BrainComponent

`serpentine.mind.brain`

ECS-компонент, хранящий корень дерева и blackboard:

```python
@Registry.register_component
class BrainComponent(BaseComponent):
    root: Optional[BehaviorTreeNode] = None
    blackboard: Blackboard = Field(default_factory=Blackboard)
    active: bool = True
```

Если `active=False` или `root=None`, `AI_BrainSystem` пропускает эту сущность.

---

## AI_BrainSystem

`serpentine.mind.brain`

Система в фазе `COGNITION`. Для каждой сущности с `BrainComponent` вызывает `root.tick()`:

```python
@Registry.register_system(phase=SystemPhase.COGNITION, modes=[PRODUCTION, TEACHER, GYMNASIUM, CONTINUOUS_LEARNING])
class AI_BrainSystem(System):
    async def update(self, world, dt):
        entities = world.get_components(BrainComponent)
        for entity_id, brain in entities.items():
            if not brain.active or not brain.root:
                continue
            await brain.root.tick(world, entity_id, brain.blackboard)
```

**Внимание**: В режиме `ARCHITECT` `AI_BrainSystem` не активна. Behaviour Tree исполняется только в production-подобных режимах.

---

## Композиты (ветвления)

### Sequence

`serpentine.mind.composites`

Выполняет детей **по порядку**. Останавливается на первом `FAILURE`. Возвращает `SUCCESS`, если все дети успешны.

```python
Sequence([node1, node2, node3])
```

- При `RUNNING` запоминает индекс (`current_child_index`) и продолжает с него на следующем tick.
- При `FAILURE` сбрасывает индекс.

### Selector

Выполняет детей **по порядку**. Останавливается на первом `SUCCESS`. Возвращает `FAILURE`, если все упали.

```python
Selector([try_first, fallback, last_resort])
```

- При `RUNNING` запоминает индекс.

### Parallel

Выполняет **всех детей одновременно** на каждом tick.

```python
Parallel([node_a, node_b])
```

- `FAILURE`, если хоть один упал.
- `SUCCESS`, если все успешны.
- `RUNNING`, если хоть один в RUNNING и ни одного FAILURE.

---

## Декораторы (модификаторы)

### Inverter

Инвертирует результат: `SUCCESS → FAILURE`, `FAILURE → SUCCESS`. `RUNNING` проходит без изменений.

### Succeeder

Всегда возвращает `SUCCESS`, если ребёнок не в `RUNNING`.

### RepeatUntilFail

Повторяет ребёнка, пока тот не вернёт `FAILURE`. После FAILURE возвращает `SUCCESS` (цикл завершён).

---

## Action-узлы

Все регистрируются через `@Registry.register_node(category="Actions", ...)` и находятся в `mind/actions.py`.

Общая схема: узел создаёт `Intent`, кладёт его в `ActionBufferComponent` сущности (через `world.get_component(entity, ActionBufferComponent)`).

### ChangeDirectionNode

```python
ChangeDirectionNode(direction="UP")  # UP, DOWN, LEFT, RIGHT
```

Создаёт `ChangeDirectionIntent`. Обрабатывается `SnakeActionSystem`.

### WaitNode

```python
WaitNode(duration=1.0)
```

Ждёт указанное количество секунд. Использует `asyncio.get_event_loop().time()`. Возвращает `RUNNING`, пока время не истекло.

### ClickNode

```python
ClickNode(x=100, y=200, button="left")
```

Создаёт `ClickIntent`. Исполняется `ActionExecutionSystem` через PyAutoGUI.

### MoveNode

```python
MoveNode(x=500, y=300, duration=0.5)
```

Создаёт `MoveIntent`. Исполняется `ActionExecutionSystem`.

### KeyNode

```python
KeyNode(key="enter", action="press")  # press, down, up
```

Создаёт `KeyIntent`. Исполняется `ActionExecutionSystem`.

### SetBlackboardVariable

```python
SetBlackboardVariable(key="target", value="food")
```

Мгновенно записывает значение в blackboard. Всегда `SUCCESS`.

---

## LLM-узел

### LLMInferenceNode

`serpentine.mind.llm`

```python
LLMInferenceNode(
    prompt_template="What is at position {x},{y}?",
    output_key="llm_result",
    adapter=my_adapter
)
```

- Форматирует `prompt_template` через `str.format(**blackboard.data)`.
- Запускает асинхронный `adapter.generate(prompt, context)`.
- Пока запрос выполняется, возвращает `RUNNING`.
- По завершении сохраняет результат в blackboard под `output_key`.
- Если `adapter = None`, возвращает `FAILURE`.

### AIAdapter (ABC)

```python
class AIAdapter(ABC):
    @abstractmethod
    async def generate(self, prompt: str, context: Dict[str, Any] = None) -> str:
        pass
```

### MockAdapter

```python
class MockAdapter(AIAdapter):
    async def generate(self, prompt: str, context: Dict[str, Any] = None) -> str:
        await asyncio.sleep(0.1)
        return f"Mock response to: {prompt}"
```

Для продакшена реализуйте свой `AIAdapter` (OpenAI, Anthropic, локальная модель).

---

## Intents (намерения)

`serpentine.mind.intent`

Базовый класс и конкретные реализации:

```python
class Intent(BaseModel):
    type: str
    target: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)

class ClickIntent(Intent):
    type: str = "click"
    x: int; y: int; button: str = "left"

class MoveIntent(Intent):
    type: str = "move"
    x: int; y: int; duration: float = 0.0

class KeyIntent(Intent):
    type: str = "key"
    key: str; action: str = "press"

class ChangeDirectionIntent(Intent):
    type: str = "change_direction"
    direction: str  # UP, DOWN, LEFT, RIGHT
```

Intents помещаются в `ActionBufferComponent.action_queue` или `shadow_queue` (для shadow mode — симуляция без реального исполнения).

---

## Swarm-узлы (меж-агентная коммутация)

### SendMessageNode

```python
SendMessageNode(
    recipient_id=target_id,      # статический получатель
    recipient_key="target",       # или динамический из blackboard
    topic="help",
    payload={"need": "food"},    # статический payload
    payload_key="msg_data"       # или динамический из blackboard
)
```

Создаёт `SwarmMessage`, кладёт в `mailbox.outbox`. `MessageRouterSystem` (фаза `MAIL_ROUTING`) разносит сообщения.

### ListenForEventNode

```python
ListenForEventNode(
    topic="help",
    output_key="incoming_help"
)
```

Просматривает `mailbox.inbox` на предмет сообщений с указанным топиком. При нахождении — потребляет его (удаляет из inbox) и сохраняет payload в blackboard. Если сообщений нет — возвращает `FAILURE`.

Оба узла требуют `MailboxComponent` на сущности.

---

## ActionBufferComponent

`serpentine.perception.components`

Мост между Mind (когниция) и Body (исполнение):

```python
@Registry.register_component
class ActionBufferComponent(BaseComponent):
    action_queue: List[Intent] = Field(default_factory=list)
    shadow_queue: List[Intent] = Field(default_factory=list)
    history: List[Tuple[float, Intent]] = Field(default_factory=list)
    last_executed_intent: Optional[Intent] = None

    def enqueue(self, action: Intent): ...
    def enqueue_shadow(self, action: Intent): ...
    def dequeue(self) -> Optional[Intent]: ...
    def clear(self): ...
```

---

## Полный список узлов BT

| Узел | Категория | Описание |
|------|-----------|----------|
| `Sequence` | Composites | Последовательное выполнение |
| `Selector` | Composites | Выполнение до первого успеха |
| `Parallel` | Composites | Параллельное выполнение |
| `Inverter` | Decorators | Инвертирование статуса |
| `Succeeder` | Decorators | Всегда SUCCESS |
| `RepeatUntilFail` | Decorators | Повтор до неудачи |
| `ChangeDirectionNode` | Actions | Смена направления змейки |
| `WaitNode` | Actions | Ожидание по времени |
| `ClickNode` | Actions | Клик мыши |
| `MoveNode` | Actions | Движение мыши |
| `KeyNode` | Actions | Нажатие клавиши |
| `SetBlackboardVariable` | Actions | Запись в blackboard |
| `LLMInferenceNode` | Cognition | Запрос к LLM |
| `SendMessageNode` | Swarm | Отправка сообщения агенту |
| `ListenForEventNode` | Swarm | Прослушивание сообщений |

---

## Связь с другими слоями

```
PerceptionComponent  →  BrainComponent.root.tick()  →  ActionBufferComponent
     (наблюдения)          (дерево решений)              (очередь Intents)
                                                             ↓
                                                    ActionExecutionSystem
                                                    (PyAutoGUI / simulation)
```
