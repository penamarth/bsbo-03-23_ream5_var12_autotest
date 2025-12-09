import uuid
from enums import EnvironmentType
from enums.statuses import ResourceStatus

class Environment:
    def __init__(self, env_id: str, env_type: EnvironmentType, config: dict):
        self.envId = env_id
        self.type = env_type
        self.config = config

    def isAvailable(self) -> bool:
        return True

    def __str__(self):
        return f"Environment[{self.envId}]: {self.type.value}"


class Resource:
    def __init__(self, resource_id: str, resource_type: str):
        self.resourceId = resource_id
        self.type = resource_type
        self.status = ResourceStatus.AVAILABLE.value

    def allocate(self) -> bool:
        if self.status == ResourceStatus.AVAILABLE.value:
            self.status = ResourceStatus.ALLOCATED.value
            return True
        return False

    def release(self):
        self.status = ResourceStatus.AVAILABLE.value

    def __str__(self):
        return f"Resource[{self.resourceId}]: {self.type} ({self.status})"