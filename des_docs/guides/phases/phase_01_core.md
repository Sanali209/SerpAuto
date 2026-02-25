# Phase 1: Core Engine & ECS Architecture Guide

This guide details the foundational ECS architecture of the Serpentine Engine.

## 1. Objectives
- **Core ECS**: Establish `World`, `Entity`, and `BaseComponent`.
- **Async Loop**: Implement a non-blocking engine heart using `asyncio`.
- **Optimization**: Reactive query caching for high-performance entity filtering.

## 2. Technical Prerequisites & Architecture
- [**Engine Overview**](../../architecture/engine_overview.md)
- [**ECS Hierarchy Implementation**](../../architecture/ecs_hierarchy_impl.md)
- [**Component Reference**](../../architecture/COMPONENT_REFERENCE.md)

## 3. Implementation Status

### 1.1 Core Data Structures
- [ ] **Entity**: UUID wrapper for unique identification.
- [ ] **BaseComponent**: Pydantic-based data models.
- [ ] **World**: Central storage for entities and components.
- [ ] **Query Engine**: Efficient set-intersection based filtering (`get_entities_with`).

### 🛠️ Web Insights & Advanced Patterns
> [!TIP]
> **Data Locality in Python**: While Python objects are scattered in memory, storing component data in **NumPy arrays** for high-frequency systems (like Physics) can lead to 30x speedups via vectorization.
> - **Archetypes**: Group entities with identical component sets to minimize "holes" in data arrays and improve CPU cache hits.
> - **Pure Data**: Keep components as logic-less data classes. Use **Cython** for performance-critical systems to bridge the gap with C-level execution speeds.

### 🔄 Consolidation Hook: Event-Driven Orchestration
- **Goal**: Transition from static system list to a dynamic, `@register_system` based discovery.
- **Action**: All core components and systems must be registered via `RegistryV2` to enable dynamic orchestration and meta-data driven discovery.

### 1.2 System Architecture
- [ ] **System Base**: Abstract class with `update(world, dt)`.
- [ ] **Async Loop**: Tick-based execution in `SerpentineEngine`.
- [ ] **Tick Limiter**: Configurable TPS and sleep logic.

### 1.3 Standard Components
- [ ] **TransformComponent**: Position, rotation, and parent/child hierarchy.
- [ ] **StatsComponent**: Generic health/stamina tracking.
- [ ] **SpatialGridComponent**: (Pending) Broad-phase collision optimization.

## 4. Backlog Management
- **Input**: Read the primary task list from [tasks.md](../../planning/tasks.md).
- **Output**: Save remaining core tasks and technical debt to: `des_docs/planning/backlogs/phase_01_backlog.md`.

## 5. Code Quality & Decomposition
- **File Length Limit**: Individual files **must not exceed 500 lines**.
- **Decomposition**: If a file grows beyond 500 lines, split it into smaller modules (e.g., `logic.py`, `types.py`, `utils.py`) within a package.
- **Complexity**: Prefer descriptive function names and typed hints to reduce comments.

## 6. Quality Assurance & Testing
- **Automated Tests**: Run `pytest tests/test_core_ecs.py` to ensure core stability.
- **Regression Check**: Monitor `dt` consistency in the engine loop; tick variance must remain < 5ms under load (10k entities).

## 6. Phase Completion Criteria
- [ ] `World` handles 10k entities at 60 FPS.
- [ ] `get_entities_with` query time is < 1ms for cached queries.
- [ ] All systems are correctly decorated with `@register_system`.

## 7. Execution Logging & Monitoring
- **Logs**: Track `Entity` creation/destruction in `serpentine.log` at the `DEBUG` level.
- **Metrics**: Monitor `SerpentineEngine.actual_tps` via the Telemetry system.

## 8. Developer Experience (DX)
- **MCP Servers**: Use the `sequential-thinking` MCP server to plan complex ECS hierarchy changes. Utilize `memory` MCP (if available) to track entity relationships during design.
