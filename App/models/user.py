from datetime import datetime
from typing import Optional
from enums import UserRole


class User:
    """Базовый класс пользователя системы"""
    
    def __init__(self, user_id: str, name: str, role: UserRole):
        self.user_id = user_id
        self.name = name
        self.role = role
        self.created_at = datetime.now()
        self.last_login: Optional[datetime] = None
        self.email: Optional[str] = None
        self.permissions: list = []
    
    def login(self) -> None:
        """Зарегистрировать вход пользователя"""
        self.last_login = datetime.now()
        print(f"Пользователь {self.name} вошел в систему")
    
    def has_permission(self, permission: str) -> bool:
        """Проверить наличие разрешения"""
        return permission in self.permissions
    
    def add_permission(self, permission: str) -> None:
        """Добавить разрешение пользователю"""
        if permission not in self.permissions:
            self.permissions.append(permission)
    
    def __str__(self) -> str:
        return f"{self.role.value}: {self.name} (ID: {self.user_id})"
    
    def to_dict(self) -> dict:
        """Преобразовать объект в словарь"""
        return {
            'user_id': self.user_id,
            'name': self.name,
            'role': self.role.value,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'email': self.email,
            'permissions': self.permissions
        }


class Developer(User):
    """Класс разработчика"""
    
    def __init__(self, user_id: str, name: str):
        super().__init__(user_id, name, UserRole.DEVELOPER)
        self.test_cases_created: int = 0
        self.test_sessions_run: int = 0
    
    def create_test_case(self, name: str, script_path: str, expected_result: str):
        """Создание тест-кейса"""
        print(f"{self.name} создает тест-кейс: {name}")
        self.test_cases_created += 1
        
        from models.test_models import TestCase
        return TestCase(name, script_path, expected_result, created_by=self.user_id)
    
    def run_test_suite(self, test_suite, environment):
        """Запуск тест-сьюта"""
        print(f"{self.name} запускает тест-сьют: {test_suite.name}")
        self.test_sessions_run += 1
        
        from services.test_controller import TestController
        controller = TestController.get_instance()
        return controller.start_test_session(test_suite, environment, self.user_id)
    
    def to_dict(self) -> dict:
        """Расширенный метод для разработчика"""
        base_dict = super().to_dict()
        base_dict.update({
            'test_cases_created': self.test_cases_created,
            'test_sessions_run': self.test_sessions_run
        })
        return base_dict


class QAEngineer(User):
    """Класс QA-инженера"""
    
    def __init__(self, user_id: str, name: str):
        super().__init__(user_id, name, UserRole.QA_ENGINEER)
        self.test_suites_managed: int = 0
        self.test_data_sets: list = []
    
    def create_test_suite(self, name: str):
        """Создание тест-сьюта"""
        print(f"{self.name} создает тест-сьют: {name}")
        self.test_suites_managed += 1
        
        from models.test_models import TestSuite
        return TestSuite(name, created_by=self.user_id)


class DevOps(User):
    """Класс DevOps-инженера"""
    
    def __init__(self, user_id: str, name: str):
        super().__init__(user_id, name, UserRole.DEVOPS)
        self.environments_configured: int = 0
    
    def configure_environment(self, env_type, config):
        """Настройка тестовой среды"""
        print(f"{self.name} настраивает среду типа: {env_type.value}")
        
        from services.environment_manager import EnvironmentManager
        env_manager = EnvironmentManager.get_instance()
        environment = env_manager.setup_environment(env_type, config)
        
        self.environments_configured += 1
        return environment