# Serpentine Engine Roadmap

This roadmap outlines the strategic development phases for the Serpentine Engine, transitioning from a basic ECS framework to a full-scale Multi-Agent System (MAS) with cognitive capabilities.

## Phase 1: Core Engine & ECS Architecture (Foundation) ([**Guide**](../guides/phases/phase_01_core.md))
**Goal**: Establish a robust, high-performance Entity-Component-System framework capable of handling thousands of entities at 60+ TPS.

*   **Milestone 1.1**: Core Data Structures (`World`, `Entity`, [**BaseComponent**](../core/component.py)).
*   **Milestone 1.2**: System Update Loop ([**Engine Overview**](../architecture/engine_overview.md) with `asyncio`).
*   [ ] **Milestone 1.3**: Query Caching & Optimization (Set Intersection Logic).
*   **Milestone 1.4**: Standard Component Library ([**Component Reference**](../architecture/COMPONENT_REFERENCE.md)).

## Phase 2: The Body (Perception & Action Pipelines) ([**Guide**](../guides/phases/phase_02_perception.md))
**Goal**: Enable agents to sense the environment and execute physical actions.

*   **Milestone 2.1**: Ingestion Phase (`SensoryInputSystem`, Screen Capture).
*   **Milestone 2.2**: Perception Pipeline ([**Perception Nodes**](../architecture/perception_nodes.md), DAG Nodes).
*   **Milestone 2.3**: Basic CV Nodes (Crop, Grayscale, Template Matching).
*   [ ] **Milestone 2.4**: Advanced CV/Perception Nodes (**OCR**, YOLO integration).
*   [ ] **Milestone 2.5**: Navigation & Mapping (**Grid Mapper Node**).
*   **Milestone 2.6**: Web Perception (**DOMParserNode**).
*   **Milestone 2.7**: Action Execution (`ActionExecutionSystem`, Buffer Queue).

## Phase 3: The Mind (Cognitive System) ([**Guide**](../guides/phases/phase_03_mind.md))
**Goal**: Integrate decision-making capabilities using Behavior Trees and LLMs.

*   [ ] **Milestone 3.1**: Behavior Tree Engine ([**BT Guide**](../guides/BEHAVIOR_TREE_GUIDE.md)).
*   [ ] **Milestone 3.2**: Blackboard Integration (`MemoryComponent`).
*   **Milestone 3.3**: AI Adapter Interface (`BaseAIAdapter`, Context Builder).
*   **Milestone 3.4**: External Integrations (**N8N, Microservices**).
*   **Milestone 3.5**: LLM Inference Node (Async Integration).

## Phase 4: The Swarm (Multi-Agent System) ([**Guide**](../guides/phases/phase_04_swarm.md))
**Goal**: Scale from single-agent logic to coordinated multi-agent operations.

*   **Milestone 4.1**: Agent Identity & Metadata (`AgentMetaComponent`).
*   [ ] **Milestone 4.2**: Pub/Sub Communication Architecture (`MailboxComponent`).
*   **Milestone 4.3**: Message Router System (Event Bus Orchestrator).
*   **Milestone 4.4**: Swarm Logic Nodes (`SendMessage`, `ListenForEvent`).
*   **Milestone 4.5**: Swarm Monitoring (**Message Sniffer**).
*   **Milestone 4.6**: Mailbox Persistence (Message History).

## Phase 5: God Mode (UI & Developer Tools) ([**Guide**](../guides/phases/phase_05_god_mode.md))
**Goal**: Create a massive Docking Space "Control Center" for surgical debugging of ECS architecture and Multi-Agent Swarms.

*   [ ] **Milestone 5.1**: DearPyGui Core Workspace (Docking Layout, Control Deck).
*   [ ] **Milestone 5.2**: World Outliner (Entity Manager with CRUD operations).
*   [ ] **Milestone 5.3**: Component Inspector ([**Auto UI Builder**](../architecture/auto_ui_builder.md)).
*   **Milestone 5.4**: Perception Monitor (GPU Textures, JSON Tree, Debug Overlays).
*   **Milestone 5.5**: **Contextual Inspector** (Agent-specific logic inspection).
*   **Milestone 5.6**: Brain & Memory Editor (Blackboard Table, **BT Visualizer/Editor**, Prompt Preview, Episodic Memory).
*   **Milestone 5.7**: Actions & Swarm Visualizers (**Action Timeline**, Intervention Queue, BT Tracer, Data Sniffer).
*   **Milestone 5.8**: Global Swarm Roster (CPU/Status/Task overview).

## Phase 6: Environment & Simulation (Advanced Features) ([**Guide**](../guides/phases/phase_06_simulation.md))
**Goal**: Support hybrid environments (External OS + Internal Sim) and MLOps workflows.

*   **Milestone 6.1**: Internal Physics & Rendering Systems (`SpriteComponent`, `VelocitySystem`).
*   **Milestone 6.2**: Environment Routing (`Direct Perception Bypass`).
*   **Milestone 6.3**: MLOps Pipeline Integration (YOLO, ONNX Runtime).
*   **Milestone 6.4**: Dataset Collection Tools (`Teacher Mode`).
*   **Milestone 6.5**: **Shadow Mode Validation** (Model vs Human comparison).
*   **Milestone 6.6**: Collision Resolution (AABB, Penetration Vectors).
*   **Milestone 6.7**: RPG Mechanics (Stats, Inventory, Status Effects).

## Phase 7: Persistence & Deployment (DevOps) ([**Guide**](../guides/phases/phase_07_persistence.md))
**Goal**: Enable saving/loading of agent brains, world states, and tool layouts for seamless debugging ("Time Travel").

*   **Milestone 7.1**: World State Serialization & [**Snapshots**](../architecture/persistence_system.md).
*   **Milestone 7.2**: Project Configuration (Save/Load Blueprints for Pipeline/BT).
*   **Milestone 7.3**: UI Layout Persistence (`dpg.save_init_file`).
*   **Milestone 7.4**: Time Travel & Hot-Reload Logic (Pause, Load Snapshot, Resume).

## Phase 8: Operation Modes (Lifecycle) ([**Guide**](../guides/phases/phase_08_modes.md))
**Goal**: Configure the engine for specific use cases (Debug, Deploy, Train).

*   **Milestone 8.1**: [**Architect Mode**](../modes/architect_mode.md) (GUI + Debug Systems) [ ].
*   **Milestone 8.2**: [**Production Mode**](../modes/production_mode.md) (Headless + Telemetry + **FastAPI Integration**) [ ].
*   **Milestone 8.3**: [**Teacher Mode**](../modes/teacher_mode.md) (Human Input + Dataset Logging) [ ].
*   **Milestone 8.4**: [**Gymnasium Mode**](../modes/gym_mode.md) (Internal Physics + Rewards + Uncapped Speed) [ ].
*   **Milestone 8.5**: [**Continuous Learning Mode**](../modes/actor_learner.md) (Actor-Learner split, Async I/O, Hot-Swapping) [ ].

## Phase 9: Sample Project (Snake AI) ([**Guide**](../guides/phases/phase_09_snake_demo.md))
**Goal**: Demonstrate the full cycle of engine capabilities with a complete internal simulation and RL training loop.

*   [ ] **Milestone 9.1**: Internal Snake Simulation (Locomotion & Collision Systems).
*   [ ] **Milestone 9.2**: Agent Perception (Grid State Node) & Action Mapping.
*   [ ] **Milestone 9.3**: RL Training Loop Integration (Gymnasium).
*   [ ] **Milestone 9.4**: Architect Mode Visual Debugging.

## Phase 10: Scene Management & Dynamic Loading ([**Guide**](../guides/phases/phase_10_scenes.md))
**Goal**: Create a Unity-like experience for managing scenes, systems, and entities dynamically.

*   [ ] **Milestone 10.1**: Global Registries with Decorators (`@register_component/system`).
*   [ ] **Milestone 10.2**: Scene File Format & Manager (Save/Load Scene).
*   [ ] **Milestone 10.3**: CLI Entry Point (`main.py`) for Headless loading.
*   [ ] **Milestone 10.4**: Integration with `SerpentineEngineV2` (Dynamic System Injection).

## Phase 11: Play Mode (ModernGL Rendering) ([**Guide**](../guides/phases/phase_11_rendering.md))
**Goal**: Transition from a debug-only UI to a high-performance 3D/2D game rendering environment.

*   [ ] **Milestone 11.1**: ModernGL Render Pipeline (Shaders, Meshes, FBO).
*   [ ] **Milestone 11.2**: Play In Editor (PIE) Architecture.
*   [ ] **Milestone 11.3**: Player Input System (Hardware Input Bridge).
*   [ ] **Milestone 11.4**: Possession System (Human <-> AI Control Swapping).
*   [ ] **Milestone 11.5**: Camera Raycasting & 3D World Interaction.

## Phase 12: Integrated Core Modernization ([**Guide**](../guides/phases/phase_12_modernization.md) | [**GUI Design**](../architecture/gui_modernization_design.md) | [**Registry Design**](../architecture/unified_registry_and_node_graph.md))
**Goal**: Transition to a metadata-driven, modular architecture with synchronized selection and registry discovery.

*   **Milestone 12.1**: Base Frameworks (`BaseUIWindow`, `WindowManager`, `SelectionService`).
*   **Milestone 12.2**: Registry V2 Implementation (Metadata decorators & category discovery).
*   **Milestone 12.3**: GUI Event Bus (Decoupled synchronization between Registry, Selection, and Windows).
*   **Milestone 12.4**: Porting Core Windows (Outliner, Inspector using new Selection API).

## Phase 13: Visual Graph Editors ([**Guide**](../guides/phases/phase_13_graph_editors.md) | [**Brain Editor**](../architecture/behavior_tree_editor.md) | [**Graph Framework**](../architecture/unified_registry_and_node_graph.md))
**Goal**: Enable no-code design and real-time visualization of agent logic and data pipelines.

*   **Milestone 13.1**: Base Node Graph Manager ([**Unified Registry**](../architecture/unified_registry_and_node_graph.md)).
*   **Milestone 13.2**: Behavior Tree Canvas ([**BT Editor Design**](../architecture/behavior_tree_editor.md)).
*   **Milestone 13.3**: Live Execution Overlay (Real-time node status colors: Success/Fail/Run).
*   **Milestone 13.4**: Node Library Sidebar (Attribute-based registration via `@register_node`).
*   **Milestone 13.5**: Inspector Integration ([**Selection Sync**](../architecture/unified_registry_and_node_graph.md#2-global-selection-service) & [**AutoUI**](../architecture/auto_ui_builder.md)).
*   **Milestone 13.6**: Blackboard Monitor & Editor (Real-time agent memory manipulation).
*   **Milestone 13.7**: [**Perception Pipeline Editor**](../architecture/perception_pipeline_editor.md) (DAG visualization with preview pins).

## Phase 14: Analytics & Swarm Monitoring ([**Guide**](../guides/phases/phase_14_analytics.md))
**Goal**: Add deep inspection tools for multi-agent dynamics and model performance.

*   **Milestone 14.1**: **Global Swarm Roster** (Table with CPU/Status/Current Task).
*   **Milestone 14.2**: **Action Execution Timeline** (Gantt-like view of agent intents).
*   **Milestone 14.3**: **Imitation Learning Loss Monitor** (Real-time diff in Shadow Mode).
### Phase 15: Framework Consolidation & Structural Refinement
**Goal**: Unified orchestration and architectural debt reduction.
- [ ] **Data-Driven Cockpit**: Refactor `main.py` to use `RegistryV2` metadata for system discovery.
- [ ] **Unified Command Stream**: Implementation of the "Observation -> Intent -> Command" pipeline.
- [ ] **Generic Node Canvas**: Multi-purpose DPG base class for all node graph tools.
- [ ] **Snapshot-as-a-Service**: Core `World` trait for state serialization and time-travel.
