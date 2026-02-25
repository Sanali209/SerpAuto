# Phase 12: Integrated Core Modernization Guide

This guide provides autonomous instructions for implementing the Integrated Core Modernization phase, focusing on a metadata-driven architecture, a global selection system, and a modular UI.

## 1. Objectives
- **Registry V2**: Transition from a simple class map to a metadata-rich discovery service.
- **Selection Service**: Implement a centralized system to synchronize user focus across all UI panels.
- **GUIDebugSystem Refactor**: Decompose the monolithic GUI into a class-based package.

## 2. Technical Prerequisites & References
- [**Modernized Debug UI Architecture**](../../architecture/gui_modernization_design.md)
- [**Unified Registry & Node Graph Architecture**](../../architecture/unified_registry_and_node_graph.md)
- [**Auto UI Builder Guide**](../../architecture/auto_ui_builder.md)

## 3. Implementation Steps

### 12.1 Core Foundations
1.  **Registry V2 (`core/registry_v2.py`)**:
    - Implement a `RegistryMeta` data class to hold icon, category, and description.
    - Create `@register_node` and `@register_system` decorators that populate the registry with this metadata.
    - Add methods to filter registry items by category (e.g., `get_nodes_by_category("Logic")`).
2.  **Selection Service (`core/selection.py`)**:
    - Build a singleton `SelectionService` that stores `selected_entity_id`, `selected_node_id`, and `selected_component_type`.
    - Integrate with `GUIEventBus` to emit events like `ON_SELECTION_CHANGED`.
3.  **Grid Layouts**: Apply **DearPyGui-Grid** for the new modular window system to ensure structural consistency and responsive resizing.

### 12.2 GUI Modularization (`systems/gui/`)
1.  **Base Framework**:
    - Create `base.py` with the `BaseUIWindow` abstract class (hooks: `render()`, `update()`).
    - Create `manager.py` with `WindowManager` to handle DPG window registration and visibility.
2.  **Window Migration**:
    - **Outliner**: Move entity tree logic to `systems/gui/windows/outliner.py`. Call `SelectionService.set_entity()` on click.
    - **Inspector**: Move auto-generating UI logic to `systems/gui/windows/inspector.py`. Listen for `ON_SELECTION_CHANGED` and refresh content.
  - [ ] **Skeleton Loaders**: (Pending) Perceived performance during layout parsing.

### 🛠️ Web Insights & Advanced Patterns
> [!TIP]
> **Bento-Style UI**: Modern developer tools (like Vercel or Linear) utilize "Bento Grids"—high-contrast cards with rounded corners and subtle shadows—to organize dense information without clutter.
> - **Glassmorphism**: Use `dpg.add_texture_registry` to create frosted-glass backgrounds for overlay menus (e.g., God Mode commands) to provide depth and "premium" aesthetics.
> - **Skeleton States**: Implement "ghost" UI placeholders during async registry loading to eliminate jumping layouts and reduce perceived latency for the user.

### 🔄 Consolidation Hook: Event-Driven Orchestration
- **Goal**: Finalize the migration to a metadata-driven orchestration model.
- **Action**: Decommission the legacy monolithic `GUIDebugSystem` and replace it with modular windows discovered via `RegistryV2`.

## 4. Backlog Management
- **Input**: Read the pending tasks from the Phase 11 backlog: `des_docs/planning/backlogs/phase_11_backlog.md`.
- **Output**: Save remaining modernization tasks and technical debt to: `des_docs/planning/backlogs/phase_12_backlog.md`.

## 5. Code Quality & Decomposition
- **File Length Limit**: Individual files **must not exceed 500 lines**.
- **Decomposition**: Modularize the `RegistryV2` into decorator scanning, metadata storage, and query logic files.
- **Complexity**: Avoid deep inheritance in UI window classes; use composition for window feature sets.

## 6. Quality Assurance & Testing
- **Automated Tests**: Run `pytest tests/test_registry_v2.py`.
- **Regression Check**: Verify that `SelectionService` events do not trigger redundant UI redraws (event debouncing).

## 6. Phase Completion Criteria
- [ ] `RegistryV2` correctly categorizes 100% of existing nodes.
- [ ] `SelectionService` broadcasts changes to all active windows.
- [ ] `WindowManager` handles window stacking and persistence without flickering.

## 7. Execution Logging & Monitoring
- **Logs**: Record registry discovery events and UI event bus traffic in `modernization.log` via **Loguru**.
- **Metrics**: Track UI event latency (selection-to-draw) and display via **Rich.LiveData** in the terminal during development.

## 9. Developer Experience (DX) & Tooling
- **Logging**: Use **Loguru** for structured, traceable events.
- **Terminal UI**: Use **Rich** for status tables and **Typer** for CLI arguments.
- **Static Analysis**: Enforce quality with **Ruff** (lint/format) and **Mypy** (types).
- **Perception Debug**: Use **visual-logging** for CV/ingestion node audits.
- **UI Layout**: Use **DearPyGui-Grid** for maintainable DPG window structures.
- **MCP Servers**:
    - `sequential-thinking`: Plan migration of complex legacy windows.
    - `filesystem`: Audit the new modular directory structure.
