import os
import sys

# Ensure atlas-ocr is in sys.path
_atlas_ocr_path = os.path.join(os.path.dirname(__file__), "atlas-ocr")
if _atlas_ocr_path not in sys.path:
    sys.path.insert(0, _atlas_ocr_path)

# Set Paddle paths to avoid read-only sandbox errors in ~/.paddlex
os.environ["PADDLEX_HOME"] = "/tmp/.paddlex"
os.environ["PADDLE_PDX_CACHE_HOME"] = "/tmp/.paddlex"
os.environ["PADDLE_HOME"] = "/tmp/.paddle"

from paddleocr import PaddleOCR
from atlas.adapters.ports import AdapterPort
from atlas.core.contracts import CapabilityRequest, CapabilityResult

class OCRPort(AdapterPort):
    def __init__(self, lang="en", use_angle_cls=True):
        super().__init__()
        self.lang = lang
        self.use_angle_cls = use_angle_cls
        self.ocr = None

    def _load_model(self):
        if self.ocr is None:
            # Lazy load the PaddleOCR model
            self.ocr = PaddleOCR(use_angle_cls=self.use_angle_cls, lang=self.lang)

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        image_path = request.parameters.get("image_path")
        if not image_path:
            return CapabilityResult(success=False, error="image_path required")
        if not os.path.exists(image_path):
            return CapabilityResult(success=False, error=f"File not found: {image_path}")
            
        try:
            self._load_model()
            result = self.ocr.ocr(image_path, cls=self.use_angle_cls)
            
            # The result is a list of lists of text boxes
            # Format: [[[box_coords], (text, confidence)], ...]
            extracted_texts = []
            if result and len(result) > 0 and result[0]:
                for line in result[0]:
                    text, confidence = line[1]
                    extracted_texts.append(text)
                    
            transcription = "\n".join(extracted_texts).strip()
            
            return CapabilityResult(
                success=True, 
                data={"text": transcription}
            )
        except Exception as e:
            return CapabilityResult(success=False, error=str(e))
