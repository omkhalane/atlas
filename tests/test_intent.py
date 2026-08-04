from runtime.intelligence.intent import IntentDetector


def test_pure_greeting_uses_direct_answer():
    detector = IntentDetector()

    result = detector.detect("hi")

    assert result["intent"] == "chat.greeting"
    assert result["difficulty"] == "easy"
    assert result["direct_answer"]


def test_greeting_with_task_signal_does_not_short_circuit():
    detector = IntentDetector()

    result = detector.detect("hi, create a folder for the project")

    assert result["direct_answer"] is None
    assert result["difficulty"] == "hard"
    assert result["intent"] == "unknown"
