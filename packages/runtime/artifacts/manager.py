import os
import uuid
import logging
from typing import Optional

logger = logging.getLogger("atlas.artifacts")

class ArtifactsManager:
    def __init__(self, base_dir: str = "/code/ATLAS/.atlas/artifacts"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def save_artifact(self, task_id: str, content: str, extension: str = "md", filename: Optional[str] = None) -> str:
        """
        Saves content to a reusable artifact file.
        Returns the absolute path to the artifact.
        """
        task_dir = os.path.join(self.base_dir, task_id)
        os.makedirs(task_dir, exist_ok=True)
        
        fname = filename if filename else f"artifact_{uuid.uuid4().hex[:8]}.{extension}"
        filepath = os.path.join(task_dir, fname)
        
        try:
            with open(filepath, "w") as f:
                f.write(content)
            logger.info(f"Artifact saved: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save artifact {filepath}: {e}")
            return ""

    def get_task_artifacts(self, task_id: str) -> list[str]:
        """Returns list of artifact file paths for a given task ID."""
        task_dir = os.path.join(self.base_dir, task_id)
        if not os.path.exists(task_dir):
            return []
            
        artifacts = []
        for file in os.listdir(task_dir):
            artifacts.append(os.path.join(task_dir, file))
        return artifacts
