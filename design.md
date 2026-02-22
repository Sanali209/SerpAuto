# Дизайн-документ: Когнитивный гибридный движок "Serpentine" (v2.0)

## 1. Концепция и Архитектурная философия

Serpentine — это асинхронный, Tick-based движок на базе паттерна Entity-Component-System (ECS). Он спроектирован для создания как одиночных автономных агентов, так и многоагентных роев (Swarms), способных бесшовно оперировать во внешних средах (ОС, Web-браузеры, сторонние игры) и во внутренних симуляциях.

**Главная парадигма:** Полное разделение Данных, Логики и Интерфейсов. Движок работает как единая магистраль, где жесткие скрипты (Behavior Trees) и вероятностные модели (LLM/CV) комбинируются через стандартизированные интерфейсы.

## 2. Ядро Движка (Core ECS & Loop)

### 2.1. Реестр Состояния (World)
Весь стейт системы хранится в объекте `World`. Сущности (Entity) — это UUID-идентификаторы. Вся информация хранится в Компонентах. Поиск осуществляется через сверхбыстрое пересечение множеств (Query Caching), что позволяет обрабатывать тысячи сущностей за миллисекунды.

### 2.2. Базовые Компоненты (Data Models)
Компоненты строго типизированы через Pydantic BaseModel. Это обеспечивает встроенную валидацию и фундамент для авто-генерации GUI.

#### A. Когнитивные Компоненты
*   `PerceptionComponent`: Снимок среды на текущий тик (JSON с парсингом DOM или CV-объектами).
*   `MemoryComponent` (Blackboard): Рабочая память агента (Key-Value) и история (лог для LLM).
*   `ActionBufferComponent`: Очередь FIFO (List[BaseAction]) для команд на исполнение.
*   `BrainComponent`: Статус (IDLE, RUNNING, WAITING) и контекст.
*   `RewardComponent` (RL): Награда за текущий шаг (для Gymnasium Mode).

#### B. Коммуникационные Компоненты (Рой)
*   `AgentMetaComponent`: Имя, роль, статус.
*   `MailboxComponent`: Буфер Pub/Sub (inbox, outbox, subscriptions).

#### C. Пространственные/Внутренние Компоненты
*   `TransformComponent`: Позиция (x, y, w, h, layer).
*   `VelocityComponent`: Вектор скорости (vx, vy).
*   `ColliderComponent`: Геометрия для физики (Box/Circle).
*   `SpriteComponent`: Текстура для внутреннего рендера.

### 2.3. Главный Асинхронный Цикл (The Engine Tick Loop)
Движок не блокируется тяжелыми вычислениями. Целевой Tick Rate — 20-60 TPS (в Headless/Gym режиме — безлимитно).

**Порядок выполнения Систем (Phases):**
1.  **Mail Routing Phase**: `MessageRouterSystem` разносит письма из outbox в inbox адресатов.
2.  **Perception Phase**: Сбор сырых данных (`SensoryInputSystem`) и прогон через направленный граф фильтров (`PerceptionPipelineSystem`). Обновление `PerceptionComponent`.
3.  **Internal Physics Phase** (Опционально): `InternalPhysicsSystem` двигает внутренние сущности, обсчитывает коллизии.
4.  **Cognition Phase**: `AI_BrainSystem` опрашивает Behavior Trees каждого агента. Если нужен ответ сети (LLM/API), создается асинхронная Task, а агент переходит в статус WAITING.
5.  **Execution Phase**: `ActionExecutionSystem` маршрутизирует команды из буфера (клик мышью в ОС или вызов `on_click` внутри памяти).
6.  **Telemetry Phase**: Обновление GUI (`GUIDebugSystem`), запись датасетов (`DatasetLoggerSystem`).

## 3. Восприятие и Компьютерное Зрение (Perception Pipeline)

Конвейер обработки входящих данных, построенный на архитектуре DAG (Directed Acyclic Graph).

*   **Узлы (Nodes)**: Каждый фильтр имеет Pydantic-конфиг (авто-биндинг в GUI) и метод `process(context)`.
*   **Базовые фильтры**:
    *   `DOMParserNode`: Извлечение XPath/CSS селекторов.
    *   `OpenCVNodes`: Crop, Grayscale, Threshold, MatchTemplate.
    *   `YOLONode` (ONNX Runtime): Использование скомпилированных моделей Ultralytics YOLOv8/v11 для мгновенного поиска объектов (bounding boxes) без тяжеловесного PyTorch.
    *   `OCRNode`: Извлечение текста с кропов (Docling/Tesseract).
    *   `GridMapperNode`: Трансформация пикселей в изометрическую/2D сетку `passability_grid`.

## 4. Гибридный Мозг (Cognition Core)

Сочетает детерминированную надежность и адаптивность ML.

### 4.1. Behavior Tree (BT)
Дерево поведения — основа логики. Узлы общаются через Blackboard агента.

*   **Control Nodes**: `Selector` (поиск первого успешного), `Sequence` (строгий порядок).
*   **Decorator Nodes**: Инверторы, таймеры (`WaitNode`).
*   **MAS Nodes**: `SendMessageNode` (отправка в Pub/Sub), `ListenForEventNode` (ожидание в inbox).

### 4.2. Адаптеры Моделей (AI Bridge)
Behavior Tree не знает, какая модель подключена. Узел `LLM_Inference` использует адаптеры. `ContextBuilder` сжимает `PerceptionComponent` и Blackboard в текстовый JSON-промпт.

*   `OpenAILikeAdapter`: Для больших моделей (GPT-4/Gemini) с историей чата и Function Calling.
*   `MicroserviceAdapter`: Для быстрых HTTP-вызовов к легковесным моделям (Koyeb/Hugging Face).
*   `N8NWebhookAdapter`: Передача стейта агента во внешний воркфлоу n8n.

## 5. Многоагентная Система (MAS & Pub/Sub)

Агенты строго изолированы и не имеют прямого доступа к памяти друг друга.

*   **Event Bus**: Общение происходит через `MessageRouterSystem`.
*   **Топики (Topics)**: Агент-разведчик публикует `{"topic": "target_found", "payload": {...}}`. Агент-боец или Агент-скрапер, у которого в `MailboxComponent.subscriptions` есть `target_found`, получает это письмо в свой inbox на следующем тике.
*   **Преимущества**: Предотвращение Race Conditions, легкое масштабирование роя, возможность перезапускать зависших агентов без обрушения всей системы.

## 6. Исполнение Действий (Action Routing)

Система паттерна Command. Любое действие — это объект (например, `ClickAction`, `SendAPIAction`).

**Маршрутизация среды (target_env):**
Каждый экшен имеет флаг цели:
*   `EXTERNAL_OS`: Выполняется через драйверы ОС (Playwright, PyAutoGUI). Агент взаимодействует с реальным браузером, игрой или заводским софтом.
*   `INTERNAL_ENGINE`: Выполняется через прямое изменение компонентов другой сущности в World. Агент играет во "внутреннюю" игру или взаимодействует с другим внутренним агентом.

## 7. Инструментарий и GUI (DearPyGui)

Графический интерфейс — это не часть логики, а подключаемая система (`GUIDebugSystem`), работающая в реальном времени.

### 7.1. Авто-Интерфейс (Pydantic ➡️ DPG)
Движок автоматически сканирует Pydantic-схемы конфигураций узлов и фильтров, генерируя ползунки, чекбоксы и выпадающие списки (Zero-code GUI для новых модулей).

### 7.2. "God Mode" Dashboard (Рабочее пространство)
*   **Global Roster**: Таблица активных агентов роя с их текущим статусом, CPU-нагрузкой и задачей.
*   **Contextual Inspector**: Выбор агента обновляет все панели (Дерево, Память, Буфер) только для него.
*   **Live BT Tracer**: Графическое отображение Behavior Tree с пульсирующими узлами (зеленый/красный/желтый) для отладки логики в реальном времени.
*   **Buffer Editor**: Возможность вручную удалить ошибочный экшен из `ActionBufferComponent` или изменить переменную в Blackboard "на горячую".
*   **Perception View**: Мультиоконный или сеточный (CCTV) рендер экранов/пайплайнов с нулевым копированием (Zero-copy GPU рендер через DPG Texture Registry). Возможность переключать промежуточные слои CV (например, видеть только слой Canny Edges или Bounding Boxes YOLO).
*   **Message Broker Sniffer**: Лог Pub/Sub трафика между агентами с подсветкой Dead Letter (недоставленных) сообщений.

## 8. MLOps и Режимы Работы

Движок поддерживает мгновенное переключение режимов для обучения нейросетей.

*   **Production (Headless)**: Запуск в Docker (например, на Koyeb). Максимальный TPS, UI отключен.
*   **Teacher Mode (Сбор датасетов)**:
    *   BT агента ставится на паузу.
    *   Оператор управляет средой (через перехват мыши в GUI).
    *   `DatasetLoggerSystem` каждый тик сохраняет пару `[Perception_JSON, User_Action]` в HDF5/JSONL.
    *   Интеграция с экспорт-пайплайном Label Studio -> Ultralytics -> ONNX.
*   **Gymnasium Mode (Спортзал RL)**:
    *   Движок оборачивается в стандартный интерфейс OpenAI Gym (`reset()`, `step(action)`).
    *   Таймауты `asyncio.sleep` отключаются для турбо-скорости (Fast-Forward).
    *   Оценка действий происходит через добавленный `RewardComponent`.
