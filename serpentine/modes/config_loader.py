import json
import yaml
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ModeConfigLoader:
    """
    Utilities for loading mode configurations from JSON/YAML files.
    """

    @staticmethod
    def load_config(filepath: str) -> Dict[str, Any]:
        """
        Loads configuration from a file.
        """
        if not os.path.exists(filepath):
            logger.error(f"Mode config file not found: {filepath}")
            return {}

        try:
            with open(filepath, 'r') as f:
                if filepath.endswith('.yaml') or filepath.endswith('.yml'):
                    return yaml.safe_load(f) or {}
                else:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load mode config {filepath}: {e}")
            return {}
