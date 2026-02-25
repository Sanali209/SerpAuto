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
*   `HierarchyComponent`: Определяет родство (parent/children) для Data-Driven Hierarchy.
*   `VelocityComponent`: Вектор скорости (vx, vy).
*   `ColliderComponent`: Геометрия для физики (Box/Circle).
*   `SpriteComponent`: Текстура для внутреннего рендера.
*   **Подробнее о Иерархии**: См. [Реализация иерархии в ECS](ecs_hierarchy_impl.md) и [Управление иерархией в GUI](ecs_hierarchy_gui.md).

### 2.3. Главный Асинхронный Цикл (The Engine Tick Loop)
Движок не блокируется тяжелыми вычислениями. Целевой Tick Rate — 20-60 TPS (в Headless/Gym режиме — безлимитно).

**Порядок выполнения Систем (Phases):**
1.  **Input Phase**: `HumanInputSystem` захватывает ввод пользователя (Phase.INPUT).
2.  **Mail Routing Phase**: `MessageRouterSystem` разносит письма из outbox в inbox адресатов (Phase.MAIL_ROUTING).
3.  **Perception Phase**: Сбор сырых данных (`SensoryInputSystem`) и прогон через направленный граф фильтров (`PerceptionPipelineSystem`). Обновление `PerceptionComponent` (Phase.PERCEPTION).
4.  **Internal Physics Phase**: `InternalPhysicsSystem` двигает внутренние сущности, обсчитывает коллизии (Phase.INTERNAL_PHYSICS).
5.  **Cognition Phase**: `AI_BrainSystem` опрашивает Behavior Trees каждого агента (Phase.COGNITION).
6.  **Execution Phase**: `ActionExecutionSystem` маршрутизирует команды из буфера (Phase.EXECUTION).
7.  **Reward Phase**: `EnvironmentJudgeSystem` начисляет награды в режиме Gymnasium (Phase.REWARD).
8.  **Telemetry Phase**: Обновление GUI (`GUIDebugSystem`), запись датасетов (`DatasetLoggerSystem`) (Phase.TELEMETRY).

### 2.4. Unified Dataflow (Consolidation Strategy)
Движок переходит на стандартизированный поток данных для обеспечения модульности:
1.  **Observations** (Наблюдения): Выход Perception Phase. Сырые данные сенсоров, упакованные в Pydantic-модели.
2.  **Intent** (Намерения): Выход Cognition Phase. Behavior Tree формирует логическую цель (например, "Двигаться к яблоку").
3.  **Commands** (Команды): Выход Execution Phase. Конвертация намерений в физические действия (Click, Move, Key).

### 2.5. Data-Driven Orchestration
Вместо жесткого перечисления систем в `main.py`, движок использует **RegistryV2**.
- Каждая система помечается `@register_system(modes=[EngineMode.ARCHITECT, ...])`.
- Оркестратор динамически собирает граф систем при запуске, что позволяет добавлять новые функции (плагины) без модификации ядра.

> [!TIP]
> **Углубленное изучение ядра**:
> *   [Реализация иерархии сущностей](ecs_hierarchy_impl.md)
> *   [Библиотека игровых компонентов](game_ecs_library.md)
> *   [Руководство по реализации систем](../guides/system_implementation_guide.md)

## 3. Восприятие и Компьютерное Зрение (Perception Pipeline)

Конвейер обработки входящих данных, построенный на архитектуре DAG (Directed Acyclic Graph).

*   **Узлы (Nodes)**: Каждый фильтр имеет Pydantic-конфиг (авто-биндинг в GUI) и метод `process(context)`. Подробнее см. [Реестр узлов восприятия](perception_nodes.md).
*   **Визуальный Редактор**: Весь конвейер настраивается через [**Perception Pipeline Editor**](perception_pipeline_editor.md).
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

> [!TIP]
> **Детали интерфейса**:
> *   [Дизайн и модули God Mode](gui_layout_design.md)
> *   [Визуализация иерархии в редакторе](ecs_hierarchy_gui.md)

**Подробнее о GUI**: См. [Дизайн раскладки и модулей GUI](gui_layout_design.md).

## 8. Режимы Работы (Operation Modes)

Архитектура ECS позволяет кардинально менять поведение движка, просто изменяя состав активных Систем и параметры цикла времени. Движок поддерживает мгновенное переключение режимов для обучения нейросетей.

### 8.1. Mode: Architect & Debug (Режим Разработчика)
Визуальное программирование и отладка. [Подробнее...](../modes/play_mode.md)
*   **Системы**: Standard + `GUIDebugSystem`.
*   **Фичи**: Hot-Reloading воркспейсов, "God Mode", Zero-Copy Rendering (OpenCV -> Texture).

### 8.2. Mode: Production / Headless (Боевой серверный режим)
Фоновая работа без GUI. Идеально для Docker/Koyeb.
*   **Системы**: Standard + `TelemetrySystem`. `GUIDebugSystem` отключена.
*   **Фичи**: REST API (FastAPI) для внешнего управления, метрики (Prometheus).

### 8.3. Mode: Teacher (Сбор датасетов)
Студия захвата действий для Imitation Learning. [Подробнее...](../modes/teacher_mode.md)
*   **Системы**: `AI_BrainSystem` отключена. Включены `HumanInputSystem` и `DatasetLoggerSystem`.
*   **Фичи**: Оператор управляет агентом через GUI. Движок пишет пары `[Perception, Action]` в HDF5/JSONL.

### 8.4. Mode: Gymnasium (RL Спортзал)
Симуляция для Reinforcement Learning (PPO, DQN). [Подробнее...](../modes/gym_mode.md)
*   **Системы**: Включены `InternalPhysicsSystem` и `EnvironmentJudgeSystem` (начисление наград).
*   **Фичи**: Стандартный API `env.reset()`, `env.step()`. Векторизация 100+ агентов.

### 8.5. Mode: Continuous Learning (Actor-Learner)
Режим асинхронного онлайн-обучения в реальных I/O-средах. [Подробнее...](../modes/actor_learner.md)
*   **Системы**: Standard + `EnvironmentJudgeSystem` + `ReplayBufferSystem`.
*   **Фичи**: Отдельный процесс Learner обучает модель в реальном времени, Hot-Swapping весов ONNX.

## 9. Sample Project: Serpentine Snake AI

Этот сэмпл демонстрирует полный цикл: от создания внутренней симуляции (игры) до обучения агента (RL) и визуальной отладки. Игра живет исключительно в оперативной памяти ECS.

### 9.1. Сборка Среды (Игра)
Мы не используем внешние окна. Физика работает на компонентах:
*   `GridPositionComponent`: Координаты x, y на сетке.
*   `SnakeBodyComponent`: Очередь сегментов хвоста.
*   `VelocityComponent`: Вектор движения (dx, dy).
*   `ColliderComponent`: Тип (`head`, `body`, `apple`, `wall`).

**Игровые Системы:**
1.  `SnakeLocomotionSystem`: Двигает голову каждый тик, обновляет очередь хвоста.
2.  `SnakeCollisionSystem`: Логика игры (Съел яблоко -> Рост, Врезался -> Reset).

### 9.2. Когнитивный Интерфейс
Агент — это сущность с мозгом, подключенная к игре через стандартные интерфейсы.
*   **Perception**: `InternalGridStateNode` сканирует ECS и строит JSON-матрицу (10x10), где 0=Пусто, 1=Тело, 2=Голова, 3=Яблоко.
*   **Action**: `ChangeDirectionAction` ("UP", "DOWN"...). `ActionExecutionSystem` меняет `VelocityComponent` головы.

### 9.3. Обучение (Gymnasium Mode)
Движок переходит в режим "Спортзала" (без GUI, без sleep).
*   **Reward**: `EnvironmentJudgeSystem` начисляет +10 за яблоко, -10 за смерть, -0.1 за шаг.
*   **Результат**: RL-модель (PPO) обучается за 5 минут (1M+ шагов).

### 9.4. Визуализация (God Mode)
В режиме Architect включается `InternalRenderSystem` (DearPyGui).
*   **Game View**: Отрисовка змейки и яблока прямоугольниками.
*   **Introspection**: Рядом видна "сырая" матрица восприятия, которую видит сеть.
*   **Debug**: Можно поставить паузу, передвинуть яблоко вручную (изменив компонент), сделать шаг и проверить реакцию сети.

## 10. Управление Сценами и Реестрами (Scene & Registry Management)

Для реализации функционала, подобного игровым движкам (Unity/Unreal), где можно динамически добавлять компоненты и настраивать сцены, вводится система Реестров и Сцен.

### 10.1. Глобальные Реестры (Auto-Registration)
Чтобы UI и сериализатор знали о существовании компонентов и систем без хардкода, используются декораторы:
*   `@register_component`: Регистрирует класс данных. Позволяет UI отображать список "Add Component".
*   `@register_system(phase=...)`: Регистрирует логику и привязывает её к фазе (Physics, Perception).

### 10.2. Формат Сцены (Scene Format)
Файл `.json`, описывающий полную конфигурацию запуска (Карта + Логика):
```json
{
  "systems": ["SnakeLocomotionSystem", "SnakeCollisionSystem"],
  "entities": [ ... ],
  "settings": { "tick_rate": 10, "mode": "GYMNASIUM" }
}
```

### 10.3. Headless Loader (CLI)
Запуск движка с конкретной картой через консоль:
`python main.py --scene levels/level_01.json --mode HEADLESS`
Это позволяет тренировать агентов на разных конфигурациях мира без изменения кода.

## 11. Система Персистентности (Persistence System)

Архитектура ECS + Pydantic позволяет полностью разделить логику и данные, делая сериализацию тривиальной. Персистентность делится на три уровня:

### 9.1. Слой 1: Конфигурация Проекта (Project Blueprints)
Это статический "чертеж" агента.
*   **Что сохраняется**: Топология Perception Pipeline (граф узлов), настройки фильтров (thresholds), структура Behavior Tree.
*   **Формат**: JSON/YAML.
*   **Юзкейс**: Деплой настроенного бота на сервер (Koyeb) в Headless-режиме.

### 9.2. Слой 2: Состояние Мира (World State Snapshots)
Это динамический дамп оперативной памяти в конкретный тик.
*   **Что сохраняется**: Полный реестр `World` (Entity UUIDs + все текущие значения Компонентов).
*   **Формат**: JSON.
*   **Юзкейс**: Отладка "путешествием во времени". При ошибке делается авто-дамп. Разработчик загружает его в GUI и видит состояние мира ровно в момент бага.

### 9.3. Слой 3: Layout Интерфейса (GUI State)
Сохранение расположения окон для удобства разработчика.
*   **Что сохраняется**: Позиции, размеры и докинг окон DearPyGui.
*   **Формат**: `.ini` файл (нативный формат DPG).
*   **Юзкейс**: Персонализация рабочего пространства (монитор логов справа, граф слева).

### 9.4. Процесс Горячей Перезагрузки (Hot-Reload Workflow)
Загрузка состояния в работающий движок требует остановки времени:
1.  **Pause Engine**: `is_running = False`.
2.  **Abort Tasks**: Отмена всех асинхронных задач (LLM запросов).
3.  **Deserialize World**: Очистка памяти и восстановление сущностей из JSON.
4.  **Rebuild GUI**: Генерация новых виджетов под загруженные данные.
5.  **Resume Engine**: Запуск цикла.

---

## 12. Планирование и Ссылки

Для отслеживания прогресса и технических инсайтов используйте следующие документы:
- [x] Create [**Consolidation Strategy**](../planning/consolidation_strategy.md): Roadmap for structural refinement.
- [x] Create [**Unified Registry & Node Graph**](unified_registry_and_node_graph.md): Metadata and visual tool foundations.
*   [**Detailed Dataflow Map**](dataflow_architecture.md): Visual wiring of Observations and Commands.
*   [**Список задач (Backlog)**](../planning/tasks.md): Детальные задачи с приоритетами P0-P3.
*   [**ML Insights**](../api_ml/ml_integration_insights.md): Детали реализации Hot-Swapping и версионирования моделей.
*   [**Стандарты документации**](../dev_docs_rules.md): Правила именования и структуры файлов.
