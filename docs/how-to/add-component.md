# How-to: Добавить новый ECS-компонент

## Проблема

Вам нужно добавить новый тип данных (компонент), который можно прикрепить к сущностям в ECS-мире Serpentine Engine.

## Решение

### 1. Создайте класс, наследующий `BaseComponent`

Все компоненты — Pydantic-модели, наследующие `BaseComponent` (`core/component.py`):

```python
from serpentine.core.component import BaseComponent
from serpentine.core.registry import Registry
from pydantic import Field

@Registry.register_component
class MyCustomComponent(BaseComponent):
    data: str = "default_value"
    count: int = Field(default=0, ge=0)
```

### 2. Зарегистрируйте через декоратор

Декоратор `@Registry.register_component` (регистр `Registry._components`) делает компонент доступным:
- для сериализации/десериализации через `World.take_snapshot()` / `World.restore_snapshot()`
- для получения по имени через `Registry.get_component("MyCustomComponent")`
- для бит-маски через `Registry.get_component_mask(MyCustomComponent)`

**Важно**: импортируйте файл с компонентом до вызова любой функции, использующей Registry (например, в `__init__.py` модуля или в точке входа).

### 3. Используйте компонент

#### Чтение одного компонента у сущности:
```python
comp = world.get_component(entity_id, MyCustomComponent)
if comp:
    print(comp.data)
```

#### Чтение всех компонентов этого типа:
```python
comps = world.get_components(MyCustomComponent)  # Dict[EntityID, MyCustomComponent]
```

#### Проверка наличия:
```python
if world.has_component(entity_id, MyCustomComponent): ...
```

#### Запрос сущностей с несколькими компонентами:
```python
for eid, my_comp, transform in world.get_entities_with(MyCustomComponent, TransformComponent):
    ...
```

### 4. Правила

| Правило | Пояснение |
|---------|-----------|
| Только данные | Компонент — **чистые данные**. Без логики. |
| Pydantic-валидация | Поля автоматом валидируются при создании: `MyCustomComponent(count=-1)` → ошибка. |
| `model_dump(mode='json')` | Сериализация в JSON. |
| `model_validate(data)` | Десериализация из JSON (используется в `World.restore_snapshot`). |
| `arbitrary_types_allowed=True` | Включено в `BaseComponent.model_config`. |

### 5. Пример из кода

**TransformComponent** (`components/standard.py`):
```python
@Registry.register_component
class TransformComponent(BaseComponent):
    x: float = 0.0
    y: float = 0.0
    rotation: float = 0.0
    scale_x: float = 1.0
    scale_y: float = 1.0
    parent: Optional[EntityID] = None
    children: List[EntityID] = Field(default_factory=list)
```

**MailboxComponent** (`components/swarm.py`):
```python
@Registry.register_component
class MailboxComponent(BaseComponent):
    inbox: List[SwarmMessage] = Field(default_factory=list)
    outbox: List[SwarmMessage] = Field(default_factory=list)
```

## Альтернативы

- **RegistryV2** (`core/registry_v2.py`) — альтернативный регистр с категориями для узлов, систем и окон GUI. Для компонентов RegistryV2 не используется; все компоненты регистрируются через `Registry.register_component`.

## Связанное

- How-to: добавить систему
- Reference: ECS API
