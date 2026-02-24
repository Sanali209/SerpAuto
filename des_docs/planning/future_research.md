# Future Research & Detailed Design Goals

This document outlines the next frontiers for the Serpentine Engine. It identifies areas requiring deeper technical research, detailed architectural specifications, and proof-of-concept implementations.

## 1. High-Performance Rendering (Phase 11+)
The transition to ModernGL requires a "Zero-Copy" strategy to remain competitive.
*   **Research Goal**: Finalize the pipeline for shared GPU memory between **ModernGL** (Game Render) and **DearPyGui** (Editor UI).
*   **Questions**: 
    - Can we use `cudaInterop` or `vulkan` extensions for zero-latency texture sharing?
    - How do we handle multi-viewport rendering of 100+ agents without VRAM saturation?

## 2. Advanced Multi-Agent Coordination (MAS)
The current Pub/Sub is functional but lacks high-level "Orchestration".
*   **Research Goal**: Design a "Hierarchy of Tasks" (HoT) system where a Manager Agent can decompose a high-level goal (e.g., "Scrape this whole site") into sub-tasks for Worker Agents.
*   **Detailed Design**: Formalize the negotiation protocol (Request for Proposal pattern) between agents.

## 3. Cognitive Persistence & "Time Travel"
Saving state is easy; restoring state in a *dynamic* environment is hard.
*   **Research Goal**: Investigating "Deterministic Playback" for external I/O.
*   **Question**: How can we "Time Travel" an agent to a previous World State if the external website/game has changed its state in the meantime? 
*   **Hypothesis**: Focus on "Virtualizing the Perception" — feeding the agent historical frames instead of live data during the rewind phase.

## 4. Nuanced ML Pipeline (Hot-Swapping 2.0)
*   **Research Goal**: Implementing "Safe Transitions" during weight updates.
*   **Detailed Design**: Ensure that if a model is swapped while an agent is mid-action (e.g., `WAITING_FOR_IO`), the new model properly interprets the *previous* context to compute the next reward.

## 5. Perception: Beyond 2D Mapping
*   **Research Goal**: 3D Scene Reconstruction from 2D frames.
*   **Focus**: Integrating SLAM (Simultaneous Localization and Mapping) nodes for agents operating in 3D game environments (e.g., Survival games, FPS).
*   **Tools**: OpenVSLAM, ORB-SLAM3 integration via ONNX/C++.

## 6. Optimization: Vectorized ECS
*   **Research Goal**: Massively Parallel System Updates.
*   **Focus**: Using NumPy/PyTorch tensors inside `System.update()` to calculate physics/perception for thousands of entities in a single Python call, bypassing the per-entity loop overhead.

---

### Sync Requirements
> [!NOTE]
> As these research goals mature, they should be promoted to:
> 1.  Technical Specifications in `/architecture/`.
> 2.  Actionable tasks in `planning/tasks.md`.
