import os
import urllib.request
import logging
import uuid
from typing import Optional

logger = logging.getLogger("atlas.marketplace")

class MarketplaceManager:
    def __init__(self, plugins_dir: str = "/code/ATLAS/.atlas/plugins"):
        self.plugins_dir = plugins_dir
        os.makedirs(self.plugins_dir, exist_ok=True)
        
    def install_from_url(self, url: str) -> Optional[str]:
        """Downloads a single .py plugin file from a URL to the plugins directory."""
        if not url.startswith("http"):
            logger.error("Invalid URL")
            return None
            
        try:
            filename = url.split("/")[-1]
            if not filename.endswith(".py"):
                # fallback if it doesn't end in .py
                filename = f"plugin_{uuid.uuid4().hex[:8]}.py"
                
            file_path = os.path.join(self.plugins_dir, filename)
            
            urllib.request.urlretrieve(url, file_path)
            logger.info(f"Successfully downloaded plugin to {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Failed to install plugin from URL: {e}")
            return None
