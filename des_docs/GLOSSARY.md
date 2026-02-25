# Glossary of Terms

## Core Concepts

### Entity
A lightweight, unique identifier (UUID). It has no data or logic itself; it is just a key to group Components. Represented by the `Entity` type alias.

### Component
A pure data container (Pydantic Model). It holds state but has no methods/logic.
*   *Examples*: `TransformComponent`, `HealthComponent`, `WebSessionComponent`.

### System
A logic processor that iterates over Entities with specific Components.
*   *Examples*: `PhysicsSystem` (moves things), `RenderSystem` (draws things).

### Registry V2
A metadata-rich discovery service that tracks all components, systems, and nodes. It enables dynamic engine orchestration and zero-code GUI generation.

### World
The central container/database that stores all Entities and Components. It provides query methods like `get_entities_with()`.

---

## AI & Logic

### Behavior Tree (BT)
A hierarchical tree structure used to control the flow of decision execution.
*   **Root**: The starting point of the logic.
*   **Control Nodes**: `Sequence` (AND), `Selector` (OR), `Parallel`.
*   **Leaf Nodes**: `Action` (Do something), `Condition` (Check something).

### Blackboard (Memory)
A key-value store (`MemoryComponent.blackboard`) shared between all nodes of a single agent's Behavior Tree. Used to pass variables (e.g., `target_id`) from a "Find Target" node to an "Attack Target" node.

### Perception Pipeline
A Directed Acyclic Graph (DAG) of processing nodes that converts raw input (Pixels, HTML) into structured data (JSON).

---

## Execution & Modes

### Tick
One complete cycle of the engine loop (Input -> Logic -> Render).

### Phase
A distinct stage within a Tick (e.g., `PERCEPTION`, `PHYSICS`). Systems are registered to specific phases.

### Modes
*   **Architect**: Debug mode with full GUI.
*   **Headless**: Production mode without GUI (for servers).
*   **Gymnasium**: RL training mode (fast-forward, no sleep).
*   **Teacher**: Data collection mode (human input).

---

## Networking (Swarm)

### Agent
An Entity composed of at least `PerceptionComponent`, `BrainComponent`, and `ActionBufferComponent`.

### Topic
A string channel name used for Pub/Sub broadcasting (e.g., "market_update").

### Mailbox
A component handling incoming (`inbox`) and outgoing (`outbox`) messages for an agent.

---

## 🚀 Unified Dataflow

### Observation
The structured output of the Perception Phase (CV, DOM). It represents the agent's current understanding of the environment.

### Intent
The output of the Cognition Phase (BT/LLM). It represents a high-level goal (e.g., "Attack") before it is translated into a physical command.

### Command
The output of the Execution Phase. A physical instruction (e.g., "Left-Click @ 10,20") executed against an environment.
