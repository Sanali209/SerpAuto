# Детальная архитектура ядра Serpentine

Этот документ описывает, как абстрактные идеи превращаются в конкретные классы, интерфейсы и потоки данных. Архитектура строится вокруг строгой типизации (Pydantic), асинхронности (asyncio) и неблокирующего ввода-вывода.

## 1. Архитектурная философия

Serpentine — это асинхронный, tick-based движок, построенный на паттерне Entity-Component-System (ECS). Он предназначен для создания автономных агентов, способных оперировать в сложных цифровых средах.

## 2. Структура ECS (Entity-Component-System)

Вся память и состояние системы лежат в объекте `World`. Никакая логика не хранится в сущностях — это просто идентификаторы.

### 2.1. Базовые структуры

```python
import uuid
from pydantic import BaseModel, Field
from typing import Dict, List, Type, Any

# 1. Сущность - просто ID
Entity = uuid.UUID

# 2. Компоненты - строго данные (Pydantic дает нам сериализацию и авто-GUI)
class BaseComponent(BaseModel):
    pass

class PositionComponent(BaseComponent):
    x: float = 0.0
    y: float = 0.0

class PerceptionComponent(BaseComponent):
    visible_entities: List[dict] = Field(default_factory=list)
    passability_grid: List[List[int]] = Field(default_factory=list)
    raw_frame_id: str | None = None # Ссылка на кадр в памяти для дебага

class ActionBufferComponent(BaseComponent):
    queue: List[Any] = Field(default_factory=list) # Очередь BaseAction
    current_action_status: str = "IDLE"

class BrainComponent(BaseComponent):
    status: str = "IDLE" # IDLE, RUNNING_BT, WAITING_LLM
    context: Dict[str, Any] = Field(default_factory=dict)
```

### 2.2. Мир (Registry)

```python
class World:
    def __init__(self):
        # Структура: {ComponentClass: {EntityID: ComponentInstance}}
        self._components: Dict[Type[BaseComponent], Dict[Entity, BaseComponent]] = {}
        self._entities: set[Entity] = set()

    def add_entity(self) -> Entity:
        ent = uuid.uuid4()
        self._entities.add(ent)
        return ent

    def add_component(self, entity: Entity, component: BaseComponent):
        comp_type = type(component)
        if comp_type not in self._components:
            self._components[comp_type] = {}
        self._components[comp_type][entity] = component

    def get_component(self, entity: Entity, comp_type: Type[BaseComponent]):
        return self._components.get(comp_type, {}).get(entity)
```

**Почему так:** `World` легко сериализовать целиком в JSON/SQLite на любом тике. Это дает возможность сохранять сессии, делать "перемотку времени" в дебагере и собирать датасеты для Imitation Learning.

## 3. Главный асинхронный цикл (The Engine Loop)

Главный цикл не должен блокироваться, даже если нейросеть думает 5 секунд или кадр обрабатывается тяжелым фильтром OpenCV.

### Архитектура цикла

```python
import asyncio
import time

class SerpentineEngine:
    def __init__(self):
        self.world = World()
        self.systems = [] # Список всех System (Perception, Brain, Action)
        self.is_running = False
        self.tick_rate = 20 # Ограничение TPS для Production/Debug

    async def run(self):
        self.is_running = True
        last_time = time.perf_counter()

        while self.is_running:
            current_time = time.perf_counter()
            dt = current_time - last_time
            last_time = current_time

            # 1. Выполнение всех систем по очереди
            for system in self.systems:
                await system.update(self.world, dt)

            # 2. Искусственная задержка (Сон)
            # В режиме Gymnasium (RL Gym) мы игнорируем sleep для макс. скорости
            elapsed = time.perf_counter() - current_time
            sleep_time = max(0, (1.0 / self.tick_rate) - elapsed)
            await asyncio.sleep(sleep_time)
```

## 4. Архитектура Пайплайна Восприятия (Perception System)

Сенсорные данные (скриншоты, DOM) проходят через направленный ациклический граф (DAG) фильтров.

**Поток данных:**
* `SensoryInputSystem` делает захват (например, Playwright берет скриншот).
* `PerceptionPipelineSystem` прогоняет кадр через узлы.
* Результат записывается в `PerceptionComponent` агента.

### Структура узла (Node)

Каждый фильтр имеет свою конфигурацию на Pydantic. DearPyGui будет динамически читать эту конфигурацию и строить интерфейс (ползунки, чекбоксы).

```python
class CannyFilterConfig(BaseModel):
    threshold_1: int = Field(100, ge=0, le=255)
    threshold_2: int = Field(200, ge=0, le=255)

class CannyFilterNode:
    def __init__(self):
        self.config = CannyFilterConfig()

    def process(self, frame, context):
        # Применяем OpenCV
        # edges = cv2.Canny(frame, self.config.threshold_1, self.config.threshold_2)

        # Обновляем контекст (передаем дальше по цепочке)
        # context['edges'] = edges
        return frame, context # Placeholder
```

## 5. Гибридный Мозг (Decision System & Behavior Trees)

Здесь сходятся скрипты и нейросети. Дерево поведения опрашивается каждый тик.
Узлы дерева возвращают один из трех статусов: `SUCCESS`, `FAILURE`, `RUNNING`.
Статус `RUNNING` — ключевой для интеграции медленных ML-моделей.

### Как работает узел вызова модели (LLM/CLIP)

```python
class LLMInferenceNode: # (BehaviorTreeNode)
    def __init__(self):
        self.task = None

    async def tick(self, world: World, agent_id: Entity):
        # 1. Если таска уже запущена, проверяем её статус
        if self.task is not None:
            if self.task.done():
                result = self.task.result()
                self.task = None
                # Кладем результат в ActionBuffer агента!
                self._push_action_to_buffer(world, agent_id, result)
                return "SUCCESS"
            else:
                # Модель еще думает, цикл идет дальше, агент ждет
                return "RUNNING"

        # 2. Таски нет - запускаем новую
        perception = world.get_component(agent_id, PerceptionComponent)
        # prompt = self._build_prompt_from_perception(perception)

        # Создаем неблокирующую задачу (вызов API Koyeb/HuggingFace)
        # self.task = asyncio.create_task(self._call_llm_api(prompt))

        return "RUNNING" # Возвращаем RUNNING в этот тик
```

## 6. Исполнение Действий (Action Execution System)

Это финальное звено. Система берет экшены из буфера и транслирует их в реальный мир.
Используется паттерн Command.

```python
class ActionExecutionSystem: # (BaseSystem)
    async def update(self, world: World, dt: float):
        # Ищем всех агентов с буфером действий
        # Note: In real implementation, iterate correctly over entities with component
        # for entity, buffer in world.get_components(ActionBufferComponent):
        pass

            # if not buffer.queue:
            #     continue

            # current_action = buffer.queue[0]

            # Пробуем выполнить
            # status = await current_action.execute()

            # if status in ["SUCCESS", "FAILURE"]:
            #     buffer.queue.pop(0) # Убираем из очереди
            #     buffer.current_action_status = status
            # elif status == "RUNNING":
            #     # Например, экшен "Идти в точку X" может занять несколько тиков
            #     buffer.current_action_status = "RUNNING"
```

## 7. Модульность: GUI и ML Спортзал

Благодаря такой архитектуре, добавление новых режимов вообще не требует изменения ядра.

* **GUI (DearPyGui)**: Вы создаете `DearPyGuiSystem`. В методе `update()` она просто читает `World`, берет `PerceptionComponent`, берет схему из узлов фильтров и вызывает команды отрисовки DPG. Она работает параллельно с логикой.
* **Спортзал (Gymnasium)**: Вы оборачиваешь `SerpentineEngine` в класс `Gym`. Метод `gym.step(action)` кладет action напрямую в `ActionBufferComponent` агента, вручную вызывает `engine.tick()` один раз и возвращает измененный `PerceptionComponent` и `RewardComponent` обратно в алгоритм обучения.

## 8. Директории проекта

```
serpentine_engine/
├── core/               # Базовые классы (World, Entity, System)
├── components/         # Pydantic-схемы данных (Perception, Brain, Action)
├── systems/            # Логика (ActionExecution, PerceptionUpdate)
├── perception/         # Узлы пайплайна (OpenCV, OCR, CLIP, GridMapping)
├── actions/            # Классы физических и логических действий
├── brain/              # Интеграция Behavior Trees и коннекторы к LLM
├── tools/              # DearPyGui интерфейсы, авто-генерация GUI из Pydantic
└── envs/               # Обертки для Gymnasium и сбора датасетов
```
