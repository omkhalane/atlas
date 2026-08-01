import docker
from atlas.adapters.ports import AdapterPort
from atlas.core.contracts import CapabilityRequest, CapabilityResult

class DockerPort(AdapterPort):
    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        try:
            client = docker.from_env()
            containers = client.containers.list(all=True)
            
            # Format container info similar to standard docker ps output or json
            lines = []
            for container in containers:
                lines.append(f"{container.short_id} - {container.name} - {container.status}")
                
            return CapabilityResult(success=True, data={"containers": lines})
        except docker.errors.DockerException as e:
            return CapabilityResult(success=False, error=f"Docker command failed. Is Docker running? Error: {str(e)}")
        except Exception as e:
            return CapabilityResult(success=False, error=str(e))
