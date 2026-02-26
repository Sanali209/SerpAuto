from typing import Optional

from serpentine.core.world import World
from serpentine.core.scene.loader import SceneLoader
from serpentine.core.scene.saver import SceneSaver
from serpentine.utils.logging import configure_logging

logger = configure_logging()

class SceneManager:
    """
    Orchestrates scene loading and saving operations.
    Acts as the main entry point for scene management in the engine.
    """

    def __init__(self, world: World):
        self.world = world

    def load_scene(self, filepath: str) -> None:
        """
        Loads a scene from the given filepath, replacing the current world state.

        Args:
            filepath: Path to the scene JSON file.
        """
        try:
            logger.info(f"Loading scene from {filepath}...")
            SceneLoader.load_scene(self.world, filepath)
            logger.info("Scene loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load scene: {e}")
            raise

    def save_scene(self, filepath: str, name: str = "Scene", description: str = "") -> None:
        """
        Saves the current world state to a scene file.

        Args:
            filepath: Path to save the scene JSON file.
            name: Name of the scene.
            description: Description of the scene.
        """
        try:
            logger.info(f"Saving scene to {filepath}...")
            SceneSaver.save_scene(self.world, filepath, name, description)
            logger.info("Scene saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save scene: {e}")
            raise

    def transition_to_scene(self, filepath: str) -> None:
        """
        Transitions to a new scene.
        Currently performs a full reload.
        Future versions may support delta loading or smooth transitions.

        Args:
            filepath: Path to the target scene file.
        """
        # TODO: Implement delta loading if needed for large worlds
        self.load_scene(filepath)
