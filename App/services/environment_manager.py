from typing import Dict, List, Any, Optional
import uuid
from datetime import datetime
from enums import EnvironmentType, ResourceType
from models.environment import Environment, Resource


class EnvironmentManager:
    """Управление тестовыми средами"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._environments = {}
            cls._instance._templates = {}
        return cls._instance
    
    @classmethod
    def get_instance(cls):
        """Получение экземпляра синглтона"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def setup_environment(self, env_type: EnvironmentType, config: Dict[str, Any]) -> Environment:
        """Настройка тестовой среды"""
        env_id = str(uuid.uuid4())[:8]
        print(f"EnvironmentManager: настройка среды {env_id} типа {env_type.value}")
        
        base_config = {
            "name": f"{env_type.value}_environment",
            "description": f"Автоматически созданная среда для {env_type.value}",
            "auto_cleanup": True,
            "retention_days": 7,
            **config
        }
        
        environment = Environment(env_id, env_type, base_config)
        
        self._create_default_resources(environment)
        
        self._environments[env_id] = environment
        return environment
    
    def _create_default_resources(self, environment: Environment) -> None:
        """Создание ресурсов по умолчанию для среды"""
        resource_map = {
            EnvironmentType.DEVELOPMENT: [
                (ResourceType.VM, 2),
                (ResourceType.DATABASE, 1),
                (ResourceType.NETWORK, 1)
            ],
            EnvironmentType.STAGING: [
                (ResourceType.VM, 4),
                (ResourceType.CONTAINER, 2),
                (ResourceType.DATABASE, 1),
                (ResourceType.NETWORK, 1),
                (ResourceType.SERVICE, 2)
            ],
            EnvironmentType.PRODUCTION_LIKE: [
                (ResourceType.VM, 8),
                (ResourceType.CONTAINER, 4),
                (ResourceType.DATABASE, 2),
                (ResourceType.NETWORK, 2),
                (ResourceType.SERVICE, 4)
            ]
        }
        
        resources_config = resource_map.get(environment.type, [
            (ResourceType.VM, 2),
            (ResourceType.DATABASE, 1)
        ])
        
        for resource_type, count in resources_config:
            for i in range(count):
                resource_id = f"{resource_type.value[:3]}-{i+1}-{environment.env_id[:4]}"
                resource = Resource(resource_id, resource_type.value)
                
                if resource_type == ResourceType.VM:
                    resource.set_capacity(cpu=2, memory=2048, storage=10240)
                elif resource_type == ResourceType.CONTAINER:
                    resource.set_capacity(cpu=1, memory=1024, storage=5120)
                elif resource_type == ResourceType.DATABASE:
                    resource.set_capacity(cpu=2, memory=4096, storage=20480)
                
                resource.add_tag(environment.type.value)
                environment.add_resource(resource)
    
    def teardown_environment(self, environment: Environment) -> None:
        """Удаление тестовой среды"""
        print(f"EnvironmentManager: удаление среды {environment.env_id}")
        
        for resource in environment.resources:
            resource.release()
        
        if environment.env_id in self._environments:
            del self._environments[environment.env_id]
            print(f"Среда {environment.env_id} успешно удалена")
    
    def get_available_environments(self) -> List[Environment]:
        """Получение списка доступных сред"""
        return [env for env in self._environments.values() if env.is_available()]
    
    def get_environment_by_id(self, env_id: str) -> Optional[Environment]:
        """Получение среды по ID"""
        return self._environments.get(env_id)
    
    def get_environments_by_type(self, env_type: EnvironmentType) -> List[Environment]:
        """Получение сред по типу"""
        return [env for env in self._environments.values() if env.type == env_type]
    
    def save_template(self, name: str, config: Dict[str, Any]) -> str:
        """Сохранение шаблона среды"""
        template_id = str(uuid.uuid4())[:8]
        self._templates[template_id] = {
            'id': template_id,
            'name': name,
            'config': config,
            'created_at': datetime.now().isoformat()
        }
        print(f"Шаблон '{name}' сохранен с ID: {template_id}")
        return template_id
    
    def create_from_template(self, template_id: str, env_type: EnvironmentType) -> Optional[Environment]:
        """Создание среды из шаблона"""
        template = self._templates.get(template_id)
        if template:
            return self.setup_environment(env_type, template['config'])
        return None
    
    def get_all_environments(self) -> List[Environment]:
        """Получение всех сред"""
        return list(self._environments.values())
    
    def cleanup_inactive_environments(self, max_age_hours: int = 24) -> int:
        """Очистка неактивных сред"""
        from datetime import datetime, timedelta
        
        cleanup_time = datetime.now() - timedelta(hours=max_age_hours)
        removed_count = 0
        
        env_ids_to_remove = []
        for env_id, env in self._environments.items():
            if env.updated_at < cleanup_time and not env.resources:
                env_ids_to_remove.append(env_id)
        
        for env_id in env_ids_to_remove:
            self.teardown_environment(self._environments[env_id])
            removed_count += 1
        
        print(f"Очищено {removed_count} неактивных сред")
        return removed_count