# Detailed Task List

This document breaks down the development of the Serpentine Engine into actionable tasks, prioritized by impact and dependency.

**Priorities:**
*   **P0 (Critical)**: Must-have for the engine to run. Blocking dependency.
*   **P1 (High)**: Core feature for agent functionality.
*   **P2 (Medium)**: Important for usability and scaling (MAS, UI).
*   **P3 (Low)**: Advanced features, optimizations, nice-to-haves.

---

## Phase 1: Core Engine & ECS Architecture

### 1.1 Core Data Structures
*   [x] **P0** Implement `Entity` (UUID wrapper).
*   [x] **P0** Implement `BaseComponent` (Pydantic model).
*   [x] **P0** Implement `World` class with component storage (`_components`).
*   [x] **P0** Implement `get_entities_with` using set intersection logic (`&`).
*   [ ] **P1** Implement Reactive Query Caching (Group/Signature system).

### 1.2 System Architecture
*   [x] **P0** Define `System` abstract base class with `update(world, dt)` method.
*   [x] **P0** Implement `SerpentineEngine` main loop with `asyncio`.
*   [x] **P1** Implement Tick Rate Limiter and `sleep` logic.

### 1.3 Standard Component Library
*   [x] **P0** `TransformComponent` (Spatial).
*   [x] **P0** `StatsComponent` (Health/Stamina).
*   [x] **P1** `SpatialGridComponent` (Navigation).
*   [x] **P1** `InventoryComponent` (Resource management).

---

## Phase 2: The Body (Perception & Action)

### 2.1 Ingestion Pipeline
*   [x] **P1** Implement `SensoryInputSystem` (Abstract Interface).
*   [x] **P1** Implement `ScreenCaptureNode` (using `mss` or `playwright`).
*   [x] **P2** Implement `InternalStateReader` for direct perception bypass.

### 2.2 Perception Pipeline
*   [x] **P1** Implement `PerceptionComponent` (Ephemeral storage).
*   [x] **P1** Implement `PerceptionPipelineSystem` (DAG processor).
*   [x] **P2** create `CropNode` and `GrayscaleNode` (OpenCV wrappers).
*   [x] **P3** Implement `StateBuilderNode` (JSON sink).

### 2.3 Action Execution
*   [x] **P1** Implement `ActionBufferComponent` (Queue).
*   [x] **P1** Define `BaseAction` class with `target_env` field.
*   [x] **P1** Implement `ActionExecutionSystem` (Command pattern).
*   [x] **P2** Implement `ClickAction` and `MoveAction` (pyautogui integration).

---

## Phase 3: The Mind (Cognitive System)

### 3.1 Behavior Tree Engine
*   [x] **P1** Implement `BehaviorTreeNode` base class.
*   [x] **P1** Implement `Sequence`, `Selector` composite nodes.
*   [x] **P1** Implement `Status` enum (`SUCCESS`, `FAILURE`, `RUNNING`).

### 3.2 AI Integration
*   [x] **P1** Implement `BrainComponent` (Context storage).
*   [x] **P1** Implement `BaseAIAdapter` interface.
*   [x] **P2** Create `OpenAILikeAdapter` (httpx client).
*   [x] **P2** Implement `ContextBuilder` service.
*   [x] **P2** Implement `LLMInferenceNode` (Async API call wrapper).

---

## Phase 4: The Swarm (Multi-Agent System)

### 4.1 Agent Identity & Messaging
*   [x] **P2** Implement `AgentMetaComponent` (Name, Role, Status).
*   [x] **P2** Implement `Message` Pydantic model.
*   [x] **P2** Implement `MailboxComponent` (Inbox/Outbox).

### 4.2 Swarm Orchestration
*   [x] **P2** Implement `MessageRouterSystem` (Event Bus logic).
*   [x] **P2** Implement `SendMessageNode` (BT Leaf).
*   [x] **P2** Implement `ListenForEventNode` (BT Decorator/Leaf).

---

## Phase 5: God Mode (UI & Developer Tools)

### 5.1 DearPyGui Core Workspace
*   [x] **P1** Implement `GUIDebugSystem` with base Viewport and Docking Space layout.
*   [x] **P1** Implement Control Deck (Transport buttons, Mode switch).
*   [ ] **P2** Implement Time Travel (Snapshot) logic in Control Deck.

### 5.2 World Outliner (Менеджер Сущностей)
*   [x] **P2** Implement Tree view of entities & tags.
*   [x] **P1** Implement Add Entity (Spawn) logic via `[+]` button.
*   [x] **P1** Implement Destroy Entity logic via `[🗑️]` button.
*   [x] **P1** Implement selection state broadcast `selected_entity_id`.

### 5.3 Component Inspector (Zero-Code UI)
*   [x] **P1** Implement `auto_ui_builder.py` for primitive types (int, string, bool).
*   [x] **P1** Add support for Dropdowns (`Enum`) and Nested lists/dicts.
*   [x] **P1** Implement Live Data Binding (two-way mutation of World state).
*   [x] **P2** Add `[Select Component Class...]` dropdown to attach components dynamically.
*   [x] **P2** Add `[X]` cross button to strip components from entities.

### 5.4 Perception Monitor (Зрительная кора)
*   [x] **P2** Render CCTV Tabs framework.
*   [x] **P1** Implement GPU Texture View (Zero-copy rendering setup for future arrays).
*   [x] **P1** Implement JSON Tree fallback (rendering `raw_context` and Entity lens).
*   [x] **P2** Implement Debug Layers (YOLO Bounding Boxes, Passability Grid toggle). (Viewport Framework Done)

### 5.5 Brain & Memory Editor (Мозг)
*   [x] **P1** Implement Blackboard Table (Key-Value live editing stream).
*   [x] **P2** Implement Episodic Memory log (showing last 5 actions/thoughts).
*   [ ] **P2** Implement LLM Prompt Preview window (Read-only compilation).

### 5.6 Actions & Swarm Visualizers
*   [x] **P2** Implement Action Queue UI with `[X]` cancel and live status viewer. (Done)
*   [ ] **P2** Implement Live BT Tracer Node Editor (Read-only execution graph).
*   [ ] **P3** Implement Pipeline Node Editor (DAG builder with preview pins).
*   [ ] **P3** Implement Swarm Message Broker Monitor (Sniffer, Dead letters).

---

## Phase 6: Environment, Simulation & Teacher Mode
*   [ ] **P3** Implement Internal Physics & Rendering Systems (Gymnasium bounds).
*   [ ] **P3** Implement Generic Environment Router (Bypass for internal OS).
*   [x] **P1** Add `[⏺ REC] Teacher Mode` UI button in Control Deck.
*   [x] **P1** Implement `HumanInputSystem` (Translate DPG clicks -> `ActionBufferComponent`).
*   [x] **P1** Implement `DatasetLoggerSystem` (Dump State+Action pairs to JSONL / HDF5).
*   [x] **P2** Build `dataset_prep.py` to compile Ground Truth data into YOLO/PyTorch formats.

---

## Phase 6.5: Continuous Learning (Actor-Learner)
*   [x] **P1** Add `EngineMode.ACTOR_LEARNER` and `Phase.REWARD`, `Phase.INPUT` to core engine pipeline.
*   [x] **P1** Extend `BrainComponent` to track `last_state` and `last_action` with `WAITING_FOR_IO` status.
*   [x] **P1** Inject stubs for `EnvironmentJudgeSystem` and `ReplayBufferSystem` into `advanced.py`.
*   [x] **P2** Implement I/O Async Locks inside `SensoryInputSystem` and `ActionExecutionSystem`.
*   [x] **P2** Implement `ReplayBufferSystem` Redis/SQLite export bridge (JSONL implemented).
*   [ ] **P3** Implement File Watcher in `ONNXInferenceNode` for Hot-Swapping weights.

---

## Phase 6.8: Gymnasium Mode (Reinforcement Learning)
*   [x] **P1** Implement `RewardComponent` (`current_reward`, `total_score`, `is_terminated`, `is_truncated`).
*   [x] **P1** Create `SerpentineGymEnv` wrapper class inheriting from `gymnasium.Env` for RL libraries.
*   [x] **P2** Implement `EngineMode.GYMNASIUM` with fast-forward/uncapped TPS (Tick logic updates).
*   [x] **P2** Implement `EnvironmentJudgeSystem` logic to evaluate Game/World rules per tick.
*   [ ] **P3** Test Swarm Mass-Vectorization feature (1000 agents in one World).

---

## Phase 7: Persistence (GUI Integrated)

### 7.1 State Persistence
*   [x] **P1** Implement `World.serialize` method (JSON dump).
*   [x] **P1** Implement `World.deserialize` method (Restore state).
*   [x] **P1** Implement Time Travel (Pause, Load Snapshot, Resume).
*   [x] **P1** Implement Component Registry for dynamic loading.

### 7.2 Configuration & Layout
*   [x] **P2** Implement Blueprint Save/Load (Serialize DAG & BT config).
*   [ ] **P3** Implement UI Layout Saver (`dpg_layout.ini`).

---

## Phase 8: Operation Modes

### 8.1 Mode Switching Logic
*   [x] **P1** Implement `EngineMode` enum (ARCHITECT, PRODUCTION, TEACHER, GYMNASIUM).
*   [x] **P1** Update `SerpentineEngineV2` to configure systems/tick-rate based on mode.

### 8.2 Mode-Specific Systems
*   [x] **P2** Implement `TelemetrySystem` (Log metrics).
*   [x] **P2** Implement `HumanInputSystem` (Capture mouse/keyboard).
*   [x] **P2** Implement `EnvironmentJudgeSystem` (RL Rewards).
*   [x] **P3** Integrate `FastAPI` router for Production mode.

---

## Phase 9: Sample Project (Snake AI)

### 9.1 Snake Simulation
*   [x] **P1** Implement `SnakeBodyComponent`, `GridPositionComponent`.
*   [x] **P1** Implement `SnakeLocomotionSystem` (Movement).
*   [x] **P1** Implement `SnakeCollisionSystem` (Rules).

### 9.2 Snake Agent Interface
*   [x] **P2** Implement `InternalGridStateNode` (Perception).
*   [x] **P2** Implement `ChangeDirectionAction` and handler.
*   [x] **P2** Verify RL Training Loop (Gymnasium). (Verified at 1200+ FPS)

---

## Phase 10: Scene Management

### 10.1 Registry Architecture
*   [x] **P1** Implement `ComponentRegistry` & `SystemRegistry`.
*   [x] **P1** Implement `@register_component` and `@register_system` decorators.
*   [x] **P1** Refactor all existing Components/Systems to use decorators.

### 10.2 Scene Loader
*   [x] **P1** Implement `SceneManager.save/load`.
*   [x] **P2** Implement `Scene` data structure (JSON schema).

### 10.3 CLI & Entry Point
*   [x] **P1** Create `main.py` with `argparse`.
*   [x] **P1** Implement dynamic system instantiation from Scene config.

---

## Phase 11: Play Mode (ModernGL Rendering)
*   [x] **P1** Add `EngineMode.PLAY` and `EngineState.DEV/PLAY` to core engine loop.
*   [x] **P1** Implement `ModernGLRenderSystem` stub (Window + Context setup).
*   [x] **P1** Implement `PlayerInputSystem` stub (Hardware input bridge).
*   [x] **P2** Implement `PossessionSystem` (AI <-> Human body swapping).
*   [x] **P1** Implement full `ModernGLRenderSystem` pipeline (Geometry, Shaders).
*   [x] **P2** Implement Camera Raycasting for 3D world interaction.
