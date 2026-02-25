# Modernized Debug UI Architecture

This document outlines the refactoring of the `GUIDebugSystem` into a modular, class-based architecture, integrated with the [**Unified Registry & Selection**](unified_registry_and_node_graph.md) system.

## Phase 1: Core Modularization

The monolithic `systems/gui.py` is being decomposed into a directory-based package structure.

### 1. `BaseUIWindow` (Abstract Base)
Every window in the dashboard inherits from `BaseUIWindow`.
- `window_tag`: Unique ID for the DPG window.
- `render()`: Defines the static structure of the window (called once).
- `update(world, dt)`: Handles per-tick data updates and reactive changes.

### 2. `WindowManager` (Composite)
A central manager that orchestrates the lifecycle of all registered windows.
- Resolves window dependencies.
- Handles uniform visibility switching.
- Forwards tick updates from the ECS system to active windows.

## Integrated Core Systems

### Unified Registry (Registry V2)
The GUI now utilizes the categorized metadata from the registry to dynamically populate:
- **Add Component** dropdowns in the Inspector.
- **Node Library** sidebars in the graph editors.
- **System monitoring** lists in the System Inspector.

### Global Selection Service
Selection is no longer local to a single window.
- **Entity selection** (from Outliner or Viewport) is synchronized globally.
- **Node selection** (from BT or Pipeline editors) redirects the Inspector to show node parameters.
- Selection changes are handled via the `GUIEventBus`.

## Proposed Patterns

### Composite Pattern
The UI is a tree of components. The `WindowManager` contains `Windows`, which may contain `Modules` (e.g., the Inspector contains a `BrainModule`).

### Template Method Pattern
The `BaseUIWindow` provides a template for window creation, ensuring all windows have consistent initialization, rendering, and update hooks.

### Observer Pattern
A lightweight internal `GUIEventBus` decouples UI actions from different windows.

## Target Structure

```text
systems/gui/
├── __init__.py          # Exports the facade GUIDebugSystem
├── base.py              # BaseUIWindow and GUIEventBus
├── manager.py           # WindowManager implementation
├── style.py             # Themes, fonts, and shared visual tokens
├── windows/             # Individual window implementations
│   ├── control_deck.py 
│   ├── outliner.py     
│   ├── inspector.py    
│   ├── viewport.py     
│   └── dataset.py      
└── graph/               # Specialized Graph Editors
    ├── base_graph.py   
    ├── bt_editor.py    
    └── perc_editor.py  
```

## Benefits
1. **Developer Experience**: Adding a new debug tool becomes as simple as creating a new class.
2. **Encapsulation**: Callbacks and local state are contained within their respective classes.
3. **Synchronized State**: The Selection Service ensures all panels share a common focus.
4. **Visual Editing**: Node results and BT execution states are visible in real-time.
