# Phase 11: Play Mode (ModernGL Rendering) Guide

This guide covers the completion of the high-performance rendering pipeline and the "Play In Editor" (PIE) feature.

## 1. Objectives
- **ModernGL Pipeline**: Finalize the shader-based 2D/3D rendering system.
- **Stability Fix**: Resolve the Segmentation Fault caused by OpenGL context/thread conflicts.
- **Interaction**: Implement Camera Raycasting for selecting objects in the 3D viewport.

## 2. Technical Prerequisites & References
- [**ModernGL Integration Design**](../../architecture/engine_overview.md#phase-11-play-mode)
- [**Component Reference: Rendering**](../../architecture/COMPONENT_REFERENCE.md)

## 3. Implementation Steps

### 11.1 Stability & Context Management
1.  **Thread Safety**: Ensure all ModernGL calls happen on the main thread or within a dedicated render thread with a shared context.
2.  **Context Cleanup**: Implement robust destruction logic for the ModernGL context to prevent segmentation faults on app close.

### 11.2 Camera Raycasting (`systems/render/raycast.py`)
1.  **Unprojecting**: Implement logic to transform mouse screenspace coordinates (from DPG click) into worldspace vectors using the Camera's View-Projection matrix.
2.  **Intersection**:
    - For 2D: Simple AABB/Circle checks.
    - For 3D: Implement Ray-Sphere or Ray-Box intersection tests against `ColliderComponent` data.

### 11.3 Possession System
1.  **Body Swapping**:
    - Implement a `PossessionSystem` that can reassign the `HumanInputSystem` target to any entity with an `ActionBufferComponent`.
    - [ ] **Shader Library**: Modular GLSL loading system.

### 🛠️ Web Insights & Advanced Patterns
> [!IMPORTANT]
> **Thread-Safe Rendering**: OpenGL contexts are single-threaded. Always use a dedicated **Render Thread** and communicate via a synchronized command queue to avoid segmentation faults.
> - **Context GC**: Set `gc_mode="context_gc"` in ModernGL to ensure that resources are only deleted on the thread where the context is current, preventing race conditions with Python's garbage collector.

### 🔄 Consolidation Hook: Plugin Architecture (Render Commands)
- **Goal**: Standardize communication with the dedicated render thread using the engine's core bus.
- **Action**: Use the `UnifiedEngineEventBus` to push render state updates, ensuring thread safety via the consumer-producer pattern and decoupling rendering from the main simulation tick.

## 4. Verification Plan
- **Stress Test**: Run the renderer for 10 minutes and verify no segmentation faults occur.
- **Raycast Test**: Click a moving entity in the viewport and verify it becomes selected in the Outliner.
- **Performance**: Ensure the ModernGL context maintains 60+ FPS even with 100+ rendered sprites.

## 4. Backlog Management
- **Input**: Read the pending tasks from the Phase 10 backlog: `des_docs/planning/backlogs/phase_10_backlog.md`.
- **Output**: Save remaining rendering/PIE tasks and technical debt to: `des_docs/planning/backlogs/phase_11_backlog.md`.

## 5. Code Quality & Decomposition
- **File Length Limit**: Individual files **must not exceed 500 lines**.
- **Decomposition**: Move GLSL shader text to standalone files; keep GL context management logic separate from draw loop logic.
- **Complexity**: Use descriptive vertex attributes names to reduce inline shader comments.

## 6. Quality Assurance & Testing
- **Manual Verification**: Verify that FPS remains stable at 60 while moving the camera.
- **Regression Check**: Monitor VRAM usage; ensure no texture leaks during scene transitions.

## 6. Phase Completion Criteria
- [ ] ModernGL context launches and closes without segmentation faults.
- [ ] Camera Raycasting accurately selects entities in 3D space.
- [ ] `PossessionSystem` swaps control between agents in < 1 tick.

## 7. Execution Logging & Monitoring
- **Logs**: Record OpenGL context initialization details and shader compile errors in `render.log` via **Loguru**.
- **Metrics**: Track Draw Call count and GPU Frame Time. Render real-time GPU stats in the terminal using **Rich.LiveData**.

## 9. Developer Experience (DX) & Tooling
- **Logging**: Use **Loguru** for structured, traceable events.
- **Terminal UI**: Use **Rich** for status tables and **Typer** for CLI arguments.
- **Static Analysis**: Enforce quality with **Ruff** (lint/format) and **Mypy** (types).
- **Perception Debug**: Use **visual-logging** for CV/ingestion node audits.
- **UI Layout**: Use **DearPyGui-Grid** for maintainable DPG window structures.
- **MCP Servers**:
    - `sequential-thinking`: Debug complex OpenGL thread synchronization issues.
    - `web-search`: Optimize ModernGL shaders using latest industry techniques.
