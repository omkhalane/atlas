import os
import sys

# Ensure atlas_voice is in sys.path
_atlas_voice_path = os.path.join(os.path.dirname(__file__), "atlas-voice")
if _atlas_voice_path not in sys.path:
    sys.path.insert(0, _atlas_voice_path)

from atlas_voice import WhisperModel
from atlas.adapters.ports import AdapterPort
from atlas.core.contracts import CapabilityRequest, CapabilityResult

class SpeechPort(AdapterPort):
    def __init__(self, model_size="tiny", device="cpu", compute_type="int8"):
        super().__init__()
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = None

    def _load_model(self):
        if self.model is None:
            self.model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        audio_path = request.parameters.get("audio_path")
        if not audio_path:
            return CapabilityResult(success=False, error="audio_path required")
        if not os.path.exists(audio_path):
            return CapabilityResult(success=False, error=f"File not found: {audio_path}")
            
        try:
            self._load_model()
            segments, info = self.model.transcribe(audio_path, beam_size=5)
            
            transcription = "".join([segment.text for segment in segments]).strip()
            
            return CapabilityResult(
                success=True, 
                data={
                    "text": transcription,
                    "language": info.language,
                    "language_probability": info.language_probability
                }
            )
        except Exception as e:
            return CapabilityResult(success=False, error=str(e))
