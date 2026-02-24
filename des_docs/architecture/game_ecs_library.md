# Дизайн-документ: Библиотека Компонентов для Разработки Игр (Game Dev ECS)

В архитектуре ECS **Компонент — это исключительно контейнер с данными**. В нем нет ни одной строчки логики (никаких методов `move()` или `take_damage()`). Благодаря использованию `Pydantic`, эти данные автоматически валидируются и мгновенно превращаются в виджеты (ползунки, чекбоксы) в нашем интерфейсе DearPyGui.

Ниже представлен дизайн стандартизированных компонентов, которые превратят Serpentine из парсера сайтов в полноценный 2D-игровой движок (RPG, Survival, Аркады).

---

## 1. Пространство и Физика (Spatial & Physics)

Эти компоненты определяют физическое присутствие сущности в мире. Их будут обрабатывать `PhysicsSystem` и `CollisionSystem`.

```python
from pydantic import BaseModel, Field
from typing import Tuple, Literal, Dict, List

class TransformComponent(BaseModel):
    """Позиция и размер сущности в 2D мире"""
    x: float = 0.0
    y: float = 0.0
    width: float = 32.0
    height: float = 32.0
    rotation: float = 0.0  # Угол в градусах
    layer: int = 0         # Z-Index для сортировки отрисовки (0 - земля, 1 - объекты)

class VelocityComponent(BaseModel):
    """Вектор движения"""
    dx: float = 0.0
    dy: float = 0.0
    max_speed: float = 100.0
    friction: float = 0.9  # Замедление (скольжение)

class ColliderComponent(BaseModel):
    """Геометрия для просчета столкновений"""
    shape: Literal["box", "circle"] = "box"
    is_trigger: bool = False  # Если True - не блокирует движение, но генерирует событие (например, сбор монетки)
    offset_x: float = 0.0     # Смещение коллайдера относительно центра Transform
    offset_y: float = 0.0
    radius: float = 16.0      # Используется только если shape == "circle"

```

---

## 2. Рендеринг и Визуал (Rendering & Visuals)

Эти компоненты читаются системой `InternalRenderSystem`, чтобы перенести данные из памяти на экран графического интерфейса.

```python
class SpriteComponent(BaseModel):
    """Отображение графики"""
    texture_id: str = "default_sprite"  # Ссылка на загруженную текстуру в реестре DPG
    tint_color: Tuple[int, int, int, int] = (255, 255, 255, 255) # RGBA фильтр
    is_visible: bool = True
    animation_state: str = "idle" # Для переключения кадров ("run", "attack")

class TextLabelComponent(BaseModel):
    """Плавающий текст (например, имена NPC или урон)"""
    text: str = ""
    color: Tuple[int, int, int, int] = (255, 255, 255, 255)
    offset_y: float = -20.0 # Отрисовать чуть выше головы

```

---

## 3. Игровые Механики (RPG & Gameplay Mechanics)

Отвечают за правила игры. Обрабатываются системами вроде `CombatSystem`, `InventorySystem` или Судьей в режиме Gymnasium.

```python
class StatsComponent(BaseModel):
    """Базовые характеристики (Health, Mana, Stamina)"""
    hp: float = 100.0
    max_hp: float = 100.0
    mana: float = 50.0
    max_mana: float = 50.0
    base_damage: float = 10.0
    defense: float = 5.0
    is_alive: bool = True

class InventoryComponent(BaseModel):
    """Сумка с предметами"""
    capacity: int = 20
    # Храним предметы как словарь {item_id: quantity}
    items: Dict[str, int] = Field(default_factory=dict)
    equipped_weapon_id: str | None = None

class StatusEffectComponent(BaseModel):
    """Баффы и дебаффы (Огонь, Яд, Ускорение)"""
    # Список активных эффектов с таймерами {effect_name: duration_ticks}
    active_effects: Dict[str, int] = Field(default_factory=dict)

```

---

## 4. Контроллеры и Теги (Controllers & Tags)

Движку нужно понимать, *кто* принимает решения за эту сущность. В ECS это реализуется добавлением "компонентов-маркеров" (Tag Components).

```python
class PlayerControllerComponent(BaseModel):
    """
    Маркер: этой сущностью управляет человек с клавиатуры/мыши.
    Читается системой HumanInputSystem.
    """
    input_mapped: bool = True
    # Можно добавить кастомные бинды клавиш
    key_up: str = "W"
    key_down: str = "S"

class AIControllerComponent(BaseModel):
    """
    Маркер: этой сущностью управляет искусственный интеллект.
    Система AI_BrainSystem будет дергать Behavior Tree этой сущности.
    """
    behavior_tree_name: str = "default_npc_tree"
    target_entity_id: str | None = None # Кого мы преследуем прямо сейчас

```

---

## Как это выглядит на практике (Сборка Сущностей)

Красота ECS в том, что ты создаешь сложные игровые объекты просто комбинируя эти Pydantic-классы, как кубики Lego.

### Пример 1: Игрок (The Hero)

Создаем сущность и вешаем на нее компоненты:

* `TransformComponent(x=100, y=100)`
* `VelocityComponent(max_speed=200)`
* `ColliderComponent(shape="box")`
* `SpriteComponent(texture_id="hero_texture")`
* `StatsComponent(hp=100, base_damage=25)`
* `InventoryComponent()`
* **`PlayerControllerComponent()`** ➡️ Благодаря этому компоненту, нажатие клавиши 'W' изменит `Velocity.dy`.

### Пример 2: Ядовитая Ловушка (Poison Trap)

* `TransformComponent(x=500, y=500)`
* `ColliderComponent(shape="box", is_trigger=True)` ➡️ Нельзя упереться, можно только наступить.
* `SpriteComponent(texture_id="trap_spikes", tint_color=(0, 255, 0, 255))`
* *Логика:* Специфическая система (`TrapSystem`) ищет пересечения игроков с триггерами-ловушками. При пересечении добавляет в `StatusEffectComponent` игрока `"poison": 60` (отравлен на 60 тиков).

### Пример 3: Мозг в Банке (LLM Agent)

Если мы хотим поселить в игру умного NPC, который торгуется с игроком через ChatGPT:

* `TransformComponent(...)`
* `SpriteComponent(texture_id="merchant")`
* **`AIControllerComponent(behavior_tree_name="merchant_dialogue")`**
* **`MemoryComponent(...)`** ➡️ Сюда Behavior Tree будет записывать историю общения с игроком.
* **`PerceptionComponent(...)`** ➡️ Система восприятия будет каждый тик класть сюда JSON о том, кто стоит рядом с торговцем.

---

С этим набором компонентов ты можешь построить в оперативной памяти движка любую 2D-симуляцию, на которой потом будут обучаться твои агенты.

Следующим шагом логично будет написать базовый класс `World` (реестр сущностей), который сможет принимать эти компоненты, быстро их фильтровать для Систем и сериализовать в JSON для сохранения. Напишем код для файла `core/ecs.py`?
# Дизайн-документ: Игровые Системы (Game Dev ECS Systems)

В архитектуре ECS **Система (System)** — это чистая логика (функция), не имеющая собственного состояния. Она каждый тик запрашивает у реестра `World` список сущностей с нужной "сигнатурой" (набором компонентов) и массово их обрабатывает.

Ниже представлен дизайн базовых Систем, которые "оживят" компоненты из предыдущего документа и превратят движок Serpentine в полноценную 2D-игру.

---

## 1. Базовый интерфейс Системы

Все системы наследуются от единого базового класса. Поскольку наш цикл асинхронный, метод обновления тоже `async`.

```python
from abc import ABC, abstractmethod

class BaseSystem(ABC):
    @abstractmethod
    async def update(self, world: 'World', dt: float):
        """
        world: ссылка на реестр сущностей.
        dt: delta time (время в секундах, прошедшее с прошлого тика).
        """
        pass

```

---

## 2. Система Ввода (PlayerInputSystem)

Эта система перекидывает мост между клавиатурой разработчика/игрока и внутренней физикой движка.

* **Сигнатура:** `PlayerControllerComponent` + `VelocityComponent`
* **Логика работы:**
1. Опрашивает глобальный стейт ввода (например, через DearPyGui `dpg.is_key_down()`).
2. Находит сущность игрока.
3. Меняет вектор `dx` и `dy` в `VelocityComponent` в зависимости от зажатых клавиш (WASD).



```python
class PlayerInputSystem(BaseSystem):
    async def update(self, world, dt):
        entities = world.get_entities_with(PlayerControllerComponent, VelocityComponent)
        
        for ent in entities:
            vel = world.get_component(ent, VelocityComponent)
            ctrl = world.get_component(ent, PlayerControllerComponent)
            
            # Обнуляем скорость перед опросом
            vel.dx = 0.0
            vel.dy = 0.0
            
            if is_key_pressed(ctrl.key_up): vel.dy -= vel.max_speed
            if is_key_pressed(ctrl.key_down): vel.dy += vel.max_speed
            # ... логика для влево/вправо ...
            
            # Нормализация диагонального движения (чтобы не бегать быстрее по диагонали)
            normalize_vector(vel) 

```

---

## 3. Система Физики и Движения (PhysicsMovementSystem)

Отвечает за перемещение объектов в пространстве с учетом времени.

* **Сигнатура:** `TransformComponent` + `VelocityComponent`
* **Логика работы:** Применяет классическую интеграцию Эйлера: . Применяет трение (Friction) для плавного торможения скользящих объектов.

```python
class PhysicsMovementSystem(BaseSystem):
    async def update(self, world, dt):
        entities = world.get_entities_with(TransformComponent, VelocityComponent)
        
        for ent in entities:
            transform = world.get_component(ent, TransformComponent)
            vel = world.get_component(ent, VelocityComponent)
            
            transform.x += vel.dx * dt
            transform.y += vel.dy * dt
            
            # Применяем трение (замедляем объекты, если к ним не применяется сила)
            vel.dx *= vel.friction
            vel.dy *= vel.friction

```

---

## 4. Система Столкновений (CollisionResolutionSystem)

Самая математически сложная базовая система. Она не дает объектам проходить сквозь стены и обрабатывает триггеры (сбор лута, попадание в ловушку).

* **Сигнатура:** `TransformComponent` + `ColliderComponent`
* **Логика работы:**
1. Собирает все коллайдеры на уровне.
2. Использует пространственное хеширование (Spatial Grid) или простой двойной цикл (если сущностей < 1000) для поиска пересечений AABB (Axis-Aligned Bounding Box).
3. **Твердые тела (Solid):** Если игрок въехал в стену, система вычисляет вектор проникновения (Penetration Vector) и отталкивает `TransformComponent` игрока назад ровно на границу стены.
4. **Триггеры (Trigger):** Если коллайдер имеет флаг `is_trigger=True` (например, монетка или зона яда), система не отталкивает игрока, а генерирует событие в память движка: `TriggerEvent(entity_A, entity_B)`.



---

## 5. Система Статусов и Боя (CombatAndStatsSystem)

Управляет жизненными показателями и эффектами. Идеально для RPG и выживалок.

* **Сигнатура:** `StatsComponent` + опционально `StatusEffectComponent`
* **Логика работы:**
1. **Регенерация / Урон со временем (DoT):** Пробегается по `StatusEffectComponent`. Если видит `"poison": 5.0` (яд на 5 секунд), отнимает HP из `StatsComponent` пропорционально `dt` и уменьшает таймер яда.
2. **Проверка смерти:** Если `hp <= 0`, система ставит флаг `is_alive = False`.
3. **Сборщик мусора (Death Handler):** Если `is_alive == False`, система вызывает `world.remove_entity(ent)` или генерирует `LootDropEvent`, заменяя спрайт героя на спрайт надгробия.



---

## 6. Внутренний Рендер (InternalRenderSystem)

Мост между математикой ECS и графическим интерфейсом DearPyGui. Работает только в режимах **Architect** и **Teacher**. В **Headless/Gym** режиме эта система просто исключается из списка обновления, экономя 100% ресурсов GPU.

* **Сигнатура:** `TransformComponent` + `SpriteComponent`
* **Логика работы:**
1. Берет холст (Drawlist) из окна Perception Viewer в DPG.
2. Очищает холст от прошлого кадра.
3. Сортирует сущности по Z-индексу (`TransformComponent.layer`), чтобы земля рисовалась под игроком.
4. Отправляет пачку команд рендера:
`dpg.draw_image(sprite.texture_id, pmin=(x, y), pmax=(x+w, y+h), color=sprite.tint_color)`



---

## 7. Порядок Выполнения (The Execution Pipeline)

В главном цикле `SerpentineEngine` порядок вызова этих систем строго детерминирован. Изменение порядка сломает физику.

Правильный Pipeline игрового тика:

1. **`PlayerInputSystem`**: Человек дает команды (задает векторы).
2. **`AI_BrainSystem`**: Behavior Trees NPC думают и тоже задают векторы движения или экшены атаки.
3. **`PhysicsMovementSystem`**: Все объекты сдвигаются по заданным векторам (возможно, въезжая в стены).
4. **`CollisionResolutionSystem`**: Движок замечает тех, кто въехал в стены, и выталкивает их обратно. Обрабатывает ловушки.
5. **`CombatAndStatsSystem`**: Применяется урон от ловушек/оружия, удаляются мертвые.
6. **`InternalRenderSystem`**: Отрисовывается финальная, математически корректная картинка кадра.

---

## Интеграция с Агентами-Игроками (RL & LLM)

Как внешний ИИ-агент (из предыдущих дизайн-документов) играет в эту внутреннюю игру?

Очень просто:

1. Система `PerceptionPipelineSystem` (точнее, ее узел `InternalStateNode`) перед самым рендером "фотографирует" состояние `World` (читает Transform'ы) и собирает их в JSON-матрицу.
2. Эта матрица ложится в `PerceptionComponent` агента-игрока.
3. На следующем тике `AI_BrainSystem` скормит этот JSON нейросети. Нейросеть сгенерирует `Action` (например, Идти Вверх).
4. Узел трансляции экшенов запишет в `VelocityComponent` агента вектор (0, -100).
5. И цикл повторится! Физика сдвинет агента.

Дизайн архитектуры (Ядро, Данные, Логика, Интерфейс и Пайплайны MLOps) полностью завершен. Каждая деталь системы строго изолирована, но работает как единый часовой механизм.

Готов перейти к написанию **базового кода движка**? Я могу создать файл `core/ecs.py` с реализацией `World`, `BaseSystem` и сверхбыстрого фильтра `get_entities_with` на основе Python-множеств (Sets).