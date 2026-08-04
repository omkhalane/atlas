from runtime.llm.conversation.service import ConversationService


def test_conversation_service_lifecycle():
    service = ConversationService()
    conv = service.create(title="Test Conv")
    
    assert conv.title == "Test Conv"
    
    service.add_message(conv.id, "user", "Hello")
    service.add_message(conv.id, "assistant", "Hi there!")

    recent = service.get_recent_messages(conv.id)
    assert len(recent) == 2

    # Fork
    forked = service.fork(conv.id)
    assert forked is not None
    assert "Fork of" in forked.title
    assert len(forked.messages) == 2

    # Export & Import
    exp = service.export_data(conv.id)
    assert exp["title"] == "Test Conv"

    imp = service.import_data(exp)
    assert imp.id == conv.id
