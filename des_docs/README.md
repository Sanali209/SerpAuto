# Serpentine Engine - Design Documentation

Welcome to the internal design documentation for the Serpentine Engine. This folder contains the technical specifications and architectural blueprints for the project.

> [!IMPORTANT]
> **[Architecture Overview](ARCHITECTURE.md)** | **[Engine Overview](architecture/engine_overview.md)** | **[Component Reference](architecture/COMPONENT_REFERENCE.md)** | **[Data Flow](DATA_FLOW.md)** | **[Glossary](GLOSSARY.md)**

## 🗺️ Planning & Roadmap
*   [**Roadmap**](planning/roadmap.md): Strategic development phases.
*   [**Task List**](planning/tasks.md): Granular execution items.
*   [**Future Research**](planning/future_research.md): Deep-dive goals for the next stage of development.
*   [**Use Cases**](planning/use_cases.md): Industrial and game development scenarios.

## 🛠️ Implementation Guides
*   [**Phase 01: Core ECS**](guides/phases/phase_01_core.md)
*   [**Phase 02: Perception & Action**](guides/phases/phase_02_perception.md)
*   [**Phase 03: Cognitive Mind**](guides/phases/phase_03_mind.md)
*   [**Phase 04: Swarm Intelligence**](guides/phases/phase_04_swarm.md)
*   [**Phase 05: Developer UI**](guides/phases/phase_05_god_mode.md)
*   [**Phase 06: Simulation Layer**](guides/phases/phase_06_simulation.md)
*   [**Phase 07: Persistence System**](guides/phases/phase_07_persistence.md)
*   [**Phase 08: Operation Modes**](guides/phases/phase_08_modes.md)
*   [**Phase 09: Snake AI Demo**](guides/phases/phase_09_snake_demo.md)
*   [**Phase 10: Scene Management**](guides/phases/phase_10_scenes.md)
*   [**Phase 11: ModernGL Rendering**](guides/phases/phase_11_rendering.md)
*   [**Phase 12: Core Modernization**](guides/phases/phase_12_modernization.md)
*   [**Phase 13: Visual Graph Editors**](guides/phases/phase_13_graph_editors.md)
*   [**Phase 14: Analytics & Monitoring**](guides/phases/phase_14_analytics.md)
*   [**Framework Consolidation Strategy**](planning/consolidation_strategy.md)

## 🏗️ Core Architecture
*   [**Engine Overview**](architecture/engine_overview.md): The main design document (ECS, Loop, Perception).
*   [**Component Reference**](architecture/COMPONENT_REFERENCE.md): Detailed catalog of all ECS components.
*   [**Persistence System**](architecture/persistence_system.md): World snapshots and blueprints (Time Travel).
*   [**Auto UI Builder**](architecture/auto_ui_builder.md): Dynamic GUI generation from Pydantic.
*   [**ECS Hierarchy (Implementation)**](architecture/ecs_hierarchy_impl.md): Data-driven parent-child relationships.
*   [**ECS Hierarchy (GUI/Editor)**](architecture/ecs_hierarchy_gui.md): Visualizing and managing hierarchy in DearPyGui.
*   [**Game ECS Library**](architecture/game_ecs_library.md): Standard components and systems for simulations.
*   [**GUI Layout Design**](architecture/gui_layout_design.md): Docking space and module definitions.
*   [**Modernized Debug UI**](architecture/gui_modernization_design.md): Modular package architecture.
*   [**Unified Registry & Selection**](architecture/unified_registry_and_node_graph.md): Metadata and node graph foundations.
*   [**Behavior Tree Visual Editor**](architecture/behavior_tree_editor.md): Detailed brain editor features.

## 🕹️ Operation Modes
*   [**Architect Mode**](modes/architect_mode.md): Developer GUI and World Outliner.
*   [**Production Mode**](modes/production_mode.md): Headless operations and FastAPI integration.
*   [**Play Mode**](modes/play_mode.md): ModernGL rendering and human-in-the-loop control.
*   [**Teacher Mode**](modes/teacher_mode.md): Imitation learning and dataset collection.
*   [**Gymnasium Mode**](modes/gym_mode.md): Reinforcement learning and fast-forward simulations.
*   [**Actor-Learner Mode**](modes/actor_learner.md): Continuous online learning with I/O handling.

## 🧠 Brain & ML integration
*   [**ML Integration Insights**](api_ml/ml_integration_insights.md): Advanced notes on model versioning and hotswapping.

## 📚 Guides
*   [**Behavior Tree Guide**](guides/BEHAVIOR_TREE_GUIDE.md): How to design and implement agent logic.
*   [**Offline Development Guide**](guides/offline_dev_guide.md): Working in air-gapped environments.
*   [**Testing Strategy**](guides/testing_strategy.md): Unit testing ECS systems and Behavior Trees.
*   [**System Implementation Guide**](guides/system_implementation_guide.md): Creating and optimizing new ECS Systems.
*   [**Contribution Guidelines**](../CONTRIBUTING.md): Git workflow and code standards.

---
*See [**dev_docs_rules.md**](dev_docs_rules.md) for documentation standards.*
