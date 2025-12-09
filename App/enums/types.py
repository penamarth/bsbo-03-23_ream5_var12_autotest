from enum import Enum

class UserRole(Enum):
    """Роли пользователей системы"""
    DEVELOPER = "Разработчик"
    QA_ENGINEER = "QA-инженер"
    DEVOPS = "DevOps-инженер"
    MANAGER = "Менеджер проекта"
    SYSTEM_ADMIN = "Системный администратор"


class EnvironmentType(Enum):
    """Типы тестовых сред"""
    DEVELOPMENT = "dev"
    STAGING = "staging"
    PRODUCTION_LIKE = "production-like"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"


class ResourceType(Enum):
    """Типы ресурсов"""
    VM = "Виртуальная машина"
    CONTAINER = "Контейнер"
    DATABASE = "База данных"
    NETWORK = "Сетевое хранилище"
    SERVICE = "Внешний сервис"
    GPU = "Графический процессор"
    MEMORY = "Память"