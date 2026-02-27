# Design Document: Cognitive Hybrid Engine "Serpentine" (v2.0)

## 1. Concept and Architectural Philosophy

Serpentine is an asynchronous, Tick-based engine based on the Entity-Component-System (ECS) pattern. It is designed to create both single autonomous agents and multi-agent swarms capable of seamlessly operating in external environments (OS, Web browsers, third-party games) and internal simulations.

**Main Paradigm:** Complete separation of Data, Logic, and Interfaces. The engine operates as a unified highway where rigid scripts (Behavior Trees) and probabilistic models (LLM/CV) are combined via standardized interfaces.

## 2. Core Engine (Core ECS & Loop)

### 2.1. State Registry (World)
The entire system state is stored in the `World` object. Entities are UUID identifiers. All information is stored in Components. Search is performed via ultra-fast set intersection (Query Caching), allowing processing of thousands of entities in milliseconds.

### 2.2. Base Components (Data Models)
Components are strictly typed via Pydantic BaseModel. This ensures built-in validation and a foundation for auto-generating GUI.

#### A. Cognitive Components
*   `PerceptionComponent`: Snapshot of the environment at the current tick (JSON with DOM parsing or CV objects).
*   `MemoryComponent` (Blackboard): Agent working memory (Key-Value) and history (log for LLM).
*   `ActionBufferComponent`: FIFO queue (`List[BaseAction]`) for commands execution.
*   `BrainComponent`: Status (IDLE, RUNNING, WAITING) and context.
*   `RewardComponent` (RL): Reward for the current step (for Gymnasium Mode).

#### B. Communication Components (Swarm)
*   `AgentMetaComponent`: Name, role, status.
*   `MailboxComponent`: Pub/Sub buffer (inbox, outbox, subscriptions).

#### C. Spatial/Internal Components
*   `TransformComponent`: Position (x, y, w, h, layer).
*   `HierarchyComponent`: Defines kinship (parent/children) for Data-Driven Hierarchy.
*   `VelocityComponent`: Velocity vector (vx, vy).
*   `ColliderComponent`: Geometry for physics (Box/Circle).
*   `SpriteComponent`: Texture for internal rendering.
*   **More on Hierarchy**: See [Hierarchy Implementation in ECS](ecs_hierarchy_impl.md) and [Hierarchy Management in GUI](ecs_hierarchy_gui.md).

### 2.3. Main Asynchronous Loop (The Engine Tick Loop)
The engine is not blocked by heavy calculations. Target Tick Rate — 20-60 TPS (in Headless/Gym mode — unlimited).

**System Execution Order (Phases):**
1.  **Input Phase**: `HumanInputSystem` captures user input (Phase.INPUT).
2.  **Mail Routing Phase**: `MessageRouterSystem` distributes messages from outbox to inbox of recipients (Phase.MAIL_ROUTING).
3.  **Perception Phase**: Collection of raw data (`SensoryInputSystem`) and processing through a directed graph of filters (`PerceptionPipelineSystem`). Updates `PerceptionComponent` (Phase.PERCEPTION).
4.  **Internal Physics Phase**: `InternalPhysicsSystem` moves internal entities, calculates collisions (Phase.INTERNAL_PHYSICS).
5.  **Cognition Phase**: `AI_BrainSystem` polls Behavior Trees of each agent (Phase.COGNITION).
6.  **Execution Phase**: `ActionExecutionSystem` routes commands from the buffer (Phase.EXECUTION).
7.  **Reward Phase**: `EnvironmentJudgeSystem` calculates rewards in Gymnasium mode (Phase.REWARD).
8.  **Telemetry Phase**: GUI update (`GUIDebugSystem`), dataset logging (`DatasetLoggerSystem`) (Phase.TELEMETRY).

### 2.4. Unified Dataflow (Consolidation Strategy)
The engine moves to a standardized data flow to ensure modularity:
1.  **Observations**: Output of Perception Phase. Raw sensor data packed into Pydantic models.
2.  **Intent**: Output of Cognition Phase. Behavior Tree forms a logical goal (e.g., "Move to apple").
3.  **Commands**: Output of Execution Phase. Conversion of intents into physical actions (Click, Move, Key).

### 2.5. Data-Driven Orchestration
Instead of hardcoding systems in `main.py`, the engine uses **RegistryV2**.
- Each system is marked with `@register_system(modes=[EngineMode.ARCHITECT, ...])`.
- The orchestrator dynamically assembles the system graph at startup, allowing new functions (plugins) to be added without modifying the core.

> [!TIP]
> **Deep Dive into Core**:
> *   [Entity Hierarchy Implementation](ecs_hierarchy_impl.md)
> *   [Game Component Library](game_ecs_library.md)
> *   [System Implementation Guide](../guides/system_implementation_guide.md)

## 3. Perception and Computer Vision (Perception Pipeline)

Pipeline for processing incoming data, built on DAG (Directed Acyclic Graph) architecture.

*   **Nodes**: Each filter has a Pydantic config (auto-binding in GUI) and a `process(context)` method. See [Perception Nodes Registry](perception_nodes.md).
*   **Visual Editor**: The entire pipeline is configured via [**Perception Pipeline Editor**](perception_pipeline_editor.md).
*   **Base Filters**:
    *   `DOMParserNode`: Extraction of XPath/CSS selectors.
    *   `OpenCVNodes`: Crop, Grayscale, Threshold, MatchTemplate.
    *   `YOLONode` (ONNX Runtime): Using compiled Ultralytics YOLOv8/v11 models for instant object detection (bounding boxes) without heavy PyTorch.
    *   `OCRNode`: Text extraction from crops (Docling/Tesseract).
    *   `GridMapperNode`: Transformation of pixels into isometric/2D grid `passability_grid`.

## 4. Hybrid Mind (Cognition Core)

Combines deterministic reliability and ML adaptability.

### 4.1. Behavior Tree (BT)
The behavior tree is the foundation of logic. Nodes communicate via the agent's Blackboard.

*   **Control Nodes**: `Selector` (find first success), `Sequence` (strict order).
*   **Decorator Nodes**: Inverters, timers (`WaitNode`).
*   **MAS Nodes**: `SendMessageNode` (send to Pub/Sub), `ListenForEventNode` (wait in inbox).

### 4.2. Model Adapters (AI Bridge)
The Behavior Tree does not know which model is connected. The `LLM_Inference` node uses adapters. `ContextBuilder` compresses `PerceptionComponent` and Blackboard into a text JSON prompt.

*   `OpenAILikeAdapter`: For large models (GPT-4/Gemini) with chat history and Function Calling.
*   `MicroserviceAdapter`: For fast HTTP calls to lightweight models (Koyeb/Hugging Face).
*   `N8NWebhookAdapter`: Transferring agent state to an external n8n workflow.

## 5. Multi-Agent System (MAS & Pub/Sub)

Agents are strictly isolated and do not have direct access to each other's memory.

*   **Event Bus**: Communication occurs via `MessageRouterSystem`.
*   **Topics**: A scout agent publishes `{"topic": "target_found", "payload": {...}}`. A fighter agent or scraper agent, who has `target_found` in `MailboxComponent.subscriptions`, receives this letter in their inbox on the next tick.
*   **Benefits**: Prevention of Race Conditions, easy swarm scaling, ability to restart stuck agents without crashing the entire system.

## 6. Action Execution (Action Routing)

Command pattern system. Any action is an object (e.g., `ClickAction`, `SendAPIAction`).

**Target Environment Routing (target_env):**
Each action has a target flag:
*   `EXTERNAL_OS`: Executed via OS drivers (Playwright, PyAutoGUI). The agent interacts with a real browser, game, or factory software.
*   `INTERNAL_ENGINE`: Executed via direct modification of components of another entity in World. The agent plays an "internal" game or interacts with another internal agent.

## 7. Tooling and GUI (DearPyGui)

The graphical interface is not part of the logic, but a pluggable system (`GUIDebugSystem`) running in real-time.

### 7.1. Auto-Interface (Pydantic ➡️ DPG)
The engine automatically scans Pydantic schemas of node and filter configurations, generating sliders, checkboxes, and dropdowns (Zero-code GUI for new modules).

### 7.2. "God Mode" Dashboard (Workspace)
*   **Global Roster**: Table of active swarm agents with their current status, CPU load, and task.
*   **Contextual Inspector**: Selecting an agent updates all panels (Tree, Memory, Buffer) only for it.
*   **Live BT Tracer**: Graphical display of the Behavior Tree with pulsing nodes (green/red/yellow) for debugging logic in real-time.
*   **Buffer Editor**: Ability to manually delete an erroneous action from `ActionBufferComponent` or change a variable in Blackboard "hot".
*   **Perception View**: Multi-window or grid (CCTV) render of screens/pipelines with zero copying (Zero-copy GPU render via DPG Texture Registry). Ability to toggle intermediate CV layers (e.g., see only Canny Edges layer or YOLO Bounding Boxes).
*   **Message Broker Sniffer**: Log of Pub/Sub traffic between agents with highlighting of Dead Letter (undelivered) messages.

> [!TIP]
> **Interface Details**:
> *   [God Mode Layout and Modules](gui_layout_design.md)
> *   [Visualizing Hierarchy in Editor](ecs_hierarchy_gui.md)

**More on GUI**: See [GUI Layout and Module Design](gui_layout_design.md).

## 8. Operation Modes (Lifecycle)

The ECS architecture allows radically changing engine behavior simply by changing the composition of active Systems and time cycle parameters. The engine supports instant mode switching for neural network training.

### 8.1. Mode: Architect & Debug (Developer Mode)
Visual programming and debugging. [More...](../modes/play_mode.md)
*   **Systems**: Standard + `GUIDebugSystem`.
*   **Features**: Hot-Reloading workspaces, "God Mode", Zero-Copy Rendering (OpenCV -> Texture).

### 8.2. Mode: Production / Headless (Combat Server Mode)
Background operation without GUI. Ideal for Docker/Koyeb.
*   **Systems**: Standard + `TelemetrySystem`. `GUIDebugSystem` is disabled.
*   **Features**: REST API (FastAPI) for external control, metrics (Prometheus).

### 8.3. Mode: Teacher (Dataset Collection)
Action capture studio for Imitation Learning. [More...](../modes/teacher_mode.md)
*   **Systems**: `AI_BrainSystem` disabled. `HumanInputSystem` and `DatasetLoggerSystem` enabled.
*   **Features**: Operator controls the agent via GUI. Engine writes `[Perception, Action]` pairs to HDF5/JSONL.

### 8.4. Mode: Gymnasium (RL Gym)
Simulation for Reinforcement Learning (PPO, DQN). [More...](../modes/gym_mode.md)
*   **Systems**: `InternalPhysicsSystem` and `EnvironmentJudgeSystem` (reward calculation) enabled.
*   **Features**: Standard API `env.reset()`, `env.step()`. Vectorization of 100+ agents.

### 8.5. Mode: Continuous Learning (Actor-Learner)
Async online learning mode in real I/O environments. [More...](../modes/actor_learner.md)
*   **Systems**: Standard + `EnvironmentJudgeSystem` + `ReplayBufferSystem`.
*   **Features**: Separate Learner process trains model in real-time, Hot-Swapping of ONNX weights.

## 9. Sample Project: Serpentine Snake AI

This sample demonstrates the full cycle: from creating an internal simulation (game) to training an agent (RL) and visual debugging. The game lives exclusively in ECS RAM.

### 9.1. Environment Assembly (Game)
We do not use external windows. Physics runs on components:
*   `GridPositionComponent`: x, y coordinates on the grid.
*   `SnakeBodyComponent`: Queue of tail segments.
*   `VelocityComponent`: Movement vector (dx, dy).
*   `ColliderComponent`: Type (`head`, `body`, `apple`, `wall`).

**Game Systems:**
1.  `SnakeLocomotionSystem`: Moves head every tick, updates tail queue.
2.  `SnakeCollisionSystem`: Game logic (Ate apple -> Grow, Crashed -> Reset).

### 9.2. Cognitive Interface
The agent is an entity with a brain connected to the game via standard interfaces.
*   **Perception**: `InternalGridStateNode` scans ECS and builds JSON matrix (10x10), where 0=Empty, 1=Body, 2=Head, 3=Apple.
*   **Action**: `ChangeDirectionAction` ("UP", "DOWN"...). `ActionExecutionSystem` changes head's `VelocityComponent`.

### 9.3. Training (Gymnasium Mode)
The engine switches to "Gym" mode (no GUI, no sleep).
*   **Reward**: `EnvironmentJudgeSystem` awards +10 for apple, -10 for death, -0.1 per step.
*   **Result**: RL model (PPO) trains in 5 minutes (1M+ steps).

### 9.4. Visualization (God Mode)
In Architect mode, the `GUIDebugSystem` (DearPyGui) is enabled.
*   **Game View**: Rendering of snake and apple with rectangles.
*   **Introspection**: Nearby "raw" perception matrix seen by the network is visible.
*   **Debug**: Can pause, move apple manually (by changing component), take a step and check network reaction.

## 10. Scene & Registry Management

To implement functionality similar to game engines (Unity/Unreal), where you can dynamically add components and configure scenes, a Registry and Scene system is introduced.

### 10.1. Global Registries (Auto-Registration)
For UI and serializer to know about components and systems without hardcoding, decorators are used:
*   `@register_component`: Registers a data class. Allows UI to display "Add Component" list.
*   `@register_system(phase=...)`: Registers logic and binds it to a phase (Physics, Perception).

### 10.2. Scene Format
`.json` file describing full launch configuration (Map + Logic):
```json
{
  "systems": ["SnakeLocomotionSystem", "SnakeCollisionSystem"],
  "entities": [ ... ],
  "settings": { "tick_rate": 10, "mode": "GYMNASIUM" }
}
```

### 10.3. Headless Loader (CLI)
Launching engine with a specific map via console:
`python main.py --scene levels/level_01.json --mode HEADLESS`
This allows training agents on different world configurations without changing code.

## 11. Persistence System

ECS + Pydantic architecture allows complete separation of logic and data, making serialization trivial. Persistence is divided into three levels:

### 11.1. Layer 1: Project Configuration (Project Blueprints)
This is a static "blueprint" of the agent.
*   **What is saved**: Perception Pipeline topology (node graph), filter settings (thresholds), Behavior Tree structure.
*   **Format**: JSON/YAML.
*   **Use Case**: Deploying a configured bot to a server (Koyeb) in Headless mode.

### 11.2. Layer 2: World State Snapshots (World State Snapshots)
This is a dynamic dump of RAM at a specific tick.
*   **What is saved**: Full `World` registry (Entity UUIDs + all current Component values).
*   **Format**: JSON.
*   **Use Case**: Debugging by "time travel". On error, an auto-dump is made. Developer loads it in GUI and sees world state exactly at the moment of the bug.

### 11.3. Layer 3: Interface Layout (GUI State)
Saving window arrangement for developer convenience.
*   **What is saved**: Positions, sizes, and docking of DearPyGui windows.
*   **Format**: `.ini` file (native DPG format).
*   **Use Case**: Personalizing the workspace (log monitor on the right, graph on the left).

### 11.4. Hot-Reload Workflow (Hot-Reload Workflow)
Loading state into a running engine requires stopping time:
1.  **Pause Engine**: `is_running = False`.
2.  **Abort Tasks**: Cancel all asynchronous tasks (LLM requests).
3.  **Deserialize World**: Clear memory and restore entities from JSON.
4.  **Rebuild GUI**: Generate new widgets for loaded data.
5.  **Resume Engine**: Start loop.

---

## 12. Planning and References

To track progress and technical insights, use the following documents:
- [x] Create [**Consolidation Strategy**](../planning/consolidation_strategy.md): Roadmap for structural refinement.
- [x] Create [**Unified Registry & Node Graph**](unified_registry_and_node_graph.md): Metadata and visual tool foundations.
*   [**Detailed Dataflow Map**](dataflow_architecture.md): Visual wiring of Observations and Commands.
*   [**Task List (Backlog)**](../planning/tasks.md): Detailed tasks with priorities P0-P3.
*   [**ML Insights**](../api_ml/ml_integration_insights.md): Implementation details for Hot-Swapping and model versioning.
*   [**Documentation Standards**](../dev_docs_rules.md): Naming rules and file structures.
