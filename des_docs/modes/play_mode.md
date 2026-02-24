# Play Mode (ModernGL Rendering)

Play Mode turns the engine into a game runtime. In this configuration, a human player controls an entity alongside AI agents, visualized via hardware-accelerated rendering (ModernGL).

## 1. Bootstrapping & Lifecycle

The engine initializes with a configuration object that determines who owns the OS window.

### Two Sub-modes:
1.  **Play in Editor (PIE)**: The game runs inside the DearPyGui (DPG) toolset. The render output is blitted to a DPG Texture.
2.  **Standalone Play**: DPG is not loaded. The engine creates a raw GLFW/ModernGL window for maximum FPS.

**Toggle Logic**:
Pressing `F11` switches between `State.PLAY` and `State.DEV`.
*   **PLAY**: Input goes to the `PlayerControllerComponent`. Time flows.
*   **DEV**: Input goes to GUI. Time is paused (optional). Debug overlays appear.

## 2. Input Handling (Human-in-the-Loop)

### 2.1. PlayerInputSystem
*   Polls hardware (Keyboard/Mouse/Gamepad).
*   Maps raw inputs to semantic `Actions` (`MoveAction`, `ShootAction`).
*   Injects actions into the `ActionBufferComponent` of the entity tagged with `PlayerControllerComponent`.

### 2.2. Raycasting
To allow interaction with the 3D world:
1.  System gets cursor screen coordinates.
2.  Unprojects to world space using `CameraComponent` matrices.
3.  Casts a ray against `ColliderComponents`.
4.  Generates interaction events (`AttackAction`, `TalkAction`).

## 3. Rendering Pipeline (ModernGL)

`ModernGLRenderSystem` handles the visual output.

**Pipeline Steps:**
1.  **Transform Sync**: Update Model Matrices from ECS `TransformComponent`.
2.  **Global Uniforms**: Upload `dt`, light positions, and Camera View/Proj matrices.
3.  **Geometry Pass**: Render meshes (`MeshComponent`) with materials. Supports Instancing.
4.  **Post-Processing**: Apply FBO effects (Bloom, Color Grading).
5.  **UI Overlay**: Render HUD (Health, Ammo).
6.  **Swap Buffers**: Display frame.

## 4. Player-Agent Symbiosis

### 4.1. Unified Perception
AI Agents use `InternalStateNode` to scan the world. They do not distinguish between Player entities and other AI entities. If the Player enters an enemy's Frustum, the enemy's Behavior Tree triggers a "Chase" sequence.

### 4.2. Possession Mechanic
The ECS architecture allows seamless body-swapping.
*   **Action**: Player presses `F` on an ally NPC.
*   **System Logic**:
    1.  Swap `PlayerControllerComponent` from current entity to target entity.
    2.  Attach `AI_BrainComponent` to the old entity (handing it back to AI control).
    3.  Update Camera target.

## 5. Dev Mode Integration

Switching to Dev Mode enables "God Mode" features:
*   **Live State Editing**: Modify component values (Health, Speed) in real-time via DPG inspectors.
*   **Shader Hot-Reload**: Edit `.glsl` files and see changes instantly.
*   **AI Debug Overlays**: Render navigation paths, vision cones, and current Behavior Tree states above agent heads.
