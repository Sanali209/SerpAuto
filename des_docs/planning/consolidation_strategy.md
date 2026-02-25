# Serpentine Engine Consolidation Strategy

Analysis of the current framework reveals opportunities for tighter integration and removal of architectural redundancy.

## 1. Event-Driven System Orchestration
Currently, `main.py` manually wires systems based on modes. 
- **Improvement**: Move system discovery to `RegistryV2`. Systems should declare their `EngineMode` compatibility via decorators. The engine should automatically boot the correct system graph based on the selected mode.
- **Benefit**: Removes the massive `if/else` block in `main.py` and centralizes system-to-phase mapping.

## 2. Unified Command Pattern (Sensory -> Mind -> Action)
The link between Perception output and Mind input is currently bespoke across different demos.
- **Improvement**: Standardize on a "Command Object" that flows through the system. Perception emits `Observations`, Mind emits `Intent`, Action consumes `Commands`.
- **Benefit**: Allows swapping the vision system (MSS vs. Playwright) without changing the Behavior Tree nodes.

## 3. Generic Visual Graph UX
We have two planned editors: BT Editor and Perception DAG.
- **Improvement**: Abstract 90% of the DPG logic into a `BaseNodeCanvas`. This should handle panning/zooming, selection, and the link context menu.
- **Benefit**: Ensures a consistent look-and-feel across all node-based tools and halves the development effort for the Perception editor.

## 4. Centralized State & Snapshot Service
Persistence is currently side-loaded.
- **Improvement**: Integrate a `WorldSnapshotManager` directly into the `World` class. 
- **Benefit**: Enables "Undo/Redo" for the Architect Mode and simpler "Time Travel" debugging for the Swarm MAS.

## 5. Plugin Architecture
- **Improvement**: Support side-loading of "Extensions" (custom components/systems) from a `/plugins` folder using the `Registry`.
- **Benefit**: Allows the community to add new agent skins or sensors without modifying the core engine source code.
