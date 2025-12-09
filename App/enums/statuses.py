from enum import Enum

class TestStatus(Enum):
    """Статусы выполнения теста"""
    SUCCESS = "Успех"
    FAILURE = "Неудача"
    SKIPPED = "Пропущен"
    ERROR = "Ошибка"
    PENDING = "В ожидании"
    RUNNING = "Выполняется"


class SessionStatus(Enum):
    """Статусы тестовой сессии"""
    INITIALIZED = "initialized"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ResourceStatus(Enum):
    """Статусы ресурсов"""
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"