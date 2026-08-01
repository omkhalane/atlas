from atlas.core.contracts import CapabilityRequest
from tests.fixtures.fake_adapters import FakeFilesystemPort, FakeProcessPort

def test_fake_filesystem():
    fs = FakeFilesystemPort()
    # Write a file
    req_write = CapabilityRequest(id="fs", parameters={"operation": "write", "path": "/test.txt", "content": "hello"})
    res_write = fs.execute(req_write)
    assert res_write.success is True

    # Read a file
    req_read = CapabilityRequest(id="fs", parameters={"operation": "read", "path": "/test.txt"})
    res_read = fs.execute(req_read)
    assert res_read.success is True
    assert res_read.data["content"] == "hello"

def test_fake_process():
    proc = FakeProcessPort()
    req = CapabilityRequest(id="proc", parameters={"command": "echo test"})
    res = proc.execute(req)
    assert res.success is True
    assert res.data["stdout"] == "test\n"
