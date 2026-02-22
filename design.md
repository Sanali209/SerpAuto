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

### 5.1. Узел вызова модели (LLM/CLIP)

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

### 5.2. Система Адаптеров для ИИ (AI Model Adapters)

Чтобы движок мог бесшовно переключаться между разными моделями (локальные, облачные, вебхуки), используется **паттерн Adapter**. Адаптер — это сервисный класс, а не компонент состояния. `BehaviorTree` не знает о конкретной реализации модели, оно лишь ожидает список действий.

#### 5.2.1. Единый Интерфейс (Base Adapter)

Все адаптеры наследуются от базового класса и реализуют асинхронный метод генерации ответа.

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pydantic import BaseModel

class AIResponse(BaseModel):
    raw_text: str
    parsed_actions: List[Dict[str, Any]] # Например: [{"action": "click", "x": 10, "y": 20}]
    metadata: Dict[str, Any] # Токены, время ответа (для дебага в GUI)

class BaseAIAdapter(ABC):
    @abstractmethod
    async def generate_response(self, system_prompt: str, context_data: dict) -> AIResponse:
        """Главный метод, который вызывает Behavior Tree"""
        pass
```

#### 5.2.2. Подготовка данных (Context Builder)

Перед вызовом адаптера, `ContextBuilder` преобразует `PerceptionComponent` (сырые данные) в компактный промпт или JSON для LLM.

*   **Сырые данные**: `{"hp": 45, "enemies": [{"type": "orc", "dist": 5}]}`
*   **Сжатый промпт**: "Текущее ХП: 45. Враги рядом: orc (дистанция 5). Выбери действие: attack, heal, flee."

#### 5.2.3. Реализация Адаптеров

**Тип А: Сложные LLM (OpenAI, Anthropic, Gemini)**
Используют историю чата и Structured Output (JSON Mode).

```python
import httpx

class OpenAILikeAdapter(BaseAIAdapter):
    def __init__(self, api_key: str, model_name: str, base_url: str):
        # ... инициализация ...
        pass

    async def generate_response(self, system_prompt: str, context_data: dict) -> AIResponse:
        # Формирование payload с историей сообщений
        # Запрос к API с response_format={"type": "json_object"}
        # Парсинга JSON из ответа
        pass
```

**Тип Б: Простые / Локальные Модели (Hugging Face / Koyeb)**
Архитектура Request-Response для конкретных задач (OCR, классификация) без истории чата.

```python
class SimpleMicroserviceAdapter(BaseAIAdapter):
    def __init__(self, endpoint_url: str):
        self.endpoint = endpoint_url

    async def generate_response(self, system_prompt: str, context_data: dict) -> AIResponse:
        # Отправка фичей (context_data) на эндпоинт
        # Конвертация ответа (например, класса и уверенности) в Action
        pass
```

**Тип В: Автоматизации (n8n Webhook)**
Для сложной логики с внешними интеграциями (БД, почта).

```python
class N8NWebhookAdapter(BaseAIAdapter):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    async def generate_response(self, system_prompt: str, context_data: dict) -> AIResponse:
        # Отправка всего стейта агента на вебхук n8n
        # Ожидание результата выполнения воркфлоу в формате Action
        pass
```

#### 5.2.4. Парсер Экшенов (Guardrails)

Узел `BehaviorTree` получает `AIResponse` и конвертирует список `parsed_actions` (JSON) в физические объекты `BaseAction`. Если модель вернула некорректный JSON или опасное действие, парсер выбрасывает ошибку, и узел возвращает статус `FAILURE`, активируя запасную ветку поведения.

#### 5.2.5. AI Network Monitor (GUI)

В режиме Debug / Architect доступно окно мониторинга сети ИИ:

*   **Connection Setup**: Pydantic-настройки для горячего переключения адаптера (OpenAI ↔ Koyeb ↔ n8n).
*   **Prompt Inspector**: Просмотр финального промпта перед отправкой.
*   **Trace Log**: Лог запросов и ответов (latency, parsed actions).
*   **Cost / Latency Tracker**: Графики времени ответа и расхода токенов.

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

## 7. Когнитивный Дебаггер (GUI)

Интерфейс Serpentine физически отделен от логики и является системой (`GUIDebugSystem`), отрисовывающей состояние `World` с помощью **DearPyGui (DPG)**. Это Immediate Mode GUI, позволяющий рендерить интерфейс на GPU без замедления работы движка.

Этот функционал уровня AAA-движков превращает систему в прозрачную лабораторию, используя встроенные механизмы Node Editor и Texture Registry.

### 7.1. Компоновка Рабочего Пространства (Workspace Layout)

Интерфейс использует систему док-станций (Docking) и разбит на 5 зон:

1.  **🎮 Верхняя панель: Control Deck (Управление Временем)**
    *   **Транспорт**: `[▶ Play]`, `[⏸ Pause]`, `[⏭ Step]`. Кнопка **Step** заставляет движок сделать ровно 1 тик, что критически важно для дебага.
    *   **Режимы (Mode Switcher)**: Выпадающий список (Debug / Architect, Teacher, Gym Monitor).
    *   **Tick Rate Slider**: Ползунок скорости цикла (от 1 TPS до MAX).

2.  **🌳 Левая панель: World Outliner & Component Inspector**
    *   **Outliner**: Древовидный список всех активных сущностей (Entities).
    *   **Inspector**: Отображает компоненты выбранной сущности. Значения обновляются в реальном времени.

3.  **👁️ Центральное окно: Perception View (Глазами Агента)**
    *   **Visual Mode**: Стрим кадров (игра, браузер).
    *   **Overlays**: Чекбоксы слоев дебага (Bounding Boxes, Passability Grid, Gaze/Clicks).
    *   **Интерактивность**: В режиме **Teacher** клики по этому окну транслируются в игровые координаты для записи датасета.

4.  **🧠 Нижняя панель: Behavior Tree & Action Log**
    *   **BT Visualizer**: Граф поведения. Узлы подсвечиваются (🟩 Success, 🟥 Failure, 🟨 Running). Пульсирующий желтый узел означает ожидание ответа от LLM/ML.
    *   **Console / Action Log**: Бегущая строка событий (тики, действия, ответы LLM).

5.  **⚙️ Правая панель: Perception Pipeline (Редактор Фильтров)**
    *   **Node Editor**: Визуальный редактор графа (Screen Capture ➡️ Grayscale ➡️ OCR).
    *   **Preview Node**: Мини-экран у каждого узла для просмотра промежуточных результатов.

### 7.2. Продвинутая Отладка (AAA-Level Features)

#### 7.2.1. Редактор Behavior Tree (Live Brain Editor)
Интерфейс представляет граф поведения агента в виде визуального нодового редактора с возможностями **Live Tracing** и **Hot-Swapping**:

*   **Live Tracing**: В реальном времени видно, как сигнал проходит по узлам. Активный узел пульсирует желтым (`RUNNING`), успешные вспыхивают зеленым (`SUCCESS`), неудачные — красным (`FAILURE`).
*   **Hot-Swapping**: Можно поставить движок на паузу, изменить параметры узла (например, таймаут) или перестроить связи (разорвать провод и подключить к другой ветке). После снятия с паузы агент продолжит выполнение с новой логикой.

#### 7.2.2. Инспекция и редактирование Буфера Данных (God Mode)
Полный контроль над памятью и намерениями агента через **Entity Inspector**:

*   **Просмотр Очереди Действий (Action Queue)**: Список карточек с текущими и ожидающими действиями (например, `[RUNNING] ⏳ MoveToAction`, `[PENDING] 🕒 ClickAction`).
*   **Удаление (Cancel)**: Возможность удалить любое запланированное действие (например, галлюцинацию LLM) до его выполнения.
*   **Инъекция (Inject)**: Возможность вручную добавить действие в очередь через командную строку или меню (например, заставить агента нажать клавишу).
*   **Редактирование State/Memory**: Возможность прямого редактирования значений в памяти агента (например, изменить здоровье врага в `PerceptionComponent`), на что скрипты отреагируют немедленно.

#### 7.2.3. Визуальные буферы и X-Ray Vision
Система позволяет видеть каждую стадию обработки изображения в пайплайне компьютерного зрения, используя **Texture Registry** в DPG.

*   **Routing (Переключение буферов)**: Клик по любой ноде в редакторе пайплайна (например, `Canny Edges`) мгновенно переключает текстуру в главном окне **Perception View**, показывая результат работы именно этого фильтра.
*   **Tab-view**: Вкладки над главным окном позволяют переключаться между финальным состоянием и промежуточными буферами.
*   **Живой дебаг**: Возможность накладывать слои (Overlays) из разных буферов друг на друга (например, сырой кадр + Bounding Boxes из нейросети).
*   **Производительность**: Используется **zero-copy** передача NumPy массивов из OpenCV напрямую в текстуры DPG, обеспечивая 60 FPS без торможения логики бота.

### 7.3. Магия Авто-Интерфейса (Pydantic ➡️ DearPyGui)

Движок автоматически генерирует GUI для настроек фильтров, используя рефлексию Python и Pydantic.

**Пример:**

```python
class ColorFilterConfig(BaseModel):
    is_enabled: bool = True
    threshold: int = Field(default=128, ge=0, le=255, description="Уровень отсечения")
    mode: Literal["RGB", "HSV"] = "HSV"
```

**Результат в GUI:**
*   `bool` ➡️ `dpg.add_checkbox(label="is_enabled")`
*   `int` (с ограничениями) ➡️ `dpg.add_slider_int(label="threshold", min_value=0, max_value=255)`
*   `Literal` ➡️ `dpg.add_combo(items=["RGB", "HSV"])`

Изменение ползунка в UI напрямую мутирует поле в объекте `config` узла, мгновенно влияя на обработку следующего кадра.

### 7.4. Режим "Teacher" (Обучение с учителем)

*   **Активация**: Кнопка `[⏺ RECORD DATASET]`.
*   **Логика**: `Behavior Tree` отключается, управление передается `HumanInputSystem`.
*   **Сбор данных**:
    1.  Оператор кликает в окне **Perception View**.
    2.  `HumanInputSystem` создает `Action` (например, `ClickAction`).
    3.  `DatasetLoggerSystem` записывает пару `{PerceptionComponent (JSON), Action}` в файл датасета.
    4.  Счетчик записанных сэмплов обновляется в реальном времени.

### 7.5. Визуализация Data Extraction Pipeline (Web Parsing)

Если агент работает с DOM-деревом:
*   В **Perception View** отображается дерево объектов (как Chrome DevTools).
*   Узлы в редакторе становятся экстракторами (DOM Source ➡️ XPath Finder ➡️ LLM Context).
*   При изменении XPath в ползунке ноды, соответствующие элементы на странице мгновенно подсвечиваются.

## 8. Внутренние Миры и Симуляция (Hybrid Environment)

Архитектура позволяет бесшовно совмещать работу с внешними приложениями (автоматизация) и внутренними симуляциями (NPC, игры, обучение), не меняя ядро ECS.

### 8.1. Абстракция Среды (Environment Routing)

Разделение на уровне источников данных и исполнителей действий.

*   **Внешняя среда (External)**: Данные из `ScreenCaptureNode` или `DOMParserNode`. Действия через Playwright или эмуляцию ОС.
*   **Внутренняя среда (Internal)**: Среда и сущности (NPC, объекты) живут прямо в оперативной памяти движка.

### 8.2. Прямое Восприятие (Direct Perception Bypass)

Для внутренних сущностей не нужно зрение (CV). Используется специальный узел `InternalStateReaderNode`, который читает `World` напрямую.

*   **Вход**: Запрос (например, "все враги в радиусе 100").
*   **Выход**: Стандартный JSON для `PerceptionComponent`.
*   **Преимущество**: `BehaviorTree` и LLM получают идентичную структуру данных, не зная, откуда она пришла (из OpenCV или из памяти).

### 8.3. Маршрутизация Действий

Система исполнения действий проверяет контекст цели в `BaseAction`.

```python
class ClickAction(BaseAction):
    x: float
    y: float
    target_env: Literal["EXTERNAL_OS", "INTERNAL_ENGINE"] = "EXTERNAL_OS"
```

**Логика ActionExecutionSystem:**
*   Если `EXTERNAL_OS` ➡️ Вызов системной мыши (pyautogui).
*   Если `INTERNAL_ENGINE` ➡️ Поиск сущности по координатам и вызов `on_click()`.

### 8.4. Внутренние Системы

Для реализации внутренней "игры" добавляются системы, работающие параллельно с логикой агента:
*   `InternalPhysicsSystem`: Обсчитывает движение и коллизии внутренних сущностей.
*   `InternalRenderSystem`: Отрисовывает внутренние сущности (спрайты) в отдельном окне DPG.

### 8.5. Мульти-Агентность и RL (Идеальный Спортзал)

В одном цикле могут сосуществовать разные агенты:
1.  **Парсер (Агент А)**: Следит за браузером.
2.  **Трейдер (Агент Б)**: Принимает решения на основе данных Парсера.
3.  **NPC (Агент В)**: Живет во внутренней симуляции.

**Польза для RL:** Возможность обучать агента во внутренней среде в Headless-режиме (1000+ TPS), а затем переключать его на внешнюю среду (реальное приложение) без переобучения мозга, просто сменив источник Perception и `target_env` действий.

## 9. Директории проекта

```
serpentine_engine/
├── core/               # Базовые классы (World, Entity, System)
├── components/         # Pydantic-схемы данных (Perception, Brain, Action)
├── systems/            # Логика (ActionExecution, PerceptionUpdate, InternalPhysics)
├── perception/         # Узлы пайплайна (OpenCV, OCR, CLIP, InternalStateReader)
├── actions/            # Классы физических и логических действий
├── brain/              # Интеграция Behavior Trees и коннекторы к LLM
├── tools/              # DearPyGui интерфейсы, авто-генерация GUI из Pydantic
└── envs/               # Обертки для Gymnasium и сбора датасетов
```
