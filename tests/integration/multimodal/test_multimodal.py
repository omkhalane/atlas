from atlas.integrations.ocr.port import OCRPort
from atlas.integrations.voice.port import SpeechPort
from atlas.integrations.documents.port import DocumentPort
from atlas.core.security.filters import SensitivityFilter
from atlas.core.contracts import CapabilityRequest

def test_ocr_and_filter():
    port = OCRPort()
    req = CapabilityRequest(id="ocr", parameters={"image_path": __file__})
    res = port.execute(req)
    
    assert res.success
    text = res.data["text"]
    assert "confidential@example.com" in text
    
    s_filter = SensitivityFilter()
    filtered_text = s_filter.filter_text(text)
    
    assert "confidential@example.com" not in filtered_text
    assert "[REDACTED_EMAIL]" in filtered_text

def test_document_parser(tmp_path):
    doc_path = tmp_path / "test.txt"
    doc_path.write_text("Hello user@test.com and credit card 1234 5678 1234 5678", encoding="utf-8")
    
    port = DocumentPort()
    req = CapabilityRequest(id="doc", parameters={"doc_path": str(doc_path)})
    res = port.execute(req)
    
    assert res.success
    text = res.data["text"]
    
    s_filter = SensitivityFilter()
    filtered_text = s_filter.filter_text(text)
    
    assert "user@test.com" not in filtered_text
    assert "[REDACTED_EMAIL]" in filtered_text
    assert "1234 5678 1234 5678" not in filtered_text
    assert "[REDACTED_CARD]" in filtered_text
