import sys
from typing import Dict
from atlas.adapters.ports import AdapterPort

def get_platform_adapters() -> Dict[str, AdapterPort]:
    platform = sys.platform
    
    if platform.startswith('linux'):
        from atlas.adapters.linux import FilesystemPort, ProcessPort, ClipboardPort, NotificationPort
        return {
            "filesystem": FilesystemPort(),
            "process": ProcessPort(),
            "clipboard": ClipboardPort(),
            "notification": NotificationPort()
        }
    elif platform == 'darwin':
        from atlas.adapters.macos import MacOSFilesystemPort, MacOSProcessPort, MacOSClipboardPort, MacOSNotificationPort
        return {
            "filesystem": MacOSFilesystemPort(),
            "process": MacOSProcessPort(),
            "clipboard": MacOSClipboardPort(),
            "notification": MacOSNotificationPort()
        }
    elif platform == 'win32':
        from atlas.adapters.windows import WindowsFilesystemPort, WindowsProcessPort, WindowsClipboardPort, WindowsNotificationPort
        return {
            "filesystem": WindowsFilesystemPort(),
            "process": WindowsProcessPort(),
            "clipboard": WindowsClipboardPort(),
            "notification": WindowsNotificationPort()
        }
    else:
        raise NotImplementedError(f"Platform {platform} is not supported.")
