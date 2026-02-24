# Serpentine Engine - Design Documentation

Welcome to the internal design documentation for the Serpentine Engine. This folder contains the technical specifications and architectural blueprints for the project.

> [!IMPORTANT]
> **[Main Design Document](architecture/engine_overview.md)**: Start here for the high-level engine architecture and core systems.

## 🗺️ Planning & Progress
*   [**Roadmap**](planning/roadmap.md): Strategic development phases and milestones.
*   [**Detailed Task List**](planning/tasks.md): Granular task breakdown and P0-P3 priorities.
*   [**Future Research**](planning/future_research.md): Deep-dive goals for the next stage of development.
*   [**Use Cases**](planning/use_cases.md): Industrial and game development scenarios.

## 🏗️ Core Architecture
*   [**Engine Overview**](architecture/engine_overview.md): The main design document (ECS, Loop, Perception).
*   [**ECS Hierarchy (Implementation)**](architecture/ecs_hierarchy_impl.md): Data-driven parent-child relationships.
*   [**ECS Hierarchy (GUI/Editor)**](architecture/ecs_hierarchy_gui.md): Visualizing and managing hierarchy in DearPyGui.
*   [**Game ECS Library**](architecture/game_ecs_library.md): Standard components and systems for simulations.
*   [**GUI Layout Design**](architecture/gui_layout_design.md): Docking space and module definitions.

## 🕹️ Operation Modes
*   [**Play Mode**](modes/play_mode.md): ModernGL rendering and human-in-the-loop control.
*   [**Teacher Mode**](modes/teacher_mode.md): Imitation learning and dataset collection.
*   [**Gymnasium Mode**](modes/gym_mode.md): Reinforcement learning and fast-forward simulations.
*   [**Actor-Learner Mode**](modes/actor_learner.md): Continuous online learning with I/O handling.

## 🧠 Brain & ML integration
*   [**ML Integration Insights**](api_ml/ml_integration_insights.md): Advanced notes on model versioning and hotswapping.

---
*See [**dev_docs_rules.md**](dev_docs_rules.md) for documentation standards.*
