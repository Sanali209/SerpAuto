# Explanation: 4-слойная архитектура и фазы тика

## Общая картина

SerpAuto построена на **4-слойной архитектуре**, вдохновлённой когнитивной моделью "Perception → Cognition → Action" и дополненной слоем Core для управления движком и слоем Swarm для роевого взаимодействия.

```
┌──────────────────────────────────────────────────┐
│                   SWARM                           │
│  Меж-агентная коммутация, рой, broadcast         │
├──────────────────────────────────────────────────┤
│                   MIND (Cognition)                │
│  Behaviour Trees, LLM, Intents, Blackboard        │
├──────────────────────────────────────────────────┤
│                   BODY (Perception)               │
│  Сенсоры (mss), CV-пайплайн, Action Execution     │
├──────────────────────────────────────────────────┤
│                   CORE                            │
│  ECS (World/Entity/Component), Engine, Registry   │
│  Scene Manager, EventBus, Gym-обёртка             │
└──────────────────────────────────────────────────┘
```

---

## Core — Базовый слой

Файлы: `serpentine/core/`, `serpentine/components/`, `serpentine/systems/`

### ECS (Entity-Component-System)

- **Entity** — UUID (тип `EntityID`). Простая идентификация, без данных.
- **Component** — Pydantic-модель (`BaseComponent`). Только данные, без логики. 18+ зарегистрированных компонентов.
- **System** — асинхронный класс (`System.update(world, dt)`). Только логика, без состояния.

Хранилище — `World`:
- `_entities: Set[EntityID]` — множество сущностей
- `_components: Dict[Type, Dict[EntityID, Component]]` — компоненты по типу
- `_query_cache: Dict[Tuple, Set[EntityID]]` — кеш запросов

### Registry

Два регистра:

1. **Registry** (`core/registry.py`) — основной. Регистрирует компоненты (`@register_component`), системы (`@register_system` с фазой/режимом/приоритетом/tick-rate), узлы BT (`@register_node`).
2. **RegistryV2** (`core/registry_v2.py`) — альтернативный с категориями для GUI-окон и систем.

### SerpentineEngine

Главный цикл движка. Создаёт `World`, инициализирует системы через `ModeStrategy`, выполняет `_tick()` в бесконечном цикле с фиксацией TPS.

### Scene Manager

`SceneManager` + `SceneLoader` + `SceneSaver` + `SceneValidator` — полный цикл сериализации/десериализации мира в JSON.

### EventBus

Простой Pub/Sub. `GUIEventBus` — алиас. Используется для управления движком из GUI (Play/Pause/Step).

### SerpentineGymEnv

gym.Env-совместимая обёртка. Создаёт змейку, принимает Discrete(4) action, возвращает grid-наблюдение.

---

## Body — Слой восприятия и исполнения

Файлы: `serpentine/perception/`

### Сенсорный ввод (INPUT)

- **SensoryInputSystem** — захват экрана через `mss`. Кладёт `Observation(data_type="image")` в `PerceptionComponent` каждой сущности.

- **InternalStateReaderSystem** — для Gymnasium-режима. Читает внутреннее состояние симуляции (snake_state).

- **HumanInputSystem** — клавиатурный ввод через DearPyGui (WASD/стрелки). Преобразует в `KeyIntent`.

### Perception Pipeline (PERCEPTION)

**PerceptionPipelineSystem** — исполняет цепочку `PerceptionNode` для каждой сущности с `PerceptionComponent`.

Доступные узлы (`perception/nodes.py`):

| Узел | Функция |
|------|---------|
| `PerceptionNode` (ABC) | Базовый класс |
| `CVNode` | Базовый для CV-узлов (валидация numpy-изображения) |
| `CropNode` | Обрезка изображения по ROI |
| `GrayscaleNode` | Конвертация в оттенки серого (OpenCV) |
| `TemplateMatchNode` | Поиск шаблона на изображении |
| `OCRNode` | Распознавание текста (Tesseract) |
| `DOMParserNode` | Парсинг DOM (заглушка) |
| `GridMapperNode` | Конвертация сенсорных данных в grid |
| `InternalGridPerception` | Конвертация snake_state в grid-карту (0=пусто, 1=голова, 2=тело, 3=еда) |

### Исполнение действий (EXECUTION)

**ActionExecutionSystem** — читает `ActionBufferComponent.action_queue`, исполняет Intents через PyAutoGUI:
- `ClickIntent` → `pyautogui.click()`
- `MoveIntent` → `pyautogui.moveTo()`
- `KeyIntent` → `pyautogui.press()/keyDown()/keyUp()`

### PossessionSystem

Позволяет захватывать управление над сущностью через клик в Viewport с raycasting (AABB/sphere intersection).

---

## Mind — Когнитивный слой

Файлы: `serpentine/mind/`

### Behaviour Trees

Корень дерева хранится в `BrainComponent`. `AI_BrainSystem` (фаза `COGNITION`) вызывает `root.tick()` для каждой сущности.

Узлы разделены на категории:
- **Composites**: `Sequence`, `Selector`, `Parallel`
- **Decorators**: `Inverter`, `Succeeder`, `RepeatUntilFail`
- **Actions**: `ChangeDirectionNode`, `WaitNode`, `ClickNode`, `MoveNode`, `KeyNode`, `SetBlackboardVariable`
- **Cognition**: `LLMInferenceNode` (асинхронный запрос к LLM через `AIAdapter`)
- **Swarm**: `SendMessageNode`, `ListenForEventNode`

### Intents

Action-узлы создают интенты (`ClickIntent`, `MoveIntent`, `KeyIntent`, `ChangeDirectionIntent`) и кладут их в `ActionBufferComponent`.

Blackboard — общая память дерева. LLM-узел читает из blackboard контекст и пишет ответ обратно.

---

## Swarm — Роевой слой

Файлы: `serpentine/core/messages.py`, `serpentine/components/swarm.py`, `serpentine/systems/swarm.py`, `serpentine/mind/swarm_nodes.py`

### Компоненты

- **AgentMetaComponent** — роль (`"worker"`), статус (`"idle"`), имя
- **MailboxComponent** — `inbox` + `outbox` со списками `SwarmMessage`

### MessageRouterSystem (MAIL_ROUTING)

Раз в tick обрабатывает все `outbox`-ы:
- **Point-to-point**: `recipient_id` задан → кладёт в inbox получателя
- **Broadcast**: `recipient_id = None` → кладёт всем, кроме отправителя
- **TTL**: сообщения старше `ttl` секунд дропаются

### Swarm-узлы BT

- `SendMessageNode` — создаёт `SwarmMessage`, кладёт в `outbox`
- `ListenForEventNode` — ищет в `inbox` сообщение по топику, потребляет его

---

## 8 фаз tick-цикла

Порядок определён в `SystemPhase` и жёстко зафиксирован в `_tick()`:

```
 1. INPUT          ─── Сбор сенсорных данных и ввод
 2. MAIL_ROUTING   ─── Маршрутизация сообщений роя
 3. PERCEPTION     ─── Обработка сенсорных данных (CV-пайплайн)
 4. INTERNAL_PHYSICS ─ Физика симуляции (движение, коллизии)
 5. COGNITION      ─── Исполнение Behaviour Trees
 6. EXECUTION      ─── Исполнение действий (PyAutoGUI)
 7. REWARD         ─── Расчёт наград (RL)
 8. TELEMETRY      ─── GUI, рендер, логирование
```

### Логика паузы

```python
# engine.py: строка 164
if self.paused and not self._step_requested:
    if phase not in [SystemPhase.TELEMETRY, SystemPhase.INPUT]:
        continue
```

На паузе продолжают работать только INPUT и TELEMETRY — GUI остаётся отзывчивым, а ввод не теряется.

### Tick-rate системы

Каждая система может иметь свой TPS (`tick_rate`). Движок аккумулирует dt и вызывает `update()` с фиксированным шагом:

```python
while system._accumulator >= target_dt:
    await system.update(self.world, target_dt)
    system._accumulator -= target_dt
```

---

## Режимы (Modes)

Четыре режима через **Strategy Pattern** (`modes/base.py` → `ModeStrategy(ABC)`):

| Режим | Класс | Характеристика |
|-------|-------|----------------|
| `ARCHITECT` | `ArchitectMode` | Полный GUI, все системы, BT не исполняется |
| `PRODUCTION` | `ProductionMode` | Headless, BT исполняется, GUI выключен |
| `TEACHER` | `TeacherMode` | Демонстрация + запись датасета |
| `GYMNASIUM` | `GymnasiumMode` | RL-тренировка, серые системы, reward |

---

## Data Flow (полный цикл обработки)

```
Screen (mss)
    │
    ▼
SensoryInputSystem (INPUT) ──── PerceptionComponent.observations["raw_screen"]
    │
    ▼
PerceptionPipelineSystem (PERCEPTION)
    │  CropNode → GrayscaleNode → ...
    ▼
PerceptionComponent.observations["center_crop"]
    │
    ▼
AI_BrainSystem (COGNITION)
    │  BrainComponent.root.tick(world, entity, blackboard)
    ▼
ActionBufferComponent.action_queue [Intent, Intent, ...]
    │
    ▼
ActionExecutionSystem (EXECUTION)
    │  PyAutoGUI.click(x, y)
    ▼
Физическое действие на экране
```

Для внутренней симуляции (Snake):

```
SnakeStateReaderSystem (INPUT)
    │  snake_state → PerceptionComponent
    ▼
SnakeActionSystem (INTERNAL_PHYSICS)  ← HumanInputSystem / BT / LLM
    │  ChangeDirectionIntent → next_direction
    ▼
SnakeLocomotionSystem (INTERNAL_PHYSICS)
    │  segments.insert(0, new_head); segments.pop()
    ▼
SnakeCollisionSystem (INTERNAL_PHYSICS)
    │  wall/self/food → is_alive, reward, food respawn
    ▼
EnvironmentJudgeSystem (REWARD)
    │  reward → cumulative_reward
    ▼
DatasetLoggerSystem (TELEMETRY)
    │  state-action → JSONL
```

---

## Связь с des_docs/

Для глубокого изучения каждой подсистемы см. `des_docs/`:

- `des_docs/architecture/` — диаграммы слоёв и потоки данных
- `des_docs/api_ml/` — ML-интеграция и Gymnasium
- `des_docs/guides/` — практические руководства
- `des_docs/modes/` — детали каждого режима
- `des_docs/reports/` — отчёты о тестировании и нагрузке

Полный глоссарий: `des_docs/GLOSSARY.md`
