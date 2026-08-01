import pytest
import sys
from atlas.core.contracts import CapabilityResult, CapabilityRequest
from atlas.adapters.ports import AdapterPort
from atlas.adapters.linux.filesystem import FilesystemPort as LinuxFS
from atlas.adapters.linux.process import ProcessPort as LinuxProc
from atlas.adapters.linux.notification import NotificationPort as LinuxNotif
from atlas.adapters.linux.clipboard import ClipboardPort as LinuxClip
from atlas.integrations.docker.port import DockerPort
from atlas.integrations.browser.port import BrowserPort
from atlas.adapters.macos.filesystem import MacOSFilesystemPort
from atlas.adapters.macos.process import MacOSProcessPort
from atlas.adapters.macos.clipboard import MacOSClipboardPort
from atlas.adapters.macos.notification import MacOSNotificationPort
from atlas.adapters.windows.filesystem import WindowsFilesystemPort
from atlas.adapters.windows.process import WindowsProcessPort
from atlas.adapters.windows.clipboard import WindowsClipboardPort
from atlas.adapters.windows.notification import WindowsNotificationPort
from atlas.adapters.factory import get_platform_adapters

@pytest.mark.parametrize("adapter_class", [
    LinuxFS, LinuxProc, LinuxNotif, LinuxClip,
    MacOSFilesystemPort, MacOSProcessPort, MacOSClipboardPort, MacOSNotificationPort,
    WindowsFilesystemPort, WindowsProcessPort, WindowsClipboardPort, WindowsNotificationPort,
    DockerPort, BrowserPort
])
def test_implements_adapter_port(adapter_class):
    assert issubclass(adapter_class, AdapterPort)

def test_filesystem_conformance(tmp_path):
    adapters = get_platform_adapters()
    port = adapters["filesystem"]
    
    res = port.execute(CapabilityRequest(id="fs", parameters={"operation": "read", "path": str(tmp_path / "missing.txt")}))
    assert isinstance(res, CapabilityResult)
    assert not res.success
    
    res = port.execute(CapabilityRequest(id="fs", parameters={"operation": "write", "path": str(tmp_path / "new.txt"), "content": "data"}))
    assert isinstance(res, CapabilityResult)
    assert res.success

    res = port.execute(CapabilityRequest(id="fs", parameters={"operation": "read", "path": str(tmp_path / "new.txt")}))
    assert res.success
    assert res.data["content"] == "data"
