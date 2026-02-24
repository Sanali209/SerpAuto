# Serpentine Engine: Remediation & Implementation Plan

This document outlines the step-by-step roadmap to resolve the discrepancies identified in the `SENIOR_ARCHITECT_REPORT.md` and implement the "Standard Universal System" features.

## Phase 1: Foundation & Cleanup (P0)

**Goal:** Establish a single source of truth for documentation and ensure language compliance.

### 1.1. Create Core Architecture Artifacts
*   [ ] **Task:** Create `des_docs/ARCHITECTURE.md`.
    *   *Content:* High-level diagrams of the ECS Loop, System Layers (Core, Body, Mind), and Dependency Graph. Consolidate info from `engine_overview.md`.
*   [ ] **Task:** Create `des_docs/DATA_FLOW.md`.
    *   *Content:* Step-by-step trace of data from `PerceptionComponent` -> `BrainComponent` -> `ActionBufferComponent` -> `ExecutionSystem`.
*   [ ] **Task:** Create `des_docs/GLOSSARY.md`.
    *   *Content:* Definitions for: Entity, Component, System, Node (BT vs Pipeline), Agent, Bot, Tick, Frame.

### 1.2. Documentation Standardization
*   [ ] **Task:** Translate `des_docs/architecture/engine_overview.md` to English.
*   [ ] **Task:** Translate `des_docs/modes/*.md` files to English.
*   [ ] **Task:** Remove or update outdated references to "InternalRenderSystem" to clarify it refers to the DearPyGui debug view.

---

## Phase 2: Synchronization & Core Features (P1)

**Goal:** Align the codebase with the documentation promises and implement missing core logic.

### 2.1. Behavior Tree Standard Library (Universalization)
*   [ ] **Task:** Implement **Decorator Nodes** in `brain/nodes.py`.
    *   `Inverter`: Returns `!child_status`.
    *   `Succeeder`: Always returns `SUCCESS`.
    *   `RepeatUntilFail`: Loops child until `FAILURE`.
*   [ ] **Task:** Implement **Blackboard Logic Nodes** in `brain/nodes.py`.
    *   `CheckBlackboardVariable(key, operator, value)`: Returns `SUCCESS` if condition met.
    *   `SetBlackboardVariable(key, value)`: Sets data.
*   [ ] **Task:** Implement **Control Flow Nodes** in `brain/behavior_tree.py`.
    *   `Parallel(policy)`: Runs children concurrently (pseudo-parallel in async loop).
*   [ ] **Task:** Implement **Utility Nodes** in `brain/nodes.py`.
    *   `WaitNode(seconds)`: Returns `RUNNING` until time elapses.

### 2.2. Perception Gaps
*   [ ] **Task:** Implement `OCRNode` in `perception/cv_nodes.py`.
    *   *Implementation:* Wrapper around `pytesseract` or `docling`.
*   [ ] **Task:** Implement `GridMapperNode` in `perception/internal_nodes.py`.
    *   *Implementation:* Logic to convert Entity transforms + Collider bounds into a 2D `numpy` occupancy grid.

### 2.3. Gym Integration Fix
*   [ ] **Task:** Refactor `core/env_wrapper.py`.
    *   Remove hardcoded `(64,64,3)` observation space.
    *   Implement dynamic observation extraction from `PerceptionComponent.raw_context`.
    *   Inject `ActionAdapter` to decouple Snake logic from the generic wrapper.

---

## Phase 3: Professionalization (P2)

**Goal:** Improve Developer Experience (DX) and code maintainability.

### 3.1. Code Documentation
*   [ ] **Task:** Audit `core/` and `systems/` files.
*   [ ] **Task:** Add NumPy-style docstrings to all `System` classes and `Component` models.

### 3.2. Guide Creation
*   [ ] **Task:** Create `des_docs/guides/BEHAVIOR_TREE_GUIDE.md`.
    *   *Content:* Explanation of `tick()` lifecycle, `Status` enum, and how to write async nodes without race conditions.

---

## Phase 4: Advanced Tooling (P3)

**Goal:** Solve the "Invisible Engine" problem.

### 4.1. Behavior Tree Visualizer
*   [ ] **Task:** Create `systems/gui_bt.py`.
*   [ ] **Task:** Implement `BTVisualizerSystem`.
    *   *Logic:* Use `dpg.add_node_editor`. Traverse `BrainComponent.bt_root`. Create visual nodes. Highlight active path (green border for `SUCCESS`, yellow for `RUNNING`).

### 4.2. Action Timeline
*   [ ] **Task:** Update `ActionExecutionSystem` to log execution events to a ring buffer.
*   [ ] **Task:** Create a GUI panel in `systems/gui.py` to render this timeline as a horizontal gantt-chart like view.

---

*Plan generated based on Senior Architect Report v1.0*
