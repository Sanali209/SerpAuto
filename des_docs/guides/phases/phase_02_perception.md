# Phase 2: Perception & Action Pipelines Guide

This guide covers the sensory ingestion and action execution layers of the engine.

## 1. Objectives
- **Ingestion**: Capture environmental data (Screen, DOM, Internal).
- **Perception DAG**: Process data through a directed acyclic graph of nodes.
- **Action Buffer**: Queue and execute physical commands.

## 2. Technical Prerequisites & Architecture
- [**Perception Nodes Design**](../../architecture/perception_nodes.md)
- [**Data Flow Overview**](../../DATA_FLOW.md)

## 3. Implementation Status

### 2.1 Ingestion Pipeline
- [ ] **SensoryInputSystem**: Abstract ingestion interface.
- [ ] **ScreenCaptureNode**: Real-time screen grabbing via `mss`.
- [ ] **InternalStateReader**: Direct memory/ECS observation for internal sims.

### 2.2 Perception Pipeline
- [ ] **PerceptionComponent**: Short-term sensory storage.
- [ ] **Pipeline System**: DAG-based execution of perception nodes.
- [ ] **CV Nodes**: `Crop`, `Grayscale`, `TemplateMatch`, `OCR`.
- [ ] **DOMParserNode**: (In Progress) High-fidelity HTML structure extraction.
- [ ] **GridMapper**: Conversion of sensory data into passability maps.

### 2.3 Action Execution
- [ ] **ActionBufferComponent**: Queue for pending intents.
- [ ] **Execution System**: Command pattern for physical translation.
- [ ] **Standard Actions**: `ClickAction`, `MoveAction`, `KeyAction` (PyAutoGUI/Playwright).

### 🛠️ Web Insights & Advanced Patterns
> [!IMPORTANT]
> **Zero-Copy Ingestion**: To minimize latency, prefer zero-copy capture methods where GPU textures are processed directly without round-tripping to system RAM.
> - **Strategic Cropping (ROI)**: Always crop to Regions of Interest (ROI) before heavy processing like OCR or YOLO to reduce pixel count and inference time.
> - **Quantization**: For on-device CV, use INT8 quantization or model pruning to increase throughput on standard CPUs.

### 🔄 Consolidation Hook: Unified Dataflow (Observations)
- **Goal**: Standardize the interface between perception and cognition.
- **Action**: All CV and Web nodes must wrap their output into standardized `Observation` objects to ensure downstream cognitive systems (BT/LLM) have a consistent interface.

## 4. Backlog Management
- **Input**: Read the pending tasks from the Phase 1 backlog: `des_docs/planning/backlogs/phase_01_backlog.md`.
- **Output**: Save remaining perception tasks and technical debt to: `des_docs/planning/backlogs/phase_02_backlog.md`.

## 5. Code Quality & Decomposition
- **File Length Limit**: Individual files **must not exceed 500 lines**.
- **Decomposition**: If a file grows beyond 500 lines (e.g., in a large CV system), split it into `ingestion.py`, `nodes.py`, and `engine.py`.
- **Complexity**: Ensure all CV nodes have clear Type Hints for their observation outputs.

## 6. Quality Assurance & Testing
- **Automated Tests**: Run `pytest tests/test_perception_cv.py`.
- **Regression Check**: Perception pipeline execution time must remain < 50ms per tick for standardized DAGs.

## 6. Phase Completion Criteria
- [ ] Standardized `Observation` objects are emitted by all nodes.
- [ ] Screen capture maintains 30 FPS at 1080p.
- [ ] `ActionBufferComponent` correctly sequences `ClickAction` and `KeyAction`.

## 7. Execution Logging & Monitoring
- **Logs**: Record CV node processing times and `OCRNode` confidence scores in `perception.log`.
- **Metrics**: Track FPS of the `SensoryInputSystem` in Architect Mode.

## 8. Developer Experience (DX)
- **MCP Servers**: Use the `sequential-thinking` MCP server to design complex DAG pipelines. Reference `web-search` MCP results for the latest OpenCV optimization techniques.
