# Tutorial: Создание змейки через ECS

## Цель

Вручную создать сущность змейки, сущность еды и настроить компоненты/системы для симуляции Snake в Serpentine Engine.

## 1. Базовая ECS-архитектура

Serpentine Engine использует классический ECS:

- **Entity** — UUID (тип `EntityID` из `core/entity.py`)
- **Component** — данные (Pydantic `BaseModel`, наследуют `BaseComponent`)
- **System** — логика (асинхронный `System.update(world, dt)`)

Хранилище — `World` в `core/world.py`. Регистрация — через `Registry` в `core/registry.py`.

## 2. Компоненты для Snake

### SnakeBodyComponent
```python
# components/snake.py:11
@Registry.register_component
class SnakeBodyComponent(BaseComponent):
    segments: List[Tuple[int, int]]  # список (x,y), голова — первый элемент
    current_direction: str = "UP"
    next_direction: str = "UP"
    last_tail_pos: Tuple[int, int] = (0, 0)
```

### SnakeFoodComponent
```python
@Registry.register_component
class SnakeFoodComponent(BaseComponent):
    value: int = 1
```

### SnakeConfigComponent
```python
@Registry.register_component
class SnakeConfigComponent(BaseComponent):
    grid_width: int = 20
    grid_height: int = 20
    cell_size: int = 20
    move_interval: float = 0.1
    last_move_time: float = 0.0
```

Дополнительные компоненты, обязательные для работы:
- `TransformComponent` — позиция (для еды)
- `StatsComponent` — `is_alive` флаг
- `RewardComponent` — `current_reward / cumulative_reward`
- `ActionBufferComponent` — очередь `Intent`-ов
- `PerceptionComponent` — хранилище наблюдений

## 3. Создание сущностей вручную

### Создание змейки

```python
from serpentine.core.engine import SerpentineEngine
from serpentine.core.registry import EngineMode
from serpentine.components.snake import *
from serpentine.components.standard import *
from serpentine.components.simulation import *
from serpentine.perception.components import *

engine = SerpentineEngine(mode=EngineMode.ARCHITECT)
world = engine.world

# 1. Сущность змейки
snake_id = world.create_entity()

# 2. Компонент тела: старт в центре, змейка вверх
snake_body = SnakeBodyComponent(
    segments=[(10, 10), (10, 11), (10, 12)],
    current_direction="UP",
    next_direction="UP"
)
world.add_component(snake_id, snake_body)

# 3. Конфиг сетки
snake_config = SnakeConfigComponent(
    grid_width=20,
    grid_height=20,
    move_interval=0.15
)
world.add_component(snake_id, snake_config)

# 4. Stats (для is_alive)
world.add_component(snake_id, StatsComponent(is_alive=True))

# 5. Reward (для RL-сигнала)
world.add_component(snake_id, RewardComponent())

# 6. ActionBuffer (для приёма Intent-ов)
world.add_component(snake_id, ActionBufferComponent())

# 7. Perception (для наблюдения за миром)
world.add_component(snake_id, PerceptionComponent())
```

### Создание еды

```python
food_id = world.create_entity()
world.add_component(food_id, SnakeFoodComponent(value=1))
world.add_component(food_id, TransformComponent(x=5.0, y=5.0))
```

## 4. Какие системы обработают змейку

При запуске движка (через `asyncio.run(engine.run())`) в фазе `INTERNAL_PHYSICS` выполняются:

1. **SnakeActionSystem (priority=20)** — читает `ActionBufferComponent`, находит `ChangeDirectionIntent` и меняет `snake.next_direction`.
2. **SnakeLocomotionSystem (priority=10)** — сдвигает голову по `current_direction`, обновляет `last_tail_pos`. Учитывает `move_interval` из `SnakeConfigComponent`.
3. **SnakeCollisionSystem (priority=0)** — проверяет стены (`grid_width/grid_height`), самопересечение, еду. При съедании доращивает сегмент и респавнит еду.

Порядок внутри фазы определяется `priority`: **выше число — раньше выполнение**.

## 5. Движение через Intent

Управление змейкой — через очередь `ActionBufferComponent.action_queue`:

```python
from serpentine.mind.intent import ChangeDirectionIntent

buffer = world.get_component(snake_id, ActionBufferComponent)
buffer.enqueue(ChangeDirectionIntent(direction="RIGHT"))
```

Либо через `HumanInputSystem` (клавиши WASD/стрелки) — он кладёт `KeyIntent` в буфер, а `SnakeActionSystem` конвертирует его в `ChangeDirectionIntent`.

## 6. Полный цикл

```
HumanInputSystem (INPUT)
  └─ кладёт KeyIntent
SnakeActionSystem (INTERNAL_PHYSICS, p=20)
  └─ читает KeyIntent → меняет next_direction
SnakeLocomotionSystem (INTERNAL_PHYSICS, p=10)
  └─ смещает сегменты по current_direction
SnakeCollisionSystem (INTERNAL_PHYSICS, p=0)
  └─ проверка стен, тела, еды; респавн еды; is_alive
SnakeStateReaderSystem (INPUT, GYMNASIUM)
  └─ формирует snake_state → PerceptionComponent
PerceptionPipelineSystem (PERCEPTION)
  └─ обрабатывает наблюдения через цепочку PerceptionNode
```

## 7. Полный пример

См. `snake_demo.py` — скрипт, создающий змейку, еду и запускающий движок в Architect mode с GUI.
