# Дизайн-документ: Режим "Спортзал" (Gymnasium Mode / Reinforcement Learning)

## 1. Концепция и Философия Режима

Если в режиме **Teacher** агент учился, копируя действия человека (Imitation Learning), то режим **Gymnasium** предназначен для Обучения с Подкреплением (Reinforcement Learning - RL). Здесь агент учится сам, методом миллионов проб и ошибок.

Проблема классических RL-сред (например, написанных на чистом ООП) — низкая производительность. Архитектура ECS в движке **Serpentine** решает эту проблему: она позволяет запускать симуляцию с астрономической скоростью, отключая все "человеческие" интерфейсы и превращая движок в чистый математический конвейер.

Главная цель режима: **Обернуть ядро Serpentine в стандартный интерфейс `gymnasium.Env**`, чтобы его можно было "скормить" любым современным ML-библиотекам (Stable-Baselines3, Ray RLlib, CleanRL).

---

## 2. Изменения в Архитектуре ECS (Системы и Время)

Переход в Gymnasium Mode — это самое радикальное изменение профиля работы движка.

### 2.1. Управление Временем (Fast-Forward)

* В обычных режимах `SerpentineEngine` работает в реальном времени (вызывает `asyncio.sleep(1/TPS)`).
* В режиме Gym понятие "реального времени" уничтожается. Движок работает в режиме **Uncapped (безлимит)**. Цикл `while` крутится так быстро, как позволяет процессор, пережевывая десятки тысяч тиков в секунду (TPS).

### 2.2. Ротация Систем (Systems Toggle)

Мы отрезаем всё, что связывает агента с реальным внешним миром (браузеры, ОС, тяжелые нейросети).

* 🔴 **Отключены:** `SensoryInputSystem` (скриншоты не делаются), `ActionExecutionSystem` (внешняя мышь ОС не двигается), `GUIDebugSystem` (отрисовка DPG остановлена), `AI_BrainSystem` (Behavior Trees заморожены — решение теперь принимает внешняя RL-модель).
* 🟢 **Включены:** `InternalPhysicsSystem` (двигает сущности в памяти), `PerceptionPipelineSystem` (собирает матрицы из памяти).
* 🟢 **Новая Система:** **`EnvironmentJudgeSystem`** (Судья).

### 2.3. Новые Компоненты (Судейство)

Агенту добавляется компонент для учета его успехов:

```python
class RewardComponent(BaseComponent):
    current_reward: float = 0.0 # Награда за текущий шаг (сбрасывается каждый тик)
    total_score: float = 0.0    # Накопленная награда за эпизод
    is_terminated: bool = False # Агент умер / победил
    is_truncated: bool = False  # Вышло время эпизода (Time Limit)

```

---

## 3. Архитектура Обертки (The Gym Wrapper)

Чтобы RL-библиотека (например, PPO из Stable-Baselines3) могла управлять нашим движком, мы создаем класс-мост, который наследуется от стандарта `gymnasium.Env`.

Этот класс напрямую владеет объектом нашего ECS `World`.

```python
import gymnasium as gym
from gymnasium import spaces

class SerpentineGymEnv(gym.Env):
    def __init__(self, blueprint_path: str):
        super().__init__()
        # Инициализируем ECS движок в Headless/Gym режиме
        self.engine = SerpentineEngine(mode="GYMNASIUM", blueprint=blueprint_path)
        
        # Определяем "органы чувств" (Observation Space)
        # Например, матрица Змейки 10x10 со значениями от 0 до 3
        self.observation_space = spaces.Box(low=0, high=3, shape=(10, 10), dtype=int)
        
        # Определяем "мышцы" (Action Space)
        # 4 дискретных действия: UP, DOWN, LEFT, RIGHT
        self.action_space = spaces.Discrete(4)

    def reset(self, seed=None, options=None):
        # 1. Очищаем World, спавним агента и уровень заново
        self.engine.world.clear()
        self.engine.load_scene("snake_level")
        
        # 2. Делаем один "холостой" тик, чтобы PerceptionSystem собрала матрицу
        self.engine.tick() 
        
        # 3. Достаем матрицу из памяти
        agent_id = self.engine.get_main_agent()
        obs = self.engine.world.get_component(agent_id, PerceptionComponent).raw_context["grid"]
        
        return obs, {} # Возвращаем observation и пустой info-словарь

    def step(self, action: int):
        agent_id = self.engine.get_main_agent()
        
        # 1. Транслируем число из нейросети в ECS-Экшен
        action_map = {0: "UP", 1: "DOWN", 2: "LEFT", 3: "RIGHT"}
        ecs_action = ChangeDirectionAction(direction=action_map[action])
        
        # 2. Кладем экшен в буфер агента
        buffer = self.engine.world.get_component(agent_id, ActionBufferComponent)
        buffer.queue.append(ecs_action)
        
        # 3. КРУТИМ ДВИЖОК НА 1 ТИК ВПЕРЕД (Выполняется физика и коллизии)
        self.engine.tick()
        
        # 4. Читаем результаты работы Судьи (EnvironmentJudgeSystem)
        reward_comp = self.engine.world.get_component(agent_id, RewardComponent)
        obs = self.engine.world.get_component(agent_id, PerceptionComponent).raw_context["grid"]
        
        # 5. Возвращаем кортеж по стандарту Gymnasium
        return obs, reward_comp.current_reward, reward_comp.is_terminated, reward_comp.is_truncated, {}

```

---

## 4. Логика Судейства (`EnvironmentJudgeSystem`)

Эта система критически важна для RL. Нейросеть ничего не знает о правилах игры, она смотрит только на цифру `current_reward`. Судья формирует эту цифру на каждом тике.

**Пример логики Судьи для Змейки:**

1. Судья проверяет список событий (Events) от `PhysicsSystem` за прошедший тик.
2. Сбрасывает `current_reward = 0.0` у агента.
3. *Проверка штрафа за время:* Чтобы змея не крутилась на месте вечно, судья делает `current_reward -= 0.1` (Time Penalty).
4. *Проверка коллизий:*
* Если было событие `Collision(Head, Apple)`: `current_reward += 10.0`.
* Если было событие `Collision(Head, Wall)`: `current_reward -= 10.0`, и Судья ставит `is_terminated = True`.


5. На следующем вызове `step()` обертка `SerpentineGymEnv` прочитает эти флаги и отдаст их RL-алгоритму, который запустит Backpropagation.

---

## 5. Киллер-фича ECS: Массовая Векторизация (Swarm Training)

Главная причина, по которой мы пишем симуляцию на ECS, а не на ООП — это Векторизация.

Чтобы алгоритм PPO обучился быстро, ему нужен опыт. Обычно запускают 16 отдельных процессов Python с 16 копиями игры. Это жрет оперативную память и бьется о GIL (Global Interpreter Lock).

**В Serpentine ECS мы делаем иначе:**
Мы просто спавним **1000 агентов и 1000 уровней Змейки в одном реестре `World**`!

* Каждая змейка получает `SpatialGridComponent` со смещением (offset), чтобы они не пересекались (жили в своих изолированных вольерах).
* В `SerpentineGymEnv` метод `step(actions)` принимает сразу массив из 1000 действий `[0, 1, 3, 2, ...]`.
* Движок делает один массивный `self.engine.tick()`. Благодаря пересечению множеств (Query Caching) и тому, что данные в ECS лежат плотно в памяти, процессор обсчитывает физику 1000 змей за те же 2-3 миллисекунды, что и одну!
* Метод возвращает массив из 1000 `observations` и 1000 `rewards`.

Эта архитектура (`Vectorized Environment` внутри единого ECS-цикла) позволяет обучать нейросети на CPU со скоростями, сопоставимыми с GPU-симуляторами вроде Isaac Gym.

**ВАЖНО (Web ML Insight): Отказ от `gym.vector.AsyncVectorEnv`**
Стандартные практики Gymnasium для векторизации подразумевают использование `AsyncVectorEnv`, который запускает каждую среду в отдельном дочернем процессе Python. В нашем случае это убьет производительность из-за накладных расходов на сериализацию Pydantic/ECS-состояний через межпроцессное взаимодействие (IPC) и GIL. Мы **строго** используем синхронный `gymnasium.Env` (или `SyncVectorEnv`), принимающий батч из `N` действий разом, перекладывая всю тяжесть распараллеливания на низкоуровневые возможности samego **Serpentine ECS** (чтение массивов в едином пуле C-Contiguous памяти).

---

## 6. Жизненный цикл (Workflow) и возврат в Production

1. **Создание:** Разработчик пишет `SnakeLocomotionSystem` и настраивает компонент наград.
2. **Обучение:** Скрипт `train.py` импортирует Stable-Baselines3, скармливает ему `SerpentineGymEnv` и вызывает `model.learn(total_timesteps=2_000_000)`. За 5-10 минут (благодаря векторизации) RL-модель находит оптимальную политику выживания.
3. **Экспорт:** Модель сохраняется в формат **ONNX** (`snake_ppo_brain.onnx`).
4. **Интеграция:** Разработчик открывает DPG GUI (режим Architect), добавляет агенту-змейке в Behavior Tree узел `ONNX_InferenceNode`, указывает путь к файлу.
5. **Тест:** Нажимает `[▶ Play]`. Движок работает в обычном (Debug) режиме на 30 TPS. Агент-змейка, управляемый только что обученной нейросетью, идеально собирает яблоки на экране, а разработчик видит все его мысли в реальном времени.