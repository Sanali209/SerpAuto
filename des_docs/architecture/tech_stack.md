# Serpentine Engine Tech Stack & Integration Points

This document defines the core libraries used in the Serpentine Engine and specifies exactly how and where they are integrated to ensure a high-quality Developer Experience (DX).

## 1. Core Frameworks & Logic
| Library | Purpose | Integration Point |
| :--- | :--- | :--- |
| **NumPy** | High-perf math & data locality | Component data storage, Grid Mapping, Observation buffers. |
| **ModernGL** | GPU-accelerated rendering | `ModernGLRenderSystem` (Phase 11). |
| **Pydantic** | Data validation & schemas | `BaseComponent`, `Message` models, `Observation`, `Intent`. |
| **Asyncio** | Non-blocking engine loop | `SerpentineEngine` main loop and system updates. |

## 2. DX & Observability (New)
### 🛠️ Logging: `Loguru`
- **Integration**: Replaces the standard `logging` module globally.
- **Usage**:
    - `logger.debug("Entity {id} spawned")` in `World`.
    - `logger.info("Transition to {mode}")` in `SerpentineEngine`.
    - Automatic rotation and JSON serialization for analytics in Phase 14.

### 🛠️ CLI & Terminal: `Typer` & `Rich`
- **Integration**: `main.py` entry point.
- **Usage**:
    - **Typer**: Define subcommands like `run --mode ARCHITECT` or `test --phase 1`.
    - **Rich**: Render the "Control Deck" status in the terminal, display system update tables, and progress bars for dataset generation.

### 🛠️ Computer Vision Debugging: `visual-logging`
- **Integration**: `PerceptionPipelineSystem` (Phase 2 & 6).
- **Usage**:
    - Captures intermediate output from `CropNode`, `GrayscaleNode`, and `YOLONode`.
    - Generates `perception_debug.html` for post-mortem analysis of failed detections.

### 🛠️ UI Structure: `DearPyGui-Grid`
- **Integration**: `systems/gui/` windows.
- **Usage**:
    - Replaces manual `dpg.add_group` and `dpg.add_spacer` calls.
    - Used in the **Inspector**, **Outliner**, and **Visual Node Editors** (Phase 13).

## 3. Automation & Quality
| Tool | Integration | Command |
| :--- | :--- | :--- |
| **Pytest** | All `tests/` directories | `pytest` |
| **Ruff** | CI & Pre-commit | `ruff check .` |
| **Mypy** | CI & IDE Type Checking | `mypy .` |

## 4. Environment & AI
- **OpenCV**: Image preprocessing nodes.
- **ONNX Runtime**: CPU/GPU optimized inference for YOLO and RL models.
- **mss**: High-speed screen capture for desktop-based perception.
- **FastAPI**: Headless API and remote monitoring bridge.
