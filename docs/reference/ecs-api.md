# Reference: ECS API

## EntityID

`serpentine.core.entity`

```python
from uuid import UUID, uuid4
from typing import NewType

EntityID = NewType("EntityID", UUID)

def create_entity_id() -> EntityID:
    """Генерирует новый UUID4."""
    return EntityID(uuid4())
```

`EntityID` — это просто UUID. Все сущности в World идентифицируются через него.

---

## World

`serpentine.core.world`

ECS-хранилище. Содержит набор сущностей и компонентов.

### Основные методы

```python
class World:
    def __init__(self):
        self._entities: Set[EntityID] = set()
        self._components: Dict[Type[BaseComponent], Dict[EntityID, BaseComponent]] = {}
        self._query_cache: Dict[Tuple[Type[BaseComponent], ...], Set[EntityID]] = {}
```

#### create_entity(uid=None) -> EntityID
Создаёт новую сущность. Если `uid` не передан, генерируется UUID4.

```python
eid = world.create_entity()
eid_with_id = world.create_entity(uid=my_uuid)
```

#### delete_entity(entity_id)
Удаляет сущность и все её компоненты. Автоматически инвалидирует кеш запросов.

#### add_component(entity_id, component)
Добавляет компонент к сущности. Компонент — любой наследник `BaseComponent`.

```python
world.add_component(eid, TransformComponent(x=10.0, y=20.0))
```

Выбрасывает `ValueError`, если сущность не существует.

#### remove_component(entity_id, component_type)
Удаляет компонент указанного типа с сущности.

#### get_component(entity_id, component_type) -> Optional[Component]
Возвращает один компонент сущности или None.

```python
t = world.get_component(eid, TransformComponent)
```

#### get_components(component_type) -> Dict[EntityID, Component]
Возвращает словарь `{EntityID: Component}` для всех сущностей, имеющих этот компонент.

```python
all_transforms = world.get_components(TransformComponent)
```

#### has_component(entity_id, component_type) -> bool
Проверяет наличие компонента.

#### get_entities_with(*component_types) -> Iterator[Tuple[EntityID, ...]]
Эффективный запрос: возвращает итератор кортежей `(EntityID, comp1, comp2, ...)`.

```python
for eid, transform, stats in world.get_entities_with(TransformComponent, StatsComponent):
    ...
```

Использует кеш: `_query_cache[tuple(sorted_types)] -> Set[EntityID]`. Инвалидируется при любом изменении компонента.

#### take_snapshot() -> Dict
Сериализует весь мир в JSON-совместимый словарь. Использует `BaseComponent.model_dump(mode='json')`.

#### restore_snapshot(snapshot: Dict)
Восстанавливает мир из словаря. Очищает текущее состояние. Использует `Registry.get_component(name)` для поиска класса компонента и `model_validate()` для десериализации.

---

## BaseComponent

`serpentine.core.component`

```python
class BaseComponent(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
```

Базовый класс для всех ECS-компонентов. Pydantic `BaseModel`.

- Все поля валидируются при создании.
- `model_dump(mode='json')` — сериализация.
- `model_validate(data)` — десериализация.
- `arbitrary_types_allowed=True` разрешает UUID, EntityID и т.д.

---

## Registry

`serpentine.core.registry`

Глобальный реестр компонентов, систем, узлов BT.

### Регистрация компонента

```python
@Registry.register_component
class MyComponent(BaseComponent): ...
```

- Ключ: `__name__` класса.
- Присваивается бит-маска `1 << index`.
- Метод `Registry.get_component(name)` — поиск по имени.
- `Registry.get_all_components()` — все компоненты.

### Регистрация системы

```python
@Registry.register_system(phase=SystemPhase.INPUT, modes=[EngineMode.ARCHITECT], priority=10, tick_rate=30)
class MySystem(System): ...
```

Параметры декоратора:
| Поле | Тип | По умолчанию |
|------|-----|-------------|
| `phase` | `SystemPhase` | обязательный |
| `modes` | `List[EngineMode]` | все режимы |
| `priority` | `int` | 0 |
| `tick_rate` | `Optional[int]` | None |

Методы:
- `Registry.get_systems_for_phase(phase, mode)` — системы для фазы и режима, отсортированные по priority (desc).
- `Registry.get_all_systems()` — все системы.
- `Registry.get_component(name)` — поиск по имени.

### Регистрация узла BT

```python
@Registry.register_node(category="Actions", icon="🐍", description="...")
class MyNode(BehaviorTreeNode): ...
```

Методы:
- `Registry.get_node(name)` — класс узла.
- `Registry.get_all_nodes()` — все узлы.
- `Registry.get_node_metadata(name)` — метаданные узла.

### EngineMode

```python
class EngineMode(str, Enum):
    ARCHITECT = "ARCHITECT"
    PRODUCTION = "PRODUCTION"
    TEACHER = "TEACHER"
    GYMNASIUM = "GYMNASIUM"
    CONTINUOUS_LEARNING = "CONTINUOUS_LEARNING"
```

### SystemPhase (8 фаз)

```python
class SystemPhase(str, Enum):
    INPUT = "INPUT"
    MAIL_ROUTING = "MAIL_ROUTING"
    PERCEPTION = "PERCEPTION"
    INTERNAL_PHYSICS = "INTERNAL_PHYSICS"
    COGNITION = "COGNITION"
    EXECUTION = "EXECUTION"
    REWARD = "REWARD"
    TELEMETRY = "TELEMETRY"
```

---

## RegistryV2

`serpentine.core.registry_v2`

Альтернативный регистр с категоризацией. Используется для GUI-окон и систем с метаданными категорий.

```python
@RegistryV2.register_node(category="Custom", icon="⭐", description="My node")
class MyNode: ...

@RegistryV2.register_system(category="Custom", icon="⚙️", description="My system")
class MySystem: ...

@RegistryV2.register_window(category="Windows", icon="🪟", description="My window")
class MyWindow: ...
```

Методы:
- `get_nodes_by_category(category)` — фильтрация по категории.
- `get_windows_by_category(category)` — окна по категории.
- `get_all_windows()` — все окна.

---

## SerpentineEngine

`serpentine.core.engine`

```python
class SerpentineEngine:
    def __init__(self, mode: EngineMode = EngineMode.ARCHITECT, target_tps: int = 60):
        self.mode = mode
        self._mode_strategy: ModeStrategy = self._create_mode_strategy(mode)
        self.world = World()
        self.target_tps = target_tps
        self.target_tick_time = 1.0 / target_tps
        self.actual_tps = 0.0
        self.systems: Dict[SystemPhase, List[System]] = {}
```

### Основные методы

- `run()` — главный асинхронный цикл.
- `_tick(dt)` — один tick: проходит по всем фазам, вызывает системы.
- `play() / pause() / step()` — управление через GUI-события.
- `set_tps(tps)` — динамическая смена TPS.
- `save_snapshot(filepath)` / `load_snapshot(filepath)` — JSON-снэпшоты.

### Tick-rate системы

Движок поддерживает индивидуальный TPS для систем. Если у системы `tick_rate` задан, `_accumulator` накапливает dt, и `update()` вызывается только когда накоплено достаточно времени.

---

## EventBus

`serpentine.core.event_bus`

```python
class EventBus:
    _subscribers: Dict[str, List[Callable]] = {}

    @classmethod
    def subscribe(cls, event_type: str, callback): ...
    @classmethod
    def publish(cls, event_type: str, data=None): ...

GUIEventBus = EventBus
```

Используется для слабой связности: `GUIDebugSystem` публикует `ENGINE_PLAY`, `ENGINE_PAUSE` и т.д., а `SerpentineEngine` подписывается на них.

---

## SelectionService

`serpentine.core.selection`

Синглтон для управления выделением в GUI:

```python
SelectionService.set_selected(item, item_type)  # публикует ON_SELECTION_CHANGED
SelectionService.get_selected()
SelectionService.clear_selection()
```

---

## SceneManager / SceneLoader / SceneSaver / SceneValidator

`serpentine.core.scene.*`

```python
class SceneManager:
    def __init__(self, world: World): ...
    def load_scene(self, filepath: str): ...
    def save_scene(self, filepath: str, name="Scene", description=""): ...
    def transition_to_scene(self, filepath: str): ...
```

---

## SerpentineGymEnv

`serpentine.core.gym_wrapper`

gym.Env-совместимая обёртка для RL:

- `action_space = spaces.Discrete(4)` — UP/DOWN/LEFT/RIGHT.
- `observation_space = spaces.Box(0, 3, (H, W))` — grid-карта.
- `reset()` — очищает мир, создаёт змейку и еду.
- `step(action)` — маппит action в `ChangeDirectionIntent`, тикает движок, возвращает obs/reward/done.
- Использует `InternalGridPerception` для конвертации `snake_state` в grid.

---

## SwarmMessage

`serpentine.core.messages`

```python
class SwarmMessage(BaseModel):
    sender_id: EntityID
    recipient_id: Optional[EntityID] = None  # None = broadcast
    topic: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)
    ttl: float = 5.0
```

## Полный список компонентов (13 штук)

| Компонент | Файл | Назначение |
|-----------|------|------------|
| `TransformComponent` | `standard.py` | Позиция, иерархия |
| `StatsComponent` | `standard.py` | Здоровье, alive |
| `ColliderComponent` | `physics.py` | Физический коллайдер |
| `CameraComponent` | `rendering.py` | Камера (FOV, near/far) |
| `MeshComponent` | `rendering.py` | Меш для рендера |
| `MaterialComponent` | `rendering.py` | Материал/шейдер/текстура |
| `SnakeBodyComponent` | `snake.py` | Сегменты змейки, направление |
| `SnakeFoodComponent` | `snake.py` | Еда (value) |
| `SnakeConfigComponent` | `snake.py` | Конфиг сетки, move_interval |
| `RewardComponent` | `simulation.py` | RL-награда |
| `GoalComponent` | `simulation.py` | Цель/статус |
| `DatasetConfigComponent` | `simulation.py` | Путь к датасету, запись |
| `InputControlComponent` | `simulation.py` | Тег управляемости |
| `PerceptionComponent` | `perception/components.py` | Наблюдения |
| `ActionBufferComponent` | `perception/components.py` | Очередь Intent-ов |
| `AgentMetaComponent` | `swarm.py` | Роль/статус агента |
| `MailboxComponent` | `swarm.py` | Входящие/исходящие сообщения |
| `BrainComponent` | `mind/brain.py` | Корень BT + blackboard |
