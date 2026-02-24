import argparse
import asyncio
import sys
import os

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.engine_v2 import SerpentineEngineV2, EngineMode, Phase
from core.scene import SceneManager
from core.registry import Registry

# Import all modules to trigger registration
import components.core
import components.spatial
import components.web
import components.domain
import components.internal
import components.snake

import systems.action
import systems.perception
import perception.pipeline
import systems.brain
import systems.swarm
import systems.telemetry
import systems.input
import systems.rl
import systems.learning
import systems.advanced
import systems.games.snake
import systems.gui
import systems.api
import systems.persistence
import systems.auto_ui_builder
import systems.render_modern
import systems.player_input
import systems.possession

def main():
    parser = argparse.ArgumentParser(description="Serpentine Engine Loader")
    parser.add_argument("--scene", type=str, help="Path to scene JSON file", required=False)
    parser.add_argument("--mode", type=str, default="ARCHITECT",
                        choices=["ARCHITECT", "PRODUCTION", "TEACHER", "GYMNASIUM", "ACTOR_LEARNER", "PLAY"],
                        help="Operation Mode override")
    parser.add_argument("--tick-rate", type=int, help="Override tick rate", required=False)
    parser.add_argument("--gui", action="store_true", help="Launch the DearPyGui God Mode dashboard")
    parser.add_argument("--api", action="store_true", help="Launch the FastAPI external controller")
    parser.add_argument("--headless", action="store_true", help="Disable all rendering/UI systems")

    args = parser.parse_args()

    print(f"Initializing Serpentine Engine...")

    # 1. Determine Mode
    try:
        mode = EngineMode[args.mode]
    except KeyError:
        mode = EngineMode.ARCHITECT

    engine = SerpentineEngineV2(mode=mode)

    # 2. Load Scene if provided
    if args.scene:
        print(f"Loading scene from {args.scene}...")
        try:
            SceneManager.load_scene(args.scene, engine)
            print("Scene loaded successfully.")
        except Exception as e:
            print(f"Error loading scene: {e}")
            return
    else:
        print("No scene provided. Starting empty engine.")

    # 3. System Orchestration
    active_systems = []

    # A. Core Internal Systems (Always enabled unless headless is extreme)
    core_system_names = [
        "MessageRouterSystem",     # Swarm / MAIL_ROUTING
        "SensoryInputSystem",      # PERCEPTION
        "PerceptionPipelineSystem",# PERCEPTION (Processes the DAG)
        "AI_BrainSystem",          # COGNITION
        "ActionExecutionSystem",   # EXECUTION
    ]
    
    # B. Mode-Specific Systems
    mode_requirements = {
        EngineMode.ARCHITECT: ["RaycastSystem"],
        EngineMode.PLAY: ["PlayerInputSystem", "PossessionSystem", "RaycastSystem"],
        EngineMode.TEACHER: ["DatasetLoggerSystem", "HumanInputSystem"],
        EngineMode.GYMNASIUM: ["EnvironmentJudgeSystem"],
        EngineMode.ACTOR_LEARNER: ["EnvironmentJudgeSystem", "ReplayBufferSystem", "TelemetrySystem"],
        EngineMode.PRODUCTION: ["TelemetrySystem"]
    }

    # C. UI & Visual Systems
    # Default to showing GUI in ARCHITECT or if --gui is passed, unless --headless is explicitly set.
    show_gui = (args.gui or mode == EngineMode.ARCHITECT) and not args.headless
    show_api = args.api or (mode in [EngineMode.PRODUCTION, EngineMode.ACTOR_LEARNER])
    
    if not args.headless:
        # Add core systems
        for name in core_system_names:
            cls = Registry.get_system(name)
            if cls:
                engine.add_system(cls(), phase=Registry.get_system_phase(name))

        # Add mode systems
        for name in mode_requirements.get(mode, []):
            cls = Registry.get_system(name)
            if cls:
                engine.add_system(cls(), phase=Registry.get_system_phase(name))

        # Add Renderer
        render_cls = Registry.get_system("ModernGLRenderSystem")
        if render_cls:
            # Standalone window if PLAY mode, else FBO for embedding in GUI
            use_fbo = (mode != EngineMode.PLAY) or show_gui
            engine.add_system(render_cls(use_fbo=use_fbo), phase=Phase.PERCEPTION)
            print(f"ModernGLRenderSystem added (use_fbo={use_fbo})")

        # Add GUI
        if show_gui:
            gui_cls = Registry.get_system("GUIDebugSystem")
            if gui_cls:
                engine.add_system(gui_cls(engine=engine), phase=Phase.TELEMETRY)
                print("GUIDebugSystem activated.")

        # Add API
        if show_api:
            api_cls = Registry.get_system("FastAPISystem")
            if api_cls:
                engine.add_system(api_cls(), phase=Phase.TELEMETRY)
                print("FastAPISystem activated.")

    # 4. Default Content for Empty Scene
    if not args.scene:
        from components.core import MetadataComponent, PerceptionComponent
        from components.spatial import TransformComponent
        ent = engine.world.add_entity()
        engine.world.add_component(ent, MetadataComponent(name="Sense-Bot"))
        engine.world.add_component(ent, TransformComponent(x=0, y=0, z=0))
        engine.world.add_component(ent, PerceptionComponent())
        print("Created default perception agent: 'Sense-Bot'")

    # 5. Apply Overrides
    if args.tick_rate:
        engine.tick_rate = args.tick_rate

    print(f"Starting Engine in {mode.name} mode at {engine.tick_rate} TPS...")

    try:
        asyncio.run(engine.run())
    except KeyboardInterrupt:
        print("\nEngine stopped by user.")

if __name__ == "__main__":
    main()
