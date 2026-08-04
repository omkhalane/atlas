import os
import uuid
import logging
from runtime.events.bus import EventBus
import shutil

logger = logging.getLogger("atlas.transfers")

class TransferManager:
    def __init__(self, bus: EventBus, download_dir: str = "/code/ATLAS/.atlas/downloads"):
        self.bus = bus
        self.download_dir = download_dir
        os.makedirs(self.download_dir, exist_ok=True)
        
    async def process_upload(self, filename: str, content: bytes) -> str:
        """Saves an uploaded file to the downloads directory and notifies."""
        safe_name = f"{uuid.uuid4().hex[:6]}_{filename}"
        path = os.path.join(self.download_dir, safe_name)
        try:
            with open(path, "wb") as f:
                f.write(content)
            
            await self.bus.publish("NOTIFICATION", {
                "level": "success",
                "message": f"Successfully uploaded {filename}",
                "path": path
            })
            return path
        except Exception as e:
            logger.error(f"Failed to upload {filename}: {e}")
            await self.bus.publish("NOTIFICATION", {
                "level": "error",
                "message": f"Failed to upload {filename}"
            })
            return ""
