import os
import time
import uuid
from typing import Dict, Any
from atlas.adapters.ports import AdapterPort
from atlas.core.contracts import CapabilityRequest, CapabilityResult

# We will lazily load mss and cv2 so they don't break if not installed
class MediaPort(AdapterPort):
    def __init__(self):
        super().__init__()
        self._sct = None
        self._recording = False
        self._frames = []
        self._start_time = None
        self._record_task_id = None
        self._thread = None

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        action = request.parameters.get("action")
        
        if action == "start_recording":
            return self._start_recording(request.parameters)
        elif action == "stop_recording":
            return self._stop_recording()
        elif action == "take_screenshot":
            return self._take_screenshot(request.parameters)
        else:
            return CapabilityResult(success=False, error=f"Unknown media action: {action}")

    def _start_recording(self, params: Dict[str, Any]) -> CapabilityResult:
        if self._recording:
            return CapabilityResult(success=False, error="Already recording.")
        
        try:
            import mss
            import numpy as np
            import cv2
            import threading
            
            self._record_task_id = params.get("task_id", str(uuid.uuid4()))
            self._sct = mss.mss()
            self._frames = []
            self._recording = True
            self._start_time = time.time()
            
            # Start background thread to capture frames
            def record_loop():
                monitor = self._sct.monitors[1]  # primary monitor
                while self._recording:
                    sct_img = self._sct.grab(monitor)
                    img = np.array(sct_img)
                    # Convert BGRA to BGR
                    frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    self._frames.append(frame)
                    time.sleep(0.1) # approx 10 FPS
            
            self._thread = threading.Thread(target=record_loop, daemon=True)
            self._thread.start()
            
            return CapabilityResult(success=True, data={"status": "recording_started"})
        except ImportError as e:
            return CapabilityResult(success=False, error=f"Missing dependencies (mss, cv2, numpy): {str(e)}")

    def _stop_recording(self) -> CapabilityResult:
        if not self._recording:
            return CapabilityResult(success=False, error="Not currently recording.")
            
        self._recording = False
        if self._thread:
            self._thread.join(timeout=2.0)
        
        try:
            import cv2
            import os
            
            if not self._frames:
                return CapabilityResult(success=False, error="No frames captured.")
                
            height, width, layers = self._frames[0].shape
            
            output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "artifacts"))
            os.makedirs(output_dir, exist_ok=True)
            video_path = os.path.join(output_dir, f"{self._record_task_id}.mp4")
            
            # Use XVID or mp4v
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            # Calculate actual FPS based on elapsed time
            elapsed = time.time() - self._start_time
            fps = len(self._frames) / elapsed if elapsed > 0 else 10
            
            video = cv2.VideoWriter(video_path, fourcc, fps, (width, height))
            for frame in self._frames:
                video.write(frame)
            
            video.release()
            
            # Free memory
            self._frames = []
            if self._sct:
                self._sct.close()
                self._sct = None
                
            return CapabilityResult(success=True, data={"video_path": video_path})
        except Exception as e:
            return CapabilityResult(success=False, error=f"Failed to encode video: {str(e)}")

    def _take_screenshot(self, params: Dict[str, Any]) -> CapabilityResult:
        try:
            import mss
            import mss.tools
            import os
            import uuid
            
            output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "artifacts"))
            os.makedirs(output_dir, exist_ok=True)
            image_path = os.path.join(output_dir, f"screenshot_{uuid.uuid4().hex[:8]}.png")
            
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                sct_img = sct.grab(monitor)
                mss.tools.to_png(sct_img.rgb, sct_img.size, output=image_path)
                
            return CapabilityResult(success=True, data={"image_path": image_path})
        except Exception as e:
            return CapabilityResult(success=False, error=str(e))
