from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid
from enums import EnvironmentType, ResourceStatus


class Resource:
    """Ресурс тестовой среды"""
    
    def __init__(self, resource_id: str, resource_type: str):
        self.resource_id = resource_id
        self.type = resource_type
        self.status = ResourceStatus.AVAILABLE.value
        self.metadata: Dict[str, Any] = {}
        self.created_at = datetime.now()
        self.last_allocated: Optional[datetime] = None
        self.capacity: Dict[str, Any] = {}
        self.tags: List[str] = []
    
    def allocate(self) -> bool:
        """Выделение ресурса"""
        if self.status == ResourceStatus.AVAILABLE.value:
            self.status = ResourceStatus.ALLOCATED.value
            self.last_allocated = datetime.now()
            print(f"Ресурс {self.resource_id} выделен")
            return True
        return False
    
    def release(self) -> None:
        """Освобождение ресурса"""
        self.status = ResourceStatus.AVAILABLE.value
        print(f"Ресурс {self.resource_id} освобожден")
    
    def set_capacity(self, cpu: int = 1, memory: int = 1024, storage: int = 2048) -> None:
        """Установка характеристик ресурса"""
        self.capacity = {
            'cpu': cpu,
            'memory_mb': memory,
            'storage_mb': storage
        }
    
    def add_tag(self, tag: str) -> None:
        """Добавление тега к ресурсу"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def __str__(self) -> str:
        return f"Resource[{self.resource_id}]: {self.type} ({self.status})"
    
    def to_dict(self) -> dict:
        """Преобразовать объект в словарь"""
        return {
            'resource_id': self.resource_id,
            'type': self.type,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'last_allocated': self.last_allocated.isoformat() if self.last_allocated else None,
            'capacity': self.capacity,
            'tags': self.tags,
            'metadata': self.metadata
        }


class Environment:
    """Тестовая среда"""
    
    def __init__(self, env_id: str, env_type: EnvironmentType, config: Dict[str, Any]):
        self.env_id = env_id
        self.type = env_type
        self.config = config
        self.status = "created"
        self.resources: List[Resource] = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.version: str = "1.0"
        self.isolation_level: str = "shared"  # или "dedicated"
    
    def is_available(self) -> bool:
        """Проверка доступности среды"""
        if not self.resources:
            return False
        
        # Проверка, что все ресурсы доступны или выделены
        available_count = sum(
            1 for resource in self.resources 
            if resource.status in [ResourceStatus.AVAILABLE.value, ResourceStatus.ALLOCATED.value]
        )
        
        return available_count == len(self.resources)
    
    def add_resource(self, resource: Resource) -> None:
        """Добавление ресурса в среду"""
        if resource not in self.resources:
            self.resources.append(resource)
            self.updated_at = datetime.now()
            print(f"Ресурс {resource.resource_id} добавлен в среду {self.env_id}")
    
    def remove_resource(self, resource_id: str) -> bool:
        """Удаление ресурса из среды"""
        for resource in self.resources:
            if resource.resource_id == resource_id:
                self.resources.remove(resource)
                self.updated_at = datetime.now()
                print(f"Ресурс {resource_id} удален из среды {self.env_id}")
                return True
        return False
    
    def get_resource_by_type(self, resource_type: str) -> List[Resource]:
        """Получение ресурсов по типу"""
        return [r for r in self.resources if r.type == resource_type]
    
    def update_config(self, key: str, value: Any) -> None:
        """Обновление конфигурации среды"""
        self.config[key] = value
        self.updated_at = datetime.now()
    
    def __str__(self) -> str:
        return f"Environment[{self.env_id}]: {self.type.value} ({self.status})"
    
    def to_dict(self) -> dict:
        """Преобразовать объект в словарь"""
        return {
            'env_id': self.env_id,
            'type': self.type.value,
            'status': self.status,
            'config': self.config,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'resource_count': len(self.resources),
            'version': self.version,
            'isolation_level': self.isolation_level,
            'available': self.is_available()
        }