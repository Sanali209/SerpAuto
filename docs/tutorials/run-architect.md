# Tutorial: Запуск SerpAuto в режиме Architect

## Цель

Запустить SerpAuto с графическим интерфейсом (DearPyGui) в режиме Architect для визуального редактирования ECS-мира, Behaviour Trees и пайплайнов перцепции.

## Требования

- Python 3.10+
- Установленные зависимости из `requirements.txt`
- Рабочая директория: `D:\github\SerpAuto`

## 1. Структура запуска

Точка входа — `main.py`. Используется `typer` с единственной командой `run`:

```python
# main.py: строка 16
@app.command()
def run(mode: EngineMode = EngineMode.ARCHITECT, tps: int = 60):
    engine = SerpentineEngine(mode=mode, target_tps=tps)
    asyncio.run(engine.run())
```

Параметр `mode` по умолчанию равен `EngineMode.ARCHITECT`.

## 2. Что даёт Architect mode

Класс `ArchitectMode` (`modes/architect.py`) наследует `ModeStrategy` и возвращает системы, зарегистрированные для `EngineMode.ARCHITECT`:

```python
class ArchitectMode(ModeStrategy):
    def get_systems(self, phase: SystemPhase) -> List[Type[Any]]:
        return Registry.get_systems_for_phase(phase, self.mode)
```

В Architect mode активны все системы с флагом `ARCHITECT` в декораторе `@Registry.register_system(...)`:

- **INPUT**: `HumanInputSystem`, `SensoryInputSystem`, `PossessionSystem`
- **MAIL_ROUTING**: `MessageRouterSystem`
- **PERCEPTION**: `PerceptionPipelineSystem`
- **INTERNAL_PHYSICS**: `SnakeActionSystem`, `SnakeLocomotionSystem`, `SnakeCollisionSystem`
- **COGNITION**: (не активен в ARCHITECT — BT не исполняется)
- **EXECUTION**: `ActionExecutionSystem`
- **REWARD**: (не активен)
- **TELEMETRY**: `GUIDebugSystem`, `RenderSystem`

## 3. Список GUI окон

`GUIDebugSystem` (`systems/gui/system.py`) запускает DearPyGui со следующими окнами:

- **Outliner** — список всех сущностей и компонентов
- **Inspector** — редактор свойств выбранной сущности
- **Viewport** — 3D/2D рендер (ModernGL)
- **GlobalSwarmRoster** — список агентов роя
- **ActionTimelineWindow** — история экшенов
- **ControlDeck** — кнопки Play/Pause/Step, TPS-слайдер
- **ImitationLearningMonitor** — мониторинг имитационного обучения

Дополнительно: `BehaviorTreeEditor` и `PerceptionGraphEditor` — визуальные редакторы графов.

## 4. Запуск

```bash
cd D:/github/SerpAuto
python main.py run
```

Эквивалентно:

```bash
python main.py run --mode ARCHITECT --tps 60
```

## 5. Ожидаемый результат

После старта в терминале отобразится таблица с фазами и системами. Откроется окно DearPyGui. Через **ControlDeck** можно управлять движком: Play/Pause/Step, перетаскивать TPS-слайдер.

## 6. Управление

| Действие | Результат |
|----------|-----------|
| Кнопка Play | Запускает tick-цикл |
| Кнопка Pause | Останавливает tick-цикл (TELEMETRY и INPUT продолжают работать) |
| Кнопка Step | Выполняет один tick |
| TPS слайдер | Меняет target_tps (1–240) |
| Клик на сущность в Outliner | Открывает её в Inspector |
| Клик в Viewport | Raycast + выбор/посессия сущности |

## 7. Код, отвечающий за паузу

```python
# engine.py: строка 164
if self.paused and not self._step_requested:
    if phase not in [SystemPhase.TELEMETRY, SystemPhase.INPUT]:
        continue
```

Это гарантирует, что GUI и ввод работают даже на паузе.
