# Phase 10: Scene Management Guide

This guide covers the dynamic world management and project resource structures.

## 1. Objectives
- **Dynamic Registry**: Decorator-based discovery for all engine types.
- **Scene Serialization**: JSON-based project files.
- **Resource Management**: Dynamic loading of blueprints and world settings.

## 2. Technical Prerequisites & Architecture
- [**Unified Registry Design**](../../architecture/unified_registry_and_node_graph.md)

## 3. Implementation Status

### 10.1 Registry Architecture
- [ ] **@register_component**: Automatic bitmasking and factory setup.
- [ ] **@register_system**: Phase-based ordering and discovery.

### 10.2 Scene Loader
- [ ] **Scene JSON**: Definitions of systems, entities, and global configs.
- [ ] **SceneManager**: Orchestrator- [ ] **Transition**: Serializer-backed scene switching.

### 🛠️ Web Insights & Advanced Patterns
> [!NOTE]
> **Snapshot Layering**: Use "Delta Serialization" for scene transitions. Instead of saving the entire state, only save the changes (deltas) relative to the template. This makes scene loading instantaneous and reduces disk footprint for large worlds.
> - **Frustum Culling**: Even for 2D/pseudo-2D engine work, skip updating entities that are outside the current "Scene Viewport" to save CPU cycles for active agents.

### 🔄 Consolidation Hook: Blueprint Standardization
- **Goal**: Use Scene Files as the primary specification for environment and agent archetypes.
- **Action**: Ensure `RegistryV2` can hydrate an entire world (systems and entities) from a single consolidated JSON schema (Blueprints V2).

## 4. Backlog Management
- **Input**: Read the pending tasks from the Phase 9 backlog: `des_docs/planning/backlogs/phase_09_backlog.md`.
- **Output**: Save remaining scene/blueprint tasks and technical debt to: `des_docs/planning/backlogs/phase_10_backlog.md`.

## 5. Code Quality & Decomposition
- **File Length Limit**: Individual files **must not exceed 500 lines**.
- **Decomposition**: Break `SceneManager` into `loader.py`, `saver.py`, and `validator.py`.
- **Complexity**: Keep JSON schemas in external `.json` files to avoid embedding large strings in Python modules.

## 6. Quality Assurance & Testing
- **Automated Tests**: Run `pytest tests/test_scene_loading.py`.
- **Regression Check**: Ensure that adding new components via decorators does not increase scene parsing time linearly.

## 6. Phase Completion Criteria
- [ ] `SceneManager` loads 1000 entities from JSON in < 500ms.
- [ ] `@register_system` maintains deterministic execution order across reloads.
- [ ] Component bitmasks are generated correctly for all registered types.

## 7. Execution Logging & Monitoring
- **Logs**: Log all registered types and scene load events in `registry.log`.
- **Metrics**: Monitor time spent in `World.serialize/deserialize`.

## 8. Developer Experience (DX)
- **MCP Servers**: Use `filesystem` MCP to validate scene JSON schemas. Use `sequential-thinking` MCP to plan complex world transitions.
