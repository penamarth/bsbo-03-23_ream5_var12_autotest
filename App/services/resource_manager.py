from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime
from enums import ResourceType, ResourceStatus
from models.environment import Resource


class ResourceManager:
    """Управление ресурсами"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._resources = {}
            cls._instance._allocations = {}  # session_id -> [resource_ids]
            cls._instance._statistics = {
                'total_allocations': 0,
                'active_allocations': 0,
                'total_resources': 0
            }
        return cls._instance
    
    @classmethod
    def get_instance(cls):
        """Получение экземпляра синглтона"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def request_resource(self, resource_type: ResourceType, 
                         capacity: Optional[Dict[str, Any]] = None,
                         session_id: Optional[str] = None) -> Optional[Resource]:
        """Запрос ресурса"""
        print(f"ResourceManager: запрос ресурса типа {resource_type.value}")
        
        for resource in self._resources.values():
            if (resource.type == resource_type.value and 
                resource.status == ResourceStatus.AVAILABLE.value):
                if resource.allocate():
                    self._statistics['total_allocations'] += 1
                    self._statistics['active_allocations'] += 1
                    
                    if session_id:
                        if session_id not in self._allocations:
                            self._allocations[session_id] = []
                        self._allocations[session_id].append(resource.resource_id)
                    
                    print(f"Ресурс {resource.resource_id} выделен для сессии {session_id}")
                    return resource
        
        new_resource = self._create_resource(resource_type, capacity)
        if new_resource and new_resource.allocate():
            self._resources[new_resource.resource_id] = new_resource
            self._statistics['total_resources'] += 1
            self._statistics['total_allocations'] += 1
            self._statistics['active_allocations'] += 1
            
            if session_id:
                if session_id not in self._allocations:
                    self._allocations[session_id] = []
                self._allocations[session_id].append(new_resource.resource_id)
            
            print(f"Создан и выделен новый ресурс {new_resource.resource_id}")
            return new_resource
        
        return None
    
    def _create_resource(self, resource_type: ResourceType, 
                        capacity: Optional[Dict[str, Any]] = None) -> Resource:
        """Создание нового ресурса"""
        resource_id = f"{resource_type.value[:3]}-{str(uuid.uuid4())[:8]}"
        resource = Resource(resource_id, resource_type.value)
        
        default_capacities = {
            ResourceType.VM: {'cpu': 2, 'memory_mb': 2048, 'storage_mb': 10240},
            ResourceType.CONTAINER: {'cpu': 1, 'memory_mb': 1024, 'storage_mb': 5120},
            ResourceType.DATABASE: {'cpu': 2, 'memory_mb': 4096, 'storage_mb': 20480},
            ResourceType.NETWORK: {'bandwidth_mbps': 1000, 'latency_ms': 1},
            ResourceType.SERVICE: {'instances': 1, 'replicas': 1},
            ResourceType.GPU: {'memory_gb': 8, 'cores': 2048},
            ResourceType.MEMORY: {'size_gb': 16}
        }
        
        resource_capacity = capacity or default_capacities.get(resource_type, {})
        resource.capacity = resource_capacity
        
        resource.metadata = {
            'created_at': datetime.now().isoformat(),
            'resource_type': resource_type.value,
            'auto_managed': True
        }
        
        return resource
    
    def release_resource(self, resource: Resource, session_id: Optional[str] = None) -> None:
        """Освобождение ресурса"""
        resource.release()
        
        if session_id and session_id in self._allocations:
            if resource.resource_id in self._allocations[session_id]:
                self._allocations[session_id].remove(resource.resource_id)
                self._statistics['active_allocations'] -= 1
        
        print(f"Ресурс {resource.resource_id} освобожден")
    
    def release_session_resources(self, session_id: str) -> int:
        """Освобождение всех ресурсов сессии"""
        released_count = 0
        
        if session_id in self._allocations:
            for resource_id in self._allocations[session_id][:]:  # Копия списка
                resource = self._resources.get(resource_id)
                if resource:
                    self.release_resource(resource, session_id)
                    released_count += 1
            
            del self._allocations[session_id]
        
        print(f"Освобождено {released_count} ресурсов для сессии {session_id}")
        return released_count
    
    def check_availability(self, resource_type: ResourceType, count: int = 1) -> bool:
        """Проверка доступности ресурсов"""
        available = sum(
            1 for r in self._resources.values() 
            if r.type == resource_type.value and r.status == ResourceStatus.AVAILABLE.value
        )
        return available >= count
    
    def get_resource_utilization(self) -> Dict[str, float]:
        """Получение статистики использования ресурсов"""
        total = len(self._resources)
        if total == 0:
            return {'utilization': 0.0}
        
        allocated = sum(
            1 for r in self._resources.values() 
            if r.status == ResourceStatus.ALLOCATED.value
        )
        
        utilization = (allocated / total) * 100
        return {
            'total_resources': total,
            'allocated': allocated,
            'available': total - allocated,
            'utilization_percent': utilization
        }
    
    def get_resources_by_type(self, resource_type: ResourceType) -> List[Resource]:
        """Получение ресурсов по типу"""
        return [r for r in self._resources.values() if r.type == resource_type.value]
    
    def get_session_resources(self, session_id: str) -> List[Resource]:
        """Получение ресурсов, выделенных для сессии"""
        resource_ids = self._allocations.get(session_id, [])
        resources = []
        
        for resource_id in resource_ids:
            resource = self._resources.get(resource_id)
            if resource:
                resources.append(resource)
        
        return resources
    
    def register_existing_resource(self, resource: Resource) -> None:
        """Регистрация существующего ресурса в менеджере"""
        if resource.resource_id not in self._resources:
            self._resources[resource.resource_id] = resource
            self._statistics['total_resources'] += 1
            print(f"Ресурс {resource.resource_id} зарегистрирован в ResourceManager")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики менеджера ресурсов"""
        return {
            **self._statistics,
            'resource_count': len(self._resources),
            'active_sessions': len(self._allocations),
            'utilization': self.get_resource_utilization()
        }