# Component Reference

This document serves as a complete directory of all components available in the Serpentine Engine. Components are data containers (Pydantic models) that are attached to Entities and processed by Systems.

---

## 🏗️ Core Components (`components/core.py`)

These components form the backbone of the agent architecture and messaging.

### `MetadataComponent`
Generic entity identification.
- `name`: Human-readable name (default: "New Entity").
- `tags`: List of strings for categorization.
- `color`: RGBA list `[1.0, 1.0, 1.0, 1.0]` for UI highlighting.

### `MailboxComponent`
Enables inter-agent communication (Pub/Sub).
- `inbox`: List of incoming `Message` objects.
- `outbox`: List of outgoing `Message` objects.
- `subscriptions`: List of topic strings the agent listens to.

### `MemoryComponent` (Blackboard)
Working and episodic memory store.
- `blackboard`: Dictionary for arbitrary key-value storage.
- `history`: Sequential log of actions for LLM context.

### `PerceptionComponent`
Ephemeral snapshot of the world, updated every tick.
- `visible_entities`: List of dictionaries describing perceived entities.
- `raw_context`: Parsed JSON representation of the current view/state.
- `raw_frame_id`: ID of the visual frame (if applicable).

### `BrainComponent`
Status and Behavior Tree execution state.
- `status`: Lifecycle state (`IDLE`, `THINKING`, `WAITING_LLM`).
- `context`: Active decision context.
- `bt_root`: Reference to the live BT root instance.

### `ActionBufferComponent`
Execution queue for the `ActionExecutionSystem`.
- `queue`: List of pending actions to be executed.
- `current_action_status`: State of the current action processing.

---

## 🌍 Spatial & Hierarchy (`components/spatial.py`)

Components for 2D/3D positioning and parent-child relationships.

### `TransformComponent`
Physical position and orientation.
- `local_x`, `local_y`: Position relative to parent.
- `world_x`, `world_y`: Absolute world position (calculated).
- `local_rotation`, `local_scale_x`, `local_scale_y`: Orientation and size.

### `HierarchyComponent`
Constructs a Scene Graph.
- `parent`: UUID of the parent entity.
- `children`: List of child entity UUIDs.

### `VelocityComponent`
Vector for physical movement.
- `vx`, `vy`: Velocity on X and Y axes.

### `ColliderComponent`
Hitbox for collision detection.
- `is_solid`: Whether it blocks other objects.
- `layer`: Collision layer name.
- `type`: Semantic type (`head`, `body`, `apple`).

---

## 🌐 Web Perception (`components/web.py`)

Used by the Scraper and WebOS pipeline.

### `DOMNodeComponent`
HTML element representation.
- `xpath`, `css_selector`: Location in the DOM.
- `attributes`: Dictionary of HTML attributes (href, class, etc.).
- `extracted_text`: Text content of the node.

### `PayloadExtractionComponent`
Container for data collected during scraping.
- `target_schema_name`: Name of the Pydantic schema for validation.
- `extracted_data`: Dictionary of collected fields.

---

## 🎮 Game & Internal Components (`components/internal.py`, `components/domain.py`)

Specialized components for simulation and gamified workflows.

### `RewardComponent` (`core.py` / `internal.py`)
Used for Reinforcement Learning (Gymnasium).
- `current_reward`: Scalar reward for the current tick.
- `cumulative_reward`: Total reward for the episode.
- `is_terminated`: Flag for episode end.

### `SpriteComponent` (`internal.py`)
Visual representation for internal rendering.
- `texture_path`: Path to an image file.
- `scale`, `visible`: Rendering controls.

### `StatsComponent` (`domain.py`)
Vital statistics for agents.
- `health`, `max_health`, `stamina`.
- `status_effects`: List of active buffs/debuffs.

### `InventoryComponent` (`domain.py`)
Resource management.
- `capacity`: Maximum item count.
- `items`: Dictionary mapping item names to quantities.
