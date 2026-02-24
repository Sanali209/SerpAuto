# Serpentine Engine: Architecture Overview

## 1. High-Level Design (The Layer Cake)

Serpentine uses a modern **Entity-Component-System (ECS)** architecture, which decouples data from logic. This is distinct from traditional OOP game engines (like Unity's GameObjects before DOTS) or web scrapers.

### The 4 Layers of Serpentine

1.  **Core (Foundation)**
    *   **World**: The database of all Entities and Components.
    *   **Registry**: Auto-discovery mechanism for systems and components.
    *   **Engine Loop**: The heartbeat (Tick) that orchestrates execution phases.

2.  **Body (Perception & Action)**
    *   **Perception System**: Ingests raw data (Screen pixels, DOM tree, JSON APIs).
    *   **Action System**: Translates logical intents (`ClickAction`) into OS commands (Playwright, PyAutoGUI).

3.  **Mind (Cognition)**
    *   **Brain System**: Executes decision-making logic.
    *   **Behavior Tree**: The structure of agent logic (Sequence, Selector).
    *   **LLM Adapter**: Interface to AI models (GPT-4, Local LLM) for high-level reasoning.

4.  **Swarm (Networking)**
    *   **Message Router**: Handles Pub/Sub communication between agents.
    *   **Mailbox**: The inbox/outbox buffer for each agent.

---

## 2. The Engine Loop (Tick Cycle)

The `SerpentineEngineV2` executes systems in a strict phase order to ensure deterministic behavior.

| Phase | System Example | Responsibility |
| :--- | :--- | :--- |
| **1. INPUT** | `HumanInputSystem` | Read keyboard/mouse override commands. |
| **2. MAIL_ROUTING** | `MessageRouterSystem` | Move messages from `Outbox` A -> `Inbox` B. |
| **3. PERCEPTION** | `PerceptionPipelineSystem` | Run CV/DOM nodes to update `PerceptionComponent`. |
| **4. INTERNAL_PHYSICS** | `TransformHierarchySystem` | Update positions, handle collisions. |
| **5. COGNITION** | `AI_BrainSystem` | Tick Behavior Trees, generate Actions. |
| **6. EXECUTION** | `ActionExecutionSystem` | Execute queued actions (Click, Type, Move). |
| **7. REWARD** | `EnvironmentJudgeSystem` | Calculate RL rewards (Gym Mode only). |
| **8. TELEMETRY** | `TelemetrySystem` | Log FPS, stats, send to dashboard. |

---

## 3. Dependency Graph

```mermaid
graph TD
    User[Developer / User] -->|Configures| Blueprints[Blueprints / JSON]
    Blueprints -->|Loads| World

    subgraph ECS Loop
        Input --> Routing
        Routing --> Perception
        Perception --> Physics
        Physics --> Cognition
        Cognition --> Execution
        Execution --> Telemetry
    end

    World -->|Data| ECS Loop
    ECS Loop -->|Updates| World
```

---

## 4. Key Architectural Patterns

*   **Data-Driven**: Logic is generic (`System`); behavior is defined by data (`Component`). An agent becomes a "Sniper" not by class inheritance, but by attaching a `SniperRifleComponent` and `LongRangeBehaviorComponent`.
*   **Reactive Query Caching**: The `World` maintains cached sets of entities (e.g., "All entities with Position AND Velocity") to make iteration O(1).
*   **Asynchronous Core**: Systems are `async def update()`. This allows long-running IO (Network requests, LLM inference) to run concurrently without freezing the simulation tick.
