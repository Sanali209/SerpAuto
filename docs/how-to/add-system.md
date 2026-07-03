# How-to: Добавить новую систему в tick-цикл

## Проблема

Вам нужно добавить новую логику, которая выполняется каждый tick движка — например, проверка состояния, обновление позиций, обработка ввода.

## Решение

### 1. Создайте класс, наследующий `System`

Базовый класс `System` (`systems/base.py`):

```python
from abc import ABC, abstractmethod
from serpentine.core.world import World

class System(ABC):
    def __init__(self, tick_rate: int = None):
        self.tick_rate = tick_rate       # Специфичный TPS (None = каждый tick)
        self._accumulator = 0.0          # Внутренний аккумулятор для tick_rate

    @abstractmethod
    async def update(self, world: World, dt: float) -> None:
        pass
```

### 2. Зарегистрируйте через декоратор

Декоратор `@Registry.register_system` принимает:
- `phase: SystemPhase` — фаза, в которой выполняется система
- `modes: List[EngineMode]` — режимы, где система активна
- `priority: int` — порядок внутри фазы (выше = раньше)
- `tick_rate: Optional[int]` — если системе нужен свой TPS

```python
from serpentine.core.registry import Registry, SystemPhase, EngineMode
from serpentine.systems.base import System
from serpentine.core.world import World

@Registry.register_system(
    phase=SystemPhase.INTERNAL_PHYSICS,
    modes=[EngineMode.ARCHITECT, EngineMode.PRODUCTION],
    priority=15,
    tick_rate=10  # 10 раз в секунду
)
class MyPhysicsSystem(System):
    async def update(self, world: World, dt: float) -> None:
        # Логика системы
        for eid, comp in world.get_components(MyComponent).items():
            comp.data += 1
```

### 3. 8 фаз tick-цикла

Фазы из `SystemPhase` (`core/registry.py`, строка 17) выполняются **строго по порядку**:

| Фаза | Назначение | Примеры |
|------|-----------|---------|
| `INPUT` | Сбор ввода | `HumanInputSystem`, `SensoryInputSystem`, `SnakeStateReaderSystem` |
| `MAIL_ROUTING` | Маршрутизация сообщений между агентами | `MessageRouterSystem` |
| `PERCEPTION` | Обработка сенсорных данных | `PerceptionPipelineSystem` |
| `INTERNAL_PHYSICS` | Физика симуляции | `SnakeActionSystem`, `SnakeLocomotionSystem`, `SnakeCollisionSystem` |
| `COGNITION` | Исполнение Behaviour Trees | `AI_BrainSystem` |
| `EXECUTION` | Исполнение действий в реальном мире | `ActionExecutionSystem` |
| `REWARD` | Расчёт наград (RL) | `EnvironmentJudgeSystem` |
| `TELEMETRY` | GUI, логирование, рендер | `GUIDebugSystem`, `DatasetLoggerSystem`, `RenderSystem` |

### 4. Как движок выбирает системы

`SerpentineEngine._initialize_systems()` (строка 97):

```python
for phase in SystemPhase:
    system_classes = self._mode_strategy.get_systems(phase)
    for cls in system_classes:
        metadata = Registry._system_metadata.get(cls.__name__)
        system = cls()
        if metadata and metadata.tick_rate:
            system.tick_rate = metadata.tick_rate
        self.systems[phase].append(system)
```

`ModeStrategy.get_systems()` вызывает `Registry.get_systems_for_phase(phase, mode)`, которая фильтрует по фазе и режиму, сортирует по `priority`.

### 5. Tick-rate системы

Если у системы указан `tick_rate`, движок аккумулирует dt и вызывает `update()` только когда накоплено >= `1.0/tick_rate` секунд:

```python
# engine.py: строка 172
while system._accumulator >= target_dt:
    await system.update(self.world, target_dt)
    system._accumulator -= target_dt
```

Если `tick_rate = None` — система вызывается **каждый tick** с переменным dt.

### 6. Правила

| Правило | Пояснение |
|---------|-----------|
| Не модифицировать `_components` напрямую | Используйте `world.add_component()`, `world.remove_component()` |
| Не удалять сущности во время итерации | Делайте список на удаление (mark-and-sweep) |
| `async` обязательно | Все системы — `async def update()` |
| Импорт файла | Файл с системой должен быть импортирован до старта (в `__init__` или в точке входа) |

### 7. Пример из кода

**SnakeActionSystem** (`systems/snake.py`):
```python
@Registry.register_system(phase=SystemPhase.INTERNAL_PHYSICS, modes=[...], priority=20)
class SnakeActionSystem(System):
    async def update(self, world: World, dt: float) -> None:
        buffers = world.get_components(ActionBufferComponent)
        snakes = world.get_components(SnakeBodyComponent)
        for entity_id, buffer in buffers.items():
            if entity_id not in snakes:
                continue
            # обработка ChangeDirectionIntent
```

## Связанное

- How-to: добавить компонент
- Reference: ECS API
- Explanation: архитектура + фазы
