# Phase X: [Phase Name] Guide

This guide details the architecture, implementation steps, and completion criteria for the **[Phase Name]** of the Serpentine Engine.

## 1. Objectives
*   **Goal 1**: Brief description.
*   **Goal 2**: Brief description.
*   **Goal 3**: Brief description.

## 2. Technical Prerequisites & Architecture
*   [**Related Architecture Doc**](../../architecture/filename.md)
*   [**Component Reference**](../../architecture/COMPONENT_REFERENCE.md)

## 3. Implementation Plan

### 3.1. Core Components
*   [ ] **Component Name**: Description of data fields (Pydantic).
*   [ ] **System Name**: Description of logic and phase.

### 3.2. Integration Steps
1.  **Step 1**: Describe the action.
2.  **Step 2**: Describe the action.

### 🔄 Consolidation Hook: [Strategy Name]
> Describe how this phase aligns with the broader consolidation strategy (e.g., Registry V2, Unified Dataflow).

## 4. Backlog Management
*   **Input**: Read tasks from [tasks.md](../../planning/tasks.md).
*   **Output**: Move unfinished items to `des_docs/planning/backlogs/phase_X_backlog.md`.

## 5. Code Quality & Standards
*   **File Limits**: Ensure files stay under 500 lines.
*   **Typing**: Strict `mypy` compliance.
*   **Testing**: Unit tests must cover >80% of new logic.

## 6. Phase Completion Criteria
- [ ] Feature A works as expected.
- [ ] Feature B is documented.
- [ ] Performance metric X is met.

## 7. Developer Experience (DX)
*   **Logging**: Use `logger.bind(phase=X)` for traceability.
*   **Tooling**: Mention specific CLI commands or debug views useful for this phase.
