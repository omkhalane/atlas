import os
import pytest
from atlas.core.contracts import UserIntent
from atlas.core.memory.store import MemoryStore, Fact
from atlas.integrations.filesystem.collector import FilesystemCollector
from atlas.integrations.git.collector import GitCollector
from atlas.core.context.engine import ContextEngine
import tempfile
import subprocess

@pytest.fixture
def temp_project():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Add some files
        with open(os.path.join(tmpdir, "test.txt"), "w") as f:
            f.write("hello")
        
        # Init git
        subprocess.run(["git", "init"], cwd=tmpdir, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmpdir, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmpdir, check=True)
        subprocess.run(["git", "add", "test.txt"], cwd=tmpdir, check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=tmpdir, check=True)
        
        yield tmpdir

def test_context_snapshot(temp_project):
    memory = MemoryStore(":memory:")
    memory.store(Fact(id="1", content="user likes python", provenance="chat"))

    fs_collector = FilesystemCollector(temp_project)
    git_collector = GitCollector(temp_project)
    
    engine = ContextEngine(memory, fs_collector, git_collector)
    
    intent = UserIntent(text="python", source="cli")
    snapshot = engine.snapshot(intent)
    
    assert snapshot.intent.text == "python"
    
    # Check filesystem state
    fs_state = snapshot.state["filesystem"]
    assert "test.txt" in fs_state["files"]
    assert ".git" not in fs_state["directories"]
    
    # Check git state
    git_state = snapshot.state["git"]
    assert git_state["error"] is None
    assert git_state["is_dirty"] is False
    assert git_state["branch"] is not None
    
    # Check memory
    mem_state = snapshot.memory
    assert len(mem_state["facts"]) == 1
    assert mem_state["facts"][0]["content"] == "user likes python"
