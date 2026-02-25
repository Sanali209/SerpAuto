# Architect Mode

**Architect Mode** is the default operation mode for the Serpentine Engine during development. It provides a rich, interactive Dashboard powered by **DearPyGui** for real-time monitoring and manipulation of the ECS World.

## 🛠️ System Orchestration

In **Architect Mode**, the engine dynamically injects systems registered with `EngineMode.ARCHITECT` via **Registry V2**. Key UI systems include:
- **`WindowManager`**: Orchestrates modular panels.
- **`SelectionService`**: Synchronizes entity and node selection.
- **`AutoUIBuilder`**: Dynamically generates inspectors and graphs.
- **`ModernGLRenderSystem`**: Zero-copy visual monitoring.

## 📺 Features

### World Outliner
A hierarchical view of all entities in the `World`.
- **Search**: Filter entities by name or tags.
- **Inspect**: Click an entity to open it in the Component Inspector.

### Component Inspector
Driven by the `AutoUIBuilder`, this panel provides a live view of an entity's components.
- **Live Edit**: Adjust positions, velocities, or AI blackboard variables on the fly.
- **Add/Remove**: Prototyping components without restarting the engine.

### Swarm Sniffer
Monitor inter-agent messaging traffic in real-time. Peek into message payloads and visualize the "History" buffer.

## 🚀 Launching
```bash
python main.py --mode ARCHITECT --gui
```
*(Default when running `main.py` without arguments)*
