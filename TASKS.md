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
*   [ ] **P0** Implement `Entity` (UUID wrapper).
*   [ ] **P0** Implement `BaseComponent` (Pydantic model).
*   [ ] **P0** Implement `World` class with component storage (`_components`).
*   [ ] **P0** Implement `get_entities_with` using set intersection logic (`&`).
*   [ ] **P1** Implement Reactive Query Caching (Group/Signature system).

### 1.2 System Architecture
*   [ ] **P0** Define `System` abstract base class with `update(world, dt)` method.
*   [ ] **P0** Implement `SerpentineEngine` main loop with `asyncio`.
*   [ ] **P1** Implement Tick Rate Limiter and `sleep` logic.

### 1.3 Standard Component Library
*   [ ] **P0** `TransformComponent` (Spatial).
*   [ ] **P0** `StatsComponent` (Health/Stamina).
*   [ ] **P1** `SpatialGridComponent` (Navigation).
*   [ ] **P1** `InventoryComponent` (Resource management).

---

## Phase 2: The Body (Perception & Action)

### 2.1 Ingestion Pipeline
*   [ ] **P1** Implement `SensoryInputSystem` (Abstract Interface).
*   [ ] **P1** Implement `ScreenCaptureNode` (using `mss` or `playwright`).
*   [ ] **P2** Implement `InternalStateReader` for direct perception bypass.

### 2.2 Perception Pipeline
*   [ ] **P1** Implement `PerceptionComponent` (Ephemeral storage).
*   [ ] **P1** Implement `PerceptionPipelineSystem` (DAG processor).
*   [ ] **P2** create `CropNode` and `GrayscaleNode` (OpenCV wrappers).
*   [ ] **P3** Implement `StateBuilderNode` (JSON sink).

### 2.3 Action Execution
*   [ ] **P1** Implement `ActionBufferComponent` (Queue).
*   [ ] **P1** Define `BaseAction` class with `target_env` field.
*   [ ] **P1** Implement `ActionExecutionSystem` (Command pattern).
*   [ ] **P2** Implement `ClickAction` and `MoveAction` (pyautogui integration).

---

## Phase 3: The Mind (Cognitive System)

### 3.1 Behavior Tree Engine
*   [ ] **P1** Implement `BehaviorTreeNode` base class.
*   [ ] **P1** Implement `Sequence`, `Selector` composite nodes.
*   [ ] **P1** Implement `Status` enum (`SUCCESS`, `FAILURE`, `RUNNING`).

### 3.2 AI Integration
*   [ ] **P1** Implement `BrainComponent` (Context storage).
*   [ ] **P1** Implement `BaseAIAdapter` interface.
*   [ ] **P2** Create `OpenAILikeAdapter` (httpx client).
*   [ ] **P2** Implement `ContextBuilder` service.
*   [ ] **P2** Implement `LLMInferenceNode` (Async API call wrapper).

---

## Phase 4: The Swarm (Multi-Agent System)

### 4.1 Agent Identity & Messaging
*   [ ] **P2** Implement `AgentMetaComponent` (Name, Role, Status).
*   [ ] **P2** Implement `Message` Pydantic model.
*   [ ] **P2** Implement `MailboxComponent` (Inbox/Outbox).

### 4.2 Swarm Orchestration
*   [ ] **P2** Implement `MessageRouterSystem` (Event Bus logic).
*   [ ] **P2** Implement `SendMessageNode` (BT Leaf).
*   [ ] **P2** Implement `ListenForEventNode` (BT Decorator/Leaf).

---

## Phase 5: God Mode (UI & Developer Tools)

### 5.1 DearPyGui Framework
*   [ ] **P2** Implement `GUIDebugSystem` (Main Window setup).
*   [ ] **P2** setup Viewport vs. Docking Space layout.

### 5.2 Inspectors & Visualizers
*   [ ] **P2** Implement `World Outliner` widget.
*   [ ] **P2** Implement `Entity Inspector` (Component editor).
*   [ ] **P3** Implement `Blackboard Visualizer` (Table view).
*   [ ] **P3** Implement `Swarm Monitor` (Traffic Matrix).

---

## Phase 6: Environment & Simulation

### 6.1 Advanced Simulation
*   [ ] **P3** Implement `InternalPhysicsSystem` (Simple collision).
*   [ ] **P3** Implement `InternalRenderSystem` (2D Sprite renderer).

### 6.2 MLOps & Training
*   [ ] **P3** Integrate `ONNXRuntime` for `YOLONode`.
*   [ ] **P3** Implement `DatasetLoggerSystem` (Data collection).
*   [ ] **P3** Implement `Teacher Mode` logic.

---

## Phase 7: Persistence

### 7.1 World Serialization
*   [ ] **P1** Implement `World.serialize` method (JSON dump).
*   [ ] **P1** Implement `World.deserialize` method (Hot-Reload).
*   [ ] **P1** Implement Component Registry for dynamic loading.

### 7.2 Configuration & Deployment
*   [ ] **P2** Implement `ProjectConfig` loader (Pipeline/BT blueprints).
*   [ ] **P3** Implement `UI Layout` saver (.ini).
*   [ ] **P2** Implement `Engine.pause/resume` logic.

---

## Phase 8: Operation Modes

### 8.1 Mode Switching Logic
*   [ ] **P1** Implement `EngineMode` enum (ARCHITECT, PRODUCTION, TEACHER, GYMNASIUM).
*   [ ] **P1** Update `SerpentineEngineV2` to configure systems/tick-rate based on mode.

### 8.2 Mode-Specific Systems
*   [ ] **P2** Implement `TelemetrySystem` (Log metrics).
*   [ ] **P2** Implement `HumanInputSystem` (Capture mouse/keyboard).
*   [ ] **P2** Implement `EnvironmentJudgeSystem` (RL Rewards).
*   [ ] **P3** Integrate `FastAPI` router for Production mode.

---

## Phase 9: Sample Project (Snake AI)

### 9.1 Snake Simulation
*   [ ] **P1** Implement `SnakeBodyComponent`, `GridPositionComponent`.
*   [ ] **P1** Implement `SnakeLocomotionSystem` (Movement).
*   [ ] **P1** Implement `SnakeCollisionSystem` (Rules).

### 9.2 Snake Agent Interface
*   [ ] **P2** Implement `InternalGridStateNode` (Perception).
*   [ ] **P2** Implement `ChangeDirectionAction` and handler.
*   [ ] **P2** Verify RL Training Loop (Gymnasium).

---

## Phase 10: Scene Management

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
