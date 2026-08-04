from planner.local_planner import LocalPlanner


class DummyLLM:
    def _call_openrouter(self, *_args, **_kwargs):
        raise RuntimeError("OpenRouter unavailable")


def _planner_context(goal: str, capabilities: str) -> str:
    return f"""
CURRENT ENVIRONMENT:
Time: 2026-08-03 00:00:00
Working Directory: /code/ATLAS
Workspace Type: Git Repository

LONG TERM MEMORY (Strict Rules & Facts):
No explicit memory set.

AVAILABLE CAPABILITIES:
{capabilities}

RECENT HISTORY:
No recent tasks.

USER REQUEST:
{goal}
""".strip()


def test_generate_plan_falls_back_to_browser_for_email_goal():
    planner = LocalPlanner(DummyLLM())
    context = _planner_context(
        "open gmail and send mail to test@example.com",
        "- browser: run (Control browser using browser-harness script payload)\n- command: run (Execute bash commands)",
    )

    intent, graph, needs_cloud = planner.generate_plan(context)

    assert intent == "browser.open"
    assert needs_cloud is False
    assert graph
    assert graph[0].action == "browser"
    assert "mail.google.com" in graph[0].parameters["script"]


def test_generate_plan_falls_back_to_command_for_filesystem_goal():
    planner = LocalPlanner(DummyLLM())
    context = _planner_context(
        "create a folder for the project",
        "- filesystem: list_files, write_file, append_file, delete_file, undo (Local filesystem operations)\n- command: run (Execute bash commands)",
    )

    intent, graph, needs_cloud = planner.generate_plan(context)

    assert intent == "filesystem.inspect"
    assert needs_cloud is False
    assert graph
    assert graph[0].action == "command"
    assert graph[0].parameters["command"] == "pwd && ls -la"
