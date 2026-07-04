# Design Document: Game Dev Component Library (Game Dev ECS)

In ECS architecture, **Component is purely a data container**. It has no logic lines (no `move()` or `take_damage()` methods). Thanks to `Pydantic`, this data is automatically validated and instantly turns into widgets (sliders, checkboxes) in our DearPyGui interface.

Below is the design of standardized components that will turn Serpentine from a site parser into a full-fledged 2D game engine (RPG, Survival, Arcade).

---

## 1. Spatial & Physics

These components define the physical presence of the entity in the world. They will be handled by `PhysicsSystem` and `CollisionSystem`.

```python
from pydantic import BaseModel, Field
from typing import Tuple, Literal, Dict, List

class TransformComponent(BaseModel):
    """Position and size of the entity in the 2D world"""
    x: float = 0.0
    y: float = 0.0
    width: float = 32.0
    height: float = 32.0
    rotation: float = 0.0  # Angle in degrees
    layer: int = 0         # Z-Index for rendering sorting (0 - ground, 1 - objects)

class VelocityComponent(BaseModel):
    """Movement vector"""
    dx: float = 0.0
    dy: float = 0.0
    max_speed: float = 100.0
    friction: float = 0.9  # Deceleration (sliding)

class ColliderComponent(BaseModel):
    """Geometry for collision calculation"""
    shape: Literal["box", "circle"] = "box"
    is_trigger: bool = False  # If True - does not block movement, but generates an event (e.g., coin collection)
    offset_x: float = 0.0     # Collider offset relative to Transform center
    offset_y: float = 0.0
    radius: float = 16.0      # Used only if shape == "circle"

```

---

## 2. Rendering & Visuals

These components are read by the `GUIDebugSystem` (specifically its internal renderer module) to transfer data from memory to the graphical interface screen.

```python
class SpriteComponent(BaseModel):
    """Graphics display"""
    texture_id: str = "default_sprite"  # Link to loaded texture in DPG registry
    tint_color: Tuple[int, int, int, int] = (255, 255, 255, 255) # RGBA filter
    is_visible: bool = True
    animation_state: str = "idle" # For frame switching ("run", "attack")

class TextLabelComponent(BaseModel):
    """Floating text (e.g., NPC names or damage)"""
    text: str = ""
    color: Tuple[int, int, int, int] = (255, 255, 255, 255)
    offset_y: float = -20.0 # Draw slightly above head

```

---

## 3. Gameplay Mechanics (RPG & Gameplay Mechanics)

Responsible for game rules. Processed by systems like `CombatSystem`, `InventorySystem`, or Judge in Gymnasium mode.

```python
class StatsComponent(BaseModel):
    """Base stats (Health, Mana, Stamina)"""
    hp: float = 100.0
    max_hp: float = 100.0
    mana: float = 50.0
    max_mana: float = 50.0
    base_damage: float = 10.0
    defense: float = 5.0
    is_alive: bool = True

class InventoryComponent(BaseModel):
    """Bag with items"""
    capacity: int = 20
    # Store items as dictionary {item_id: quantity}
    items: Dict[str, int] = Field(default_factory=dict)
    equipped_weapon_id: str | None = None

class StatusEffectComponent(BaseModel):
    """Buffs and debuffs (Fire, Poison, Haste)"""
    # List of active effects with timers {effect_name: duration_ticks}
    active_effects: Dict[str, int] = Field(default_factory=dict)

```

---

## 4. Controllers & Tags

The engine needs to understand *who* makes decisions for this entity. In ECS, this is implemented by adding "Tag Components".

```python
class PlayerControllerComponent(BaseModel):
    """
    Tag: this entity is controlled by a human via keyboard/mouse.
    Read by HumanInputSystem.
    """
    input_mapped: bool = True
    # Can add custom key bindings
    key_up: str = "W"
    key_down: str = "S"

class AIControllerComponent(BaseModel):
    """
    Tag: this entity is controlled by artificial intelligence.
    The AI_BrainSystem will trigger this entity's Behavior Tree.
    """
    behavior_tree_name: str = "default_npc_tree"
    target_entity_id: str | None = None # Whom we are pursuing right now

```

---

## Practical Example (Entity Assembly)

The beauty of ECS is that you create complex game objects simply by combining these Pydantic classes like Lego blocks.

### Example 1: The Hero

Create an entity and attach components:

* `TransformComponent(x=100, y=100)`
* `VelocityComponent(max_speed=200)`
* `ColliderComponent(shape="box")`
* `SpriteComponent(texture_id="hero_texture")`
* `StatsComponent(hp=100, base_damage=25)`
* `InventoryComponent()`
* **`PlayerControllerComponent()`** ➡️ Thanks to this component, pressing 'W' will change `Velocity.dy`.

### Example 2: Poison Trap

* `TransformComponent(x=500, y=500)`
* `ColliderComponent(shape="box", is_trigger=True)` ➡️ Cannot bump into, can only step on.
* `SpriteComponent(texture_id="trap_spikes", tint_color=(0, 255, 0, 255))`
* *Logic:* A specific system (`TrapSystem`) looks for intersections of players with trigger traps. On intersection, adds `"poison": 60` (poisoned for 60 ticks) to the player's `StatusEffectComponent`.

### Example 3: Brain in a Jar (LLM Agent)

If we want to inhabit the game with a smart NPC who trades with the player via ChatGPT:

* `TransformComponent(...)`
* `SpriteComponent(texture_id="merchant")`
* **`AIControllerComponent(behavior_tree_name="merchant_dialogue")`**
* **`MemoryComponent(...)`** ➡️ The Behavior Tree will record conversation history with the player here.
* **`PerceptionComponent(...)`** ➡️ The perception system will put JSON about who is standing next to the merchant here every tick.

---

With this set of components, you can build any 2D simulation in the engine's RAM, on which your agents will then be trained.

The next logical step would be to write a base `World` class (entity registry) that can accept these components, quickly filter them for Systems, and serialize them to JSON for saving. Shall we write code for `core/ecs.py`?
# Design Document: Game Dev ECS Systems

In ECS architecture, **System** is pure logic (function) having no state of its own. Every tick, it requests from the `World` registry a list of entities with the needed "signature" (set of components) and processes them en masse.

Below is the design of base Systems that will "animate" components from the previous document and turn the Serpentine engine into a full-fledged 2D game.

---

## 1. Base System Interface

All systems inherit from a single base class. Since our loop is asynchronous, the update method is also `async`.

```python
from abc import ABC, abstractmethod

class BaseSystem(ABC):
    @abstractmethod
    async def update(self, world: 'World', dt: float):
        """
        world: link to entity registry.
        dt: delta time (time in seconds elapsed since last tick).
        """
        pass

```

---

## 2. Input System (PlayerInputSystem)

This system bridges the developer/player keyboard and internal engine physics.

* **Signature:** `PlayerControllerComponent` + `VelocityComponent`
* **Logic:**
1. Polls global input state (e.g., via DearPyGui `dpg.is_key_down()`).
2. Finds player entity.
3. Changes `dx` and `dy` vector in `VelocityComponent` depending on held keys (WASD).



```python
class PlayerInputSystem(BaseSystem):
    async def update(self, world, dt):
        entities = world.get_entities_with(PlayerControllerComponent, VelocityComponent)
        
        for ent in entities:
            vel = world.get_component(ent, VelocityComponent)
            ctrl = world.get_component(ent, PlayerControllerComponent)
            
            # Reset speed before polling
            vel.dx = 0.0
            vel.dy = 0.0
            
            if is_key_pressed(ctrl.key_up): vel.dy -= vel.max_speed
            if is_key_pressed(ctrl.key_down): vel.dy += vel.max_speed
            # ... logic for left/right ...
            
            # Diagonal movement normalization (to avoid faster diagonal movement)
            normalize_vector(vel) 

```

---

## 3. Physics & Movement System (PhysicsMovementSystem)

Responsible for moving objects in space considering time.

* **Signature:** `TransformComponent` + `VelocityComponent`
* **Logic:** Applies classic Euler integration: . Applies friction for smooth deceleration of sliding objects.

```python
class PhysicsMovementSystem(BaseSystem):
    async def update(self, world, dt):
        entities = world.get_entities_with(TransformComponent, VelocityComponent)
        
        for ent in entities:
            transform = world.get_component(ent, TransformComponent)
            vel = world.get_component(ent, VelocityComponent)
            
            transform.x += vel.dx * dt
            transform.y += vel.dy * dt
            
            # Apply friction (slow down objects if no force is applied)
            vel.dx *= vel.friction
            vel.dy *= vel.friction

```

---

## 4. Collision Resolution System (CollisionResolutionSystem)

The most mathematically complex base system. It prevents objects from passing through walls and processes triggers (loot collection, trap hit).

* **Signature:** `TransformComponent` + `ColliderComponent`
* **Logic:**
1. Collects all colliders on the level.
2. Uses spatial hashing (Spatial Grid) or simple double loop (if entities < 1000) to find AABB (Axis-Aligned Bounding Box) intersections.
3. **Solid Bodies:** If a player hits a wall, the system calculates Penetration Vector and pushes the player's `TransformComponent` back exactly to the wall boundary.
4. **Triggers:** If the collider has `is_trigger=True` flag (e.g., coin or poison zone), the system does not push the player but generates an event in engine memory: `TriggerEvent(entity_A, entity_B)`.



---

## 5. Stats & Combat System (CombatAndStatsSystem)

Manages vital stats and effects. Ideal for RPGs and survival games.

* **Signature:** `StatsComponent` + optionally `StatusEffectComponent`
* **Logic:**
1. **Regeneration / DoT:** Iterates through `StatusEffectComponent`. If sees `"poison": 5.0` (poison for 5 seconds), subtracts HP from `StatsComponent` proportional to `dt` and decreases poison timer.
2. **Death Check:** If `hp <= 0`, system sets flag `is_alive = False`.
3. **Garbage Collector (Death Handler):** If `is_alive == False`, system calls `world.remove_entity(ent)` or generates `LootDropEvent`, replacing hero sprite with tombstone sprite.



---

## 6. Rendering (GUIDebugSystem / Rendering)

Bridge between ECS math and DearPyGui graphical interface. Works only in **Architect** and **Teacher** modes. In **Headless/Gym** mode, this system is simply excluded from the update list, saving 100% GPU resources.

* **Signature:** `TransformComponent` + `SpriteComponent`
* **Logic:**
1. Takes canvas (Drawlist) from Perception Viewer window in DPG.
2. Clears canvas from previous frame.
3. Sorts entities by Z-index (`TransformComponent.layer`) so ground draws under player.
4. Sends batch of render commands:
`dpg.draw_image(sprite.texture_id, pmin=(x, y), pmax=(x+w, y+h), color=sprite.tint_color)`



---

## 7. Execution Pipeline

In the main `SerpentineEngine` loop, the call order of these systems is strictly deterministic. Changing order will break physics.

Correct Game Tick Pipeline:

1. **`PlayerInputSystem`**: Human gives commands (sets vectors).
2. **`AI_BrainSystem`**: NPC Behavior Trees think and also set movement vectors or attack actions.
3. **`PhysicsMovementSystem`**: All objects move by set vectors (possibly hitting walls).
4. **`CollisionResolutionSystem`**: Engine notices those who hit walls and pushes them back. Processes traps.
5. **`CombatAndStatsSystem`**: Damage from traps/weapons applied, dead removed.
6. **`GUIDebugSystem` (Renderer)**: Final, mathematically correct frame picture is drawn.

---

## Integration with Player Agents (RL & LLM)

How does an external AI agent (from previous design docs) play this internal game?

Very simply:

1. `PerceptionPipelineSystem` (specifically its `InternalStateNode`) "photographs" `World` state (reads Transforms) right before render and collects them into JSON matrix.
2. This matrix goes into player agent's `PerceptionComponent`.
3. Next tick, `AI_BrainSystem` feeds this JSON to neural network. Neural network generates `Action` (e.g., Move Up).
4. Action translation node writes vector (0, -100) to agent's `VelocityComponent`.
5. And the cycle repeats! Physics moves the agent.

Architecture design (Core, Data, Logic, Interface, and MLOps Pipelines) is fully complete. Each system detail is strictly isolated but works as a unified clockwork mechanism.

Ready to move to writing **base engine code**? I can create `core/ecs.py` file with implementation of `World`, `BaseSystem` and ultra-fast filter `get_entities_with` based on Python Sets.
