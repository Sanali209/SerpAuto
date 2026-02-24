# Serpentine Engine Roadmap

This roadmap outlines the strategic development phases for the Serpentine Engine, transitioning from a basic ECS framework to a full-scale Multi-Agent System (MAS) with cognitive capabilities.

## Phase 1: Core Engine & ECS Architecture (Foundation)
**Goal**: Establish a robust, high-performance Entity-Component-System framework capable of handling thousands of entities at 60+ TPS.

*   **Milestone 1.1**: Core Data Structures (`World`, `Entity`, `BaseComponent`).
*   **Milestone 1.2**: System Update Loop (`SerpentineEngine` with `asyncio`).
*   **Milestone 1.3**: Query Caching & Optimization (Set Intersection Logic).
*   **Milestone 1.4**: Standard Component Library (Memory, Transform, Stats).

## Phase 2: The Body (Perception & Action Pipelines)
**Goal**: Enable agents to sense the environment and execute physical actions.

*   **Milestone 2.1**: Ingestion Phase (`SensoryInputSystem`, Screen Capture).
*   **Milestone 2.2**: Perception Pipeline (`PerceptionPipelineSystem`, DAG Nodes).
*   **Milestone 2.3**: Basic CV Nodes (Crop, Grayscale, Template Matching).
*   **Milestone 2.4**: Action Execution (`ActionExecutionSystem`, Buffer Queue).

## Phase 3: The Mind (Cognitive System)
**Goal**: Integrate decision-making capabilities using Behavior Trees and LLMs.

*   **Milestone 3.1**: Behavior Tree Engine (Selector, Sequence, Decorators).
*   **Milestone 3.2**: Blackboard Integration (`MemoryComponent`).
*   **Milestone 3.3**: AI Adapter Interface (`BaseAIAdapter`, Context Builder).
*   **Milestone 3.4**: LLM Inference Node (Async Integration).

## Phase 4: The Swarm (Multi-Agent System)
**Goal**: Scale from single-agent logic to coordinated multi-agent operations.

*   **Milestone 4.1**: Agent Identity & Metadata (`AgentMetaComponent`).
*   **Milestone 4.2**: Pub/Sub Communication Architecture (`MailboxComponent`).
*   **Milestone 4.3**: Message Router System (Event Bus Orchestrator).
*   **Milestone 4.4**: Swarm Logic Nodes (`SendMessage`, `ListenForEvent`).

## Phase 5: God Mode (UI & Developer Tools)
**Goal**: Create a massive Docking Space "Control Center" for surgical debugging of ECS architecture and Multi-Agent Swarms.

*   [x] **Milestone 5.1**: DearPyGui Core Workspace (Docking Layout, Control Deck, Time Travel).
*   [x] **Milestone 5.2**: World Outliner (Entity Manager with CRUD operations).
*   [x] **Milestone 5.3**: Component Inspector (Zero-Code UI via Pydantic parsing & Data Binding).
*   [x] **Milestone 5.4**: Perception Monitor (GPU Textures, JSON Tree, Debug Overlays).
*   **Milestone 5.5**: Brain & Memory Editor (Blackboard Editor, Prompt Preview, Episodic Log).
*   **Milestone 5.6**: Actions & Swarm Visualizers (Intervention Queue, BT Tracer, Data Sniffer).

## Phase 6: Environment & Simulation (Advanced Features)
**Goal**: Support hybrid environments (External OS + Internal Sim) and MLOps workflows.

*   **Milestone 6.1**: Internal Physics & Rendering Systems.
*   **Milestone 6.2**: Environment Routing (`Direct Perception Bypass`).
*   **Milestone 6.3**: MLOps Pipeline Integration (YOLO, ONNX Runtime).
*   **Milestone 6.4**: Dataset Collection Tools (`Teacher Mode`).

## Phase 7: Persistence & Deployment (DevOps)
**Goal**: Enable saving/loading of agent brains, world states, and tool layouts for seamless debugging ("Time Travel").

*   **Milestone 7.1**: World State Serialization & Snapshots (JSON dumps).
*   **Milestone 7.2**: Project Configuration (Save/Load Blueprints for Pipeline/BT).
*   **Milestone 7.3**: UI Layout Persistence (`dpg.save_init_file`).
*   **Milestone 7.4**: Time Travel & Hot-Reload Logic (Pause, Load Snapshot, Resume).

## Phase 8: Operation Modes (Lifecycle)
**Goal**: Configure the engine for specific use cases (Debug, Deploy, Train).

*   **Milestone 8.1**: Architect Mode (GUI + Debug Systems) [x].
*   **Milestone 8.2**: Production Mode (Headless + Telemetry + FastAPI) [x].
*   **Milestone 8.3**: Teacher Mode (Human Input + Dataset Logging) [x].
*   **Milestone 8.4**: Gymnasium Mode (Internal Physics + Rewards + Uncapped Speed) [x].
*   **Milestone 8.5**: Continuous Learning Mode (Actor-Learner split, Async I/O, Hot-Swapping) [x].

## Phase 9: Sample Project (Snake AI)
**Goal**: Demonstrate the full cycle of engine capabilities with a complete internal simulation and RL training loop.

*   [x] **Milestone 9.1**: Internal Snake Simulation (Locomotion & Collision Systems).
*   [x] **Milestone 9.2**: Agent Perception (Grid State Node) & Action Mapping.
*   [x] **Milestone 9.3**: RL Training Loop Integration (Gymnasium).
*   [x] **Milestone 9.4**: Architect Mode Visual Debugging.

## Phase 10: Scene Management & Dynamic Loading
**Goal**: Create a Unity-like experience for managing scenes, systems, and entities dynamically.

*   [x] **Milestone 10.1**: Global Registries with Decorators (`@register_component/system`).
*   [x] **Milestone 10.2**: Scene File Format & Manager (Save/Load Scene).
*   [x] **Milestone 10.3**: CLI Entry Point (`main.py`) for Headless loading.
*   [x] **Milestone 10.4**: Integration with `SerpentineEngineV2` (Dynamic System Injection).

## Phase 11: Play Mode (ModernGL Rendering)
**Goal**: Transition from a debug-only UI to a high-performance 3D/2D game rendering environment.

*   [x] **Milestone 11.1**: ModernGL Render Pipeline (Shaders, Meshes, FBO).
*   [x] **Milestone 11.2**: Play In Editor (PIE) Architecture.
*   [x] **Milestone 11.3**: Player Input System (Hardware Input Bridge).
*   [x] **Milestone 11.4**: Possession System (Human <-> AI Control Swapping).
*   [ ] **Milestone 11.5**: Camera Raycasting & 3D World Interaction.
