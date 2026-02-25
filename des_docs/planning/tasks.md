# Detailed Task List

This document breaks down the development of the Serpentine Engine into actionable tasks, prioritized by impact and dependency.

**Priorities:**
*   **P0 (Critical)**: Must-have for the engine to run. Blocking dependency.
*   **P1 (High)**: Core feature for agent functionality.
*   **P2 (Medium)**: Important for usability and scaling (MAS, UI).
*   **P3 (Low)**: Advanced features, optimizations, nice-to-haves.

---

## Phase 1: Core Engine & ECS Architecture ([**Guide**](../guides/phases/phase_01_core.md))

### 1.1 Core Data Structures
*   [ ] **P0** Implement `Entity` (UUID wrapper).
*   [ ] **P0** Implement `BaseComponent` (Pydantic model).
*   [ ] **P0** Implement `World` class with component storage (`_components`).
*   [ ] **P0** Implement `get_entities_with` using set intersection logic (`&`).
*   [ ] **P1** Implement Reactive Query Caching (Optimized Set Intersection).

### 1.2 System Architecture
*   [ ] **P0** Define `System` abstract base class with `update(world, dt)` method.
*   [ ] **P0** Implement `SerpentineEngine` main loop with `asyncio`.
*   [ ] **P1** Implement Tick Rate Limiter and `sleep` logic.

### 1.3 Standard Component Library ([**Reference**](../architecture/COMPONENT_REFERENCE.md))
*   [ ] **P0** `TransformComponent` ([**Hierarchy**](../architecture/ecs_hierarchy_impl.md)).
*   [ ] **P0** `StatsComponent` (Health/Stamina).
*   [ ] **P1** `SpatialGridComponent` (Navigation).
*   [ ] **P1** `InventoryComponent` (Resource management).

---

## Phase 2: The Body (Perception & Action) ([**Guide**](../guides/phases/phase_02_perception.md))

### 2.1 Ingestion Pipeline
*   [ ] **P1** Implement `SensoryInputSystem` (Abstract Interface).
*   [ ] **P1** Implement `ScreenCaptureNode` (using `mss` or `playwright`).
*   [ ] **P2** Implement `InternalStateReader` for direct perception bypass.

### 2.2 Perception Pipeline ([**Nodes**](../architecture/perception_nodes.md))
*   [ ] **P1** Implement `PerceptionComponent` (Ephemeral storage).
*   [ ] **P1** Implement `PerceptionPipelineSystem` (DAG processor).
*   [ ] **P2** create `CropNode` and `GrayscaleNode` (OpenCV wrappers).
*   [ ] **P1** Implement `OCRNode` (pytesseract/docling wrapper).
*   [ ] **P1** Implement `DOMParserNode` (Playwright/HTML extraction).
*   [ ] **P1** Implement `GridMapperNode` (Navigation mesh generator).
*   [ ] **P3** Implement `StateBuilderNode` (JSON sink).

### 2.3 Action Execution
*   [ ] **P1** Implement `ActionBufferComponent` (Queue).
*   [ ] **P1** Define `BaseAction` class with `target_env` field.
*   [ ] **P1** Implement `ActionExecutionSystem` (Command pattern).
*   [ ] **P2** Implement `ClickAction` and `MoveAction` (pyautogui integration).

---

## Phase 3: The Mind (Cognitive System) ([**Guide**](../guides/phases/phase_03_mind.md))

### 3.1 Behavior Tree Engine ([**Guide**](../guides/BEHAVIOR_TREE_GUIDE.md))
*   [ ] **P1** Implement `BehaviorTreeNode` base class.
*   [ ] **P1** Implement `Sequence`, `Selector` composite nodes.
*   [ ] **P1** Implement **Decorator Nodes** (`Inverter`, `Succeeder`, `Repeat`).
*   [ ] **P1** Implement **Blackboard Logic Nodes** (`CheckVar`, `SetVar`).
*   [ ] **P1** Implement `Status` enum (`SUCCESS`, `FAILURE`, `RUNNING`).
*   [ ] **P2** Implement **Parallel Node** (Run children concurrently).

### 3.2 AI Integration
*   [ ] **P1** Implement `BrainComponent` (Context storage).
*   [ ] **P1** Implement `BaseAIAdapter` interface.
*   [ ] **P2** Create `OpenAILikeAdapter` (httpx client).
*   [ ] **P2** Implement `ContextBuilder` service.
*   [ ] **P2** Implement `LLMInferenceNode` (Async API call wrapper).
*   [ ] **P2** Implement `N8NWebhookAdapter` (External workflow trigger).
*   [ ] **P2** Implement `MicroserviceAdapter` (Lightweight HTTP AI bridge).

---

## Phase 4: The Swarm (Multi-Agent System) ([**Guide**](../guides/phases/phase_04_swarm.md))

### 4.1 Agent Identity & Messaging
*   [ ] **P2** Implement `AgentMetaComponent` (Name, Role, Status).
*   [ ] **P2** Implement `Message` Pydantic model.
*   [ ] **P2** Implement `MailboxComponent` (Inbox/Outbox).

### 4.2 Swarm Orchestration
*   [ ] **P2** Implement `MessageRouterSystem` (Event Bus logic).
*   [ ] **P2** Implement `SendMessageNode` (BT Leaf).
*   [ ] **P2** Implement `ListenForEventNode` (BT Decorator/Leaf).
*   [ ] **P2** Implement **Mailbox Persistence** (Save/Load message history).

---

## Phase 5: God Mode (UI & Developer Tools) ([**Guide**](../guides/phases/phase_05_god_mode.md))

### 5.1 DearPyGui Core Workspace
*   [ ] **P1** Implement `GUIDebugSystem` with base Viewport and Docking Space layout.
*   [ ] **P1** Implement Control Deck (Transport buttons, Mode switch).
*   [ ] **P2** Implement Time Travel (Snapshot) logic in Control Deck.

### 5.2 World Outliner (Менеджер Сущностей)
*   [ ] **P2** Implement Tree view of entities & tags.
*   [ ] **P1** Implement Add Entity (Spawn) logic via `[+]` button.
*   [ ] **P1** Implement Destroy Entity logic via `[🗑️]` button.
*   [ ] **P1** Implement selection state broadcast `selected_entity_id`.

### 5.3 Component Inspector ([**Auto UI**](../architecture/auto_ui_builder.md))
*   [ ] **P1** Implement `auto_ui_builder.py` for primitive types (int, string, bool).
*   [ ] **P1** Add support for Dropdowns (`Enum`) and Nested lists/dicts.
*   [ ] **P1** Implement Live Data Binding (two-way mutation of World state).
*   [ ] **P2** Add `[Select Component Class...]` dropdown to attach components dynamically.
*   [ ] **P2** Add `[ ]` cross button to strip components from entities.

### 5.4 Perception Monitor (Зрительная кора)
*   [ ] **P2** Render CCTV Tabs framework.
*   [ ] **P1** Implement GPU Texture View (Zero-copy rendering setup for future arrays).
*   [ ] **P1** Implement JSON Tree fallback (rendering `raw_context` and Entity lens).
*   [ ] **P2** Implement Debug Layers (YOLO Bounding Boxes, Passability Grid toggle). (Viewport Framework Done)
*   [ ] **P2** Implement **Contextual Inspector** logic (Switching agency focuses all panels).
*   [ ] **P2** Implement **Global Swarm Roster** (Table with CPU/Status/Current Task).

### 5.5 Brain & Memory Editor (Мозг)
*   [ ] **P1** Implement Blackboard Table (Key-Value live editing stream).
*   [ ] **P2** Implement Episodic Memory log (showing last 5 actions/thoughts).
*   [ ] **P2** Implement LLM Prompt Preview window (Read-only compilation).
*   [ ] **P1** Implement **BT Visualizer/Editor** (`dpg.add_node_editor`).
*   [ ] **P3** Implement **Swarm Message Sniffer** (Real-time Pub/Sub log).

### 5.6 Actions & Swarm Visualizers
*   [ ] **P2** Implement Action Queue UI with `[ ]` cancel and live status viewer. (Done)
*   [ ] **P2** Implement **Action Execution Timeline** (Horizontal Gantt-like view).
*   [ ] **P2** Implement Live BT Tracer Node Editor (Read-only execution graph).
*   [ ] **P3** Implement Pipeline Node Editor (DAG builder with preview pins).
*   [ ] **P3** Implement Swarm Message Broker Monitor (Sniffer, Dead letters).

---

## Phase 6: Environment, Simulation & Teacher Mode ([**Guide**](../guides/phases/phase_06_simulation.md))
*   [ ] **P3** Implement Internal Physics & Rendering Systems (Gymnasium bounds).
*   [ ] **P3** Implement Generic Environment Router (Bypass for internal OS).
*   [ ] **P1** Add `[⏺ REC] Teacher Mode` UI button in Control Deck.
*   [ ] **P1** Implement `HumanInputSystem` (Translate DPG clicks -> `ActionBufferComponent`).
*   [ ] **P1** Implement `DatasetLoggerSystem` (Dump State+Action pairs to JSONL / HDF5).
*   [ ] **P2** Build `dataset_prep.py` to compile Ground Truth data into YOLO/PyTorch formats.
*   [ ] **P1** Implement **Shadow Mode** logic (Parallel AI prediction during human control).
*   [ ] **P2** Implement **Imitation Learning Loss Monitor** (Real-time diff in Shadow Mode).

---

## Phase 6.5: Continuous Learning (Actor-Learner)
*   [ ] **P1** Add `EngineMode.ACTOR_LEARNER` and `Phase.REWARD`, `Phase.INPUT` to core engine pipeline.
*   [ ] **P1** Extend `BrainComponent` to track `last_state` and `last_action` with `WAITING_FOR_IO` status.
*   [ ] **P1** Inject stubs for `EnvironmentJudgeSystem` and `ReplayBufferSystem` into `advanced.py`.
*   [ ] **P2** Implement I/O Async Locks inside `SensoryInputSystem` and `ActionExecutionSystem`.
*   [ ] **P2** Implement `ReplayBufferSystem` Redis/SQLite export bridge (JSONL implemented).
*   [ ] **P3** Implement File Watcher in `ONNXInferenceNode` for Hot-Swapping weights.

---

## Phase 6.8: Gymnasium Mode (Reinforcement Learning)
*   [ ] **P1** Implement `RewardComponent` (`current_reward`, `total_score`, `is_terminated`, `is_truncated`).
*   [ ] **P1** Create `SerpentineGymEnv` wrapper class inheriting from `gymnasium.Env` for RL libraries.
*   [ ] **P2** Implement `EngineMode.GYMNASIUM` with fast-forward/uncapped TPS (Tick logic updates).
*   [ ] **P2** Implement `EnvironmentJudgeSystem` logic to evaluate Game/World rules per tick.
*   [ ] **P1** Refactor `SerpentineGymEnv` for **Dynamic Observations** (Fixing hardcoded shape).
*   [ ] **P3** Test Swarm Mass-Vectorization feature (1000 agents in one World).
*   [ ] **P1** Implement **Collision Resolution** (AABB, Penetration Vectors, Friction).
*   [ ] **P2** Implement **RPG Stats System** (Combat, Death handling, XP).
*   [ ] **P2** Implement **Inventory & Items** (Drop logic, Equipment).

---

## Phase 7: Persistence (GUI Integrated) ([**Guide**](../guides/phases/phase_07_persistence.md))

### 7.1 State Persistence ([**System**](../architecture/persistence_system.md))
*   [ ] **P1** Implement `World.serialize` method (JSON dump).
*   [ ] **P1** Implement `World.deserialize` method (Restore state).
*   [ ] **P1** Implement Time Travel (Pause, Load Snapshot, Resume).
*   [ ] **P1** Implement Component Registry for dynamic loading.

### 7.2 Configuration & Layout
*   [ ] **P2** Implement Blueprint Save/Load (Serialize DAG & BT config).
*   [ ] **P3** Implement UI Layout Saver (`dpg_layout.ini`).

---

## Phase 8: Operation Modes ([**Guide**](../guides/phases/phase_08_modes.md))

### 8.1 Mode Switching Logic
*   [ ] **P1** Implement `EngineMode` enum (ARCHITECT, PRODUCTION, TEACHER, GYMNASIUM).
*   [ ] **P1** Update `SerpentineEngineV2` to configure systems/tick-rate based on mode.

### 8.2 Mode-Specific Systems
*   [ ] **P2** Implement `TelemetrySystem` (Log metrics).
*   [ ] **P2** Implement `HumanInputSystem` (Capture mouse/keyboard).
*   [ ] **P2** Implement `EnvironmentJudgeSystem` (RL Rewards).
*   [ ] **P2** Implement `EnvironmentJudgeSystem` (RL Rewards).
*   [ ] **P1** Implement **FastAPI Integration** (Web interface for Headless mode).

---

## Phase 9: Sample Project (Snake AI) ([**Guide**](../guides/phases/phase_09_snake_demo.md)) ([**Gym Guide**](../modes/gym_mode.md))
*   [ ] **P1** Implement `SnakeBodyComponent`, `GridPositionComponent`.
*   [ ] **P1** Implement `SnakeLocomotionSystem` (Movement).
*   [ ] **P1** Implement `SnakeCollisionSystem` (Rules).

### 9.2 Snake Agent Interface
*   [ ] **P2** Implement `InternalGridStateNode` (Perception).
*   [ ] **P2** Implement `ChangeDirectionAction` and handler.
*   [ ] **P2** Verify RL Training Loop (Gymnasium). (Verified at 1200+ FPS)

---

## Phase 10: Scene Management ([**Guide**](../guides/phases/phase_10_scenes.md))

### 10.1 Registry Architecture
*   [ ] **P1** Implement `ComponentRegistry` & `SystemRegistry`.
*   [ ] **P1** Implement `@register_component` and `@register_system` decorators.
*   [ ] **P1** Refactor all existing Components/Systems to use decorators.

### 10.2 Scene Loader
*   [ ] **P1** Implement `SceneManager.save/load`.
*   [ ] **P2** Implement `Scene` data structure (JSON schema).

### 10.3 CLI & Entry Point
*   [ ] **P1** Create `main.py` with `argparse`.
*   [ ] **P1** Implement dynamic system instantiation from Scene config.

---

## Phase 11: Play Mode (ModernGL Rendering) ([**Guide**](../guides/phases/phase_11_rendering.md))
*   [ ] **P1** Add `EngineMode.PLAY` and `EngineState.DEV/PLAY` to core engine loop.
*   [ ] **P1** Implement `ModernGLRenderSystem` stub (Window + Context setup).
*   [ ] **P1** Implement `PlayerInputSystem` stub (Hardware input bridge).
*   [ ] **P2** Implement `PossessionSystem` (AI <-> Human body swapping).
*   [ ] **P1** Implement full `ModernGLRenderSystem` pipeline (Geometry, Shaders).
*   [ ] **P2** Implement Camera Raycasting for 3D world interaction.
*   [ ] **P0** Fix ModernGL Segmentation Fault (Context/Thread Safety).

---

## Phase 12: Integrated Core Modernization ([**Guide**](../guides/phases/phase_12_modernization.md) | [**GUI Design**](../../architecture/gui_modernization_design.md) | [**Registry Design**](../../architecture/unified_registry_and_node_graph.md))

### 12.1 Core Frameworks
*   [ ] **P1** Implement `BaseUIWindow` (Abstract template).
*   [ ] **P1** Implement `WindowManager` (Composite lifecycle manager).
*   [ ] **P1** Implement `SelectionService` (Global selection state).
*   [ ] **P2** Implement `GUIEventBus` (Internal Pub/Sub).
*   [ ] **P1** Implement Registry V2 decorators (`@register_node`).

### 12.2 Porting & Integration
*   [ ] **P1** Migrate Outliner/Inspector to use `SelectionService`.
*   [ ] **P1** Migrate Viewport to broadcast selection via `GUIEventBus`.
*   [ ] **P2** Centralize styles in `style.py`.

---

## Phase 13: Visual Node Graphs ([**Guide**](../guides/phases/phase_13_graph_editors.md))

### 13.1 BT Visual Editor ([**Arch**](../architecture/behavior_tree_editor.md))
*   [ ] **P1** Implement `@register_node` decorator and attribute scanning.
*   [ ] **P1** Implement Node Library Sidebar (populating from [**Registry V2**](../architecture/unified_registry_and_node_graph.md)).
*   [ ] **P1** Implement Inspector Sync via [**SelectionService**](../architecture/unified_registry_and_node_graph.md#2-global-selection-service).
*   [ ] **P1** Implement Data Binding between [**AutoUIBuilder**](../architecture/auto_ui_builder.md) and Node Params.
*   [ ] **P1** Implement Real-time Node Status polling (execution highlights).
*   [ ] **P2** Implement Blackboard Monitor panel (Agent internal memory view).
*   [ ] **P3** Implement Auto-Layout algorithm for messy trees.

### 13.2 Perception Pipeline Editor ([**Arch**](../architecture/perception_pipeline_editor.md))
*   [ ] **P2** Implement DAG visualizer for `PerceptionPipelineSystem` (using `BaseNodeCanvas`).
*   [ ] **P2** Implement pin logic for `Observation` output.
*   [ ] **P3** Add live pin previews (hover on node output to see results).

---

## Phase 15: Framework Consolidation (Structural Refinement) ([**Strategy**](../planning/consolidation_strategy.md))

### 15.1 Dynamic Orchestration
*   [ ] **P1** Refactor `main.py` into a Data-Driven Mode Orchestrator (calling `RegistryV2`).
*   [ ] **P1** Implement `@register_system(mode=...)` metadata scanning.

### 15.2 Unified Dataflow
*   [ ] **P1** Standardize all perception nodes to emit `Observation` objects.
*   [ ] **P1** Standardize all cognitive nodes to emit `Intent` objects.
*   [ ] **P1** Refactor `ActionExecutionSystem` to consume `Intents` and emit `Commands`.

### 15.3 Core Infrastructure
*   [ ] **P2** Implement `BaseNodeCanvas` as the parent for BT and Perception editors.
*   [ ] **P1** Integrate `WorldSnapshot` into the `World` class for native state persistence.

---

## Phase 14: Analytics & Swarm Monitoring ([**Guide**](../guides/phases/phase_14_analytics.md))

### 14.1 Monitoring Tools
*   [ ] **P2** Implement **Global Swarm Roster** (System-wide health table).
*   [ ] **P2** Implement **Action Execution Timeline** (Gantt view).
*   [ ] **P2** Implement **Imitation Learning Loss Monitor** (Shadow mode diffs).
