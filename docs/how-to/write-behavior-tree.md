# How-to: Написать Behaviour Tree

## Проблема

Нужно задать последовательность действий для AI-агента: двигаться, кликать, ждать, принимать решения через LLM — в виде дерева поведения.

## Решение

### 1. Базовая структура

Behaviour Tree (BT) состоит из узлов, наследующих `BehaviorTreeNode` (`mind/core.py`):

```python
class BehaviorTreeNode(ABC):
    class Params(BaseModel): pass

    def __init__(self, params: Optional[BaseModel] = None):
        self.params = params or self.Params()
        self.status: Status = Status.FAILURE

    @abstractmethod
    async def tick(self, world, entity, blackboard) -> Status:
        pass
```

Каждый `tick()` возвращает одно из трёх состояний:

```python
class Status(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RUNNING = "RUNNING"
```

### 2. Композиты (ветвление)

**Sequence** (`mind/composites.py:11`) — выполняет детей по порядку; останавливается на первом FAILURE:
```python
Sequence([node1, node2, node3])
```

**Selector** (`mind/composites.py:37`) — выполняет детей по порядку; останавливается на первом SUCCESS:
```python
Selector([try_first, fallback, last_resort])
```

**Parallel** (`mind/composites.py:64`) — выполняет всех детей одновременно:
```python
Parallel([sensor_node, movement_node])
```
Возвращает FAILURE если хоть один упал, SUCCESS если все успешны, RUNNING пока кто-то в RUNNING.

### 3. Декораторы (модификаторы)

**Inverter** (`mind/decorators.py:11`) — инвертирует SUCCESS ↔ FAILURE:
```python
Inverter(some_node)
```

**Succeeder** (`mind/decorators.py:27`) — всегда возвращает SUCCESS:
```python
Succeeder(may_fail_node)
```

**RepeatUntilFail** (`mind/decorators.py:42`) — повторяет ребёнка, пока тот не вернёт FAILURE:
```python
RepeatUntilFail(action_node)
```

### 4. Листовые узлы (actions)

Все зарегистрированы через `@Registry.register_node()` и находятся в `mind/actions.py`:

| Узел | Назначение | Параметры |
|------|-----------|-----------|
| `ChangeDirectionNode(direction="UP")` | Меняет направление змейки | direction |
| `WaitNode(duration=1.0)` | Ждёт заданное время | duration |
| `ClickNode(x=100, y=200)` | Эмулирует клик мыши | x, y, button |
| `MoveNode(x=500, y=300)` | Эмулирует движение мыши | x, y, duration |
| `KeyNode(key="enter")` | Эмулирует нажатие клавиши | key, action |
| `SetBlackboardVariable(key, value)` | Сохраняет значение в blackboard | key, value |

**Важно**: `ClickNode`, `MoveNode`, `KeyNode` и `ChangeDirectionNode` кладут Intent в `ActionBufferComponent` сущности. Для этого у сущности должен быть этот компонент.

### 5. LLM-узел

`LLMInferenceNode` (`mind/llm.py:24`) асинхронно вызывает LLM через `AIAdapter`:

```python
LLMInferenceNode(
    prompt_template="What is {target}?",
    output_key="llm_response",
    adapter=MockAdapter()  # или кастомный адаптер
)
```

Результат сохраняется в blackboard под ключом `output_key`. Пока LLM отвечает, узел возвращает `RUNNING`.

### 6. Swarm-узлы

`SendMessageNode` (`mind/swarm_nodes.py:15`) — отправляет сообщение другому агенту или broadcast.

`ListenForEventNode` (`mind/swarm_nodes.py:49`) — ждёт сообщение по топику; при получении кладёт payload в blackboard.

Оба требуют `MailboxComponent` на сущности.

### 7. Blackboard (общая память)

```python
class Blackboard(BaseModel):
    data: Dict[str, Any] = Field(default_factory=dict)

    def set(self, key, value): self.data[key] = value
    def get(self, key, default=None): return self.data.get(key, default)
    def has(self, key): return key in self.data
```

Используется для обмена данными между узлами дерева.

### 8. Подключение к системе

Узел корня дерева хранится в `BrainComponent` (`mind/brain.py:13`):

```python
@Registry.register_component
class BrainComponent(BaseComponent):
    root: Optional[BehaviorTreeNode] = None
    blackboard: Blackboard = Field(default_factory=Blackboard)
    active: bool = True
```

`AI_BrainSystem` в фазе `COGNITION` вызывает `root.tick()` для каждой сущности с `BrainComponent`:

```python
# mind/brain.py:30
for entity_id, brain in entities.items():
    if not brain.active or not brain.root:
        continue
    await brain.root.tick(world, entity_id, brain.blackboard)
```

### 9. Полный пример

```python
from serpentine.mind.core import BehaviorTreeNode, Blackboard, Status
from serpentine.mind.composites import Sequence, Selector
from serpentine.mind.actions import (
    ChangeDirectionNode, WaitNode, MoveNode, ClickNode
)
from serpentine.mind.decorators import RepeatUntilFail

# Дерево: бесконечно искать еду
tree = RepeatUntilFail(
    Sequence([
        ChangeDirectionNode(direction="RIGHT"),
        WaitNode(duration=0.5),
        ChangeDirectionNode(direction="DOWN"),
        WaitNode(duration=0.3),
    ])
)

# Подключить к сущности
from serpentine.mind.brain import BrainComponent
world.add_component(entity_id, BrainComponent(root=tree))
```

## Связанное

- How-to: добавить компонент
- Reference: Mind API
- Tutorial: создать змейку (ECS)
