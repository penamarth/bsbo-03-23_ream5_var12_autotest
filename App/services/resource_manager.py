import uuid
from models.environment import Resource


class ResourceManager:
    def __init__(self):
        self.resources = {}

    def requestResource(self, resource_type):
        print(f"ResourceManager: запрос ресурса типа {resource_type}")
        resource_id = str(uuid.uuid4())[:8]
        resource = Resource(resource_id, resource_type)
        
        if resource.allocate():
            self.resources[resource_id] = resource
            return resource
        return None

    def releaseResource(self, res):
        print(f"ResourceManager: освобождение ресурса {res.resourceId}")
        res.release()