# Offline Development Guide

This guide provides instructions for developing the Serpentine Engine in strict, air-gapped environments where internet access is unavailable.

## 1. Environment Constraints

In this environment:
*   **No Internet Access**: You cannot run `pip install`, `npm install`, or fetch external resources.
*   **Pre-installed Dependencies**: Assume the environment has a fixed set of Python packages. Do not add new libraries to `requirements.txt` unless you can manually vendor them.
*   **System Libraries**: Tools like `ffmpeg`, `tesseract`, or `X11` might be missing or limited.

## 2. Dependency Mocking Strategy

The engine is designed to degrade gracefully or use mocks when optional dependencies are missing.

### 2.1. Vision Libraries (`opencv`, `numpy`)
The codebase often imports `cv2` or `numpy`. In offline environments where these might be absent (or in CI environments), use `unittest.mock` or a `try-except` block to provide dummy implementations.

**Example: Safe Import Pattern**
```python
try:
    import cv2
    import numpy as np
except ImportError:
    from unittest.mock import MagicMock
    cv2 = MagicMock()
    np = MagicMock()
    # Define minimal functioning mocks if needed
    np.zeros = lambda shape, dtype=None: [[0]*shape[1]]*shape[0]
```

### 2.2. Browser Automation (`playwright`)
If `playwright` browsers are not installed, the `DOMParserNode` should default to a "Headless Mock" mode that returns static HTML from a local string or file.

## 3. Asset Management

Since we cannot download models or datasets at runtime:

### 3.1. Local Models
*   **Location**: Place all ML models (ONNX, PyTorch) in the `assets/models/` directory.
*   **Loading**: Use relative paths.
    ```python
    import os
    MODEL_PATH = os.path.join(os.path.dirname(__file__), "../../assets/models/yolov8n.onnx")
    ```
*   **Fallback**: If the model file is missing, the `PerceptionNode` must log a warning and switch to a "Passthrough" mode (returning the input unchanged) rather than crashing.

### 3.2. Test Data
*   **Images**: Store sample images in `tests/data/images/` for unit tests.
*   **Snapshots**: Use `tests/data/snapshots/` for Gold Master testing of World states.

## 4. Documentation
All documentation is stored locally in `des_docs/`.
*   **View**: Use a Markdown viewer or standard text editor.
*   **Search**: Use `grep` or your IDE's "Find in Files" to navigate the `des_docs` tree.

## 5. Running Tests Offline

To run tests without attempting network connections:

```bash
# Run all tests, skipping those marked with @needs_internet
pytest -m "not needs_internet"

# Run specific offline-safe test
pytest tests/core/test_world.py
```

Ensure your tests mock any external API calls (e.g., to OpenAI or N8N) using `unittest.mock.patch`.

## 6. Pre-Commit Checks

Since you cannot install `pre-commit` hooks from the internet, run the following manually before submitting:

1.  **Format**: Ensure code follows PEP8 (or use `black` if installed).
2.  **Lint**: Run `flake8` or `pylint` if available.
3.  **Test**: Run `pytest` to ensure no regressions.
