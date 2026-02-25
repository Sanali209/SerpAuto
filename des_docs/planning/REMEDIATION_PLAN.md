# Serpentine Engine: Remediation & Implementation Plan

This document outlines the step-by-step roadmap to resolve the discrepancies identified in the `SENIOR_ARCHITECT_REPORT.md` and implement the "Standard Universal System" features.

## Phase 1: Foundation & Cleanup (P0)

**Goal:** Establish a single source of truth for documentation and ensure language compliance.

### 1.1. Create Core Architecture Artifacts
*   [x] **Task:** Create `des_docs/ARCHITECTURE.md`.
*   [x] **Task:** Create `des_docs/DATA_FLOW.md`.
*   [x] **Task:** Create `des_docs/GLOSSARY.md`.

### 1.2. Documentation Standardization
*   [ ] **Task:** Translate `des_docs/architecture/engine_overview.md` to English.
*   [x] **Task:** Translate `des_docs/modes/*.md` files to English.
*   [ ] **Task:** Remove or update outdated references to "InternalRenderSystem".

---

## Phase 2: Synchronization & Core Features (P1)

**Goal:** Align the codebase with the documentation promises and implement missing core logic.

### 2.1. Behavior Tree Standard Library (Universalization)
*   [ ] **Task:** Implement **Decorator Nodes** in `brain/nodes.py`.
*   [ ] **Task:** Implement **Blackboard Logic Nodes** in `brain/nodes.py`.
*   [ ] **Task:** Implement **Control Flow Nodes** in `brain/behavior_tree.py`.
*   [ ] **Task:** Implement **Utility Nodes** (WaitNode).

### 2.2. Perception Gaps
*   [ ] **Task:** Implement `OCRNode` in `perception/cv_nodes.py`.
*   [ ] **Task:** Implement `GridMapperNode` in `perception/internal_nodes.py`.

### 2.3. Gym Integration Fix
*   [ ] **Task:** Refactor `core/env_wrapper.py`. Remove hardcoded `(64,64,3)`.

---

## Phase 3: Professionalization (P2)
...
*Plan generated based on Senior Architect Report v1.0*
