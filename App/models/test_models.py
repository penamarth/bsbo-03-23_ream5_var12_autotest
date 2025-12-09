from datetime import datetime
from typing import List, Dict, Optional, Any
import uuid
from enums import TestStatus


class TestCase:
    """Тест-кейс"""
    
    def __init__(self, name: str, script_path: str, expected_result: str, created_by: str = ""):
        self.test_id = str(uuid.uuid4())[:8]
        self.name = name
        self.script_path = script_path
        self.expected_result = expected_result
        self.created_by = created_by
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.tags: List[str] = []
        self.dependencies: List[str] = []
        self.timeout: int = 30  # секунд по умолчанию
    
    def execute(self, environment) -> 'TestResult':
        """Выполнение тест-кейса"""
        print(f"Выполнение тест-кейса: {self.name}")
        
        from services.test_runner import TestRunner
        runner = TestRunner()
        return runner.run_test(self, environment)
    
    def add_tag(self, tag: str) -> None:
        """Добавление тега к тест-кейсу"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def add_dependency(self, test_id: str) -> None:
        """Добавление зависимости от другого теста"""
        if test_id not in self.dependencies:
            self.dependencies.append(test_id)
    
    def __str__(self) -> str:
        return f"TestCase[{self.test_id}]: {self.name}"
    
    def to_dict(self) -> dict:
        """Преобразовать объект в словарь"""
        return {
            'test_id': self.test_id,
            'name': self.name,
            'script_path': self.script_path,
            'expected_result': self.expected_result,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'tags': self.tags,
            'dependencies': self.dependencies,
            'timeout': self.timeout
        }


class TestSuite:
    """Тест-сьют (набор тест-кейсов)"""
    
    def __init__(self, name: str, created_by: str = ""):
        self.suite_id = str(uuid.uuid4())[:8]
        self.name = name
        self.tests: List[TestCase] = []
        self.created_by = created_by
        self.created_at = datetime.now()
        self.description: str = ""
        self.category: str = "regression"
    
    def add_test(self, test: TestCase) -> None:
        """Добавление тест-кейса в сьют"""
        if test not in self.tests:
            self.tests.append(test)
            print(f"Тест {test.name} добавлен в сьют {self.name}")
    
    def remove_test(self, test_id: str) -> bool:
        """Удаление тест-кейса из сьюта"""
        for test in self.tests:
            if test.test_id == test_id:
                self.tests.remove(test)
                print(f"Тест {test.name} удален из сьюта {self.name}")
                return True
        return False
    
    def run_all(self, environment) -> List['TestResult']:
        """Выполнение всех тестов сьюта"""
        results = []
        for test in self.tests:
            result = test.execute(environment)
            results.append(result)
        return results
    
    def get_test_by_id(self, test_id: str) -> Optional[TestCase]:
        """Получение тест-кейса по ID"""
        for test in self.tests:
            if test.test_id == test_id:
                return test
        return None
    
    def __str__(self) -> str:
        return f"TestSuite[{self.suite_id}]: {self.name} ({len(self.tests)} тестов)"
    
    def to_dict(self) -> dict:
        """Преобразовать объект в словарь"""
        return {
            'suite_id': self.suite_id,
            'name': self.name,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'test_count': len(self.tests),
            'description': self.description,
            'category': self.category
        }


class TestResult:
    """Результат выполнения теста"""
    
    def __init__(self, test_case: TestCase, status: TestStatus, details: str = ""):
        self.test_case = test_case
        self.status = status
        self.details = details
        self.execution_time = datetime.now()
        self.duration: Optional[float] = None
        self.logs: List[str] = []
        self.screenshots: List[str] = []
        self.error_stack: Optional[str] = None
    
    def add_log(self, log_message: str) -> None:
        """Добавление лога к результату"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.logs.append(f"[{timestamp}] {log_message}")
    
    def add_screenshot(self, screenshot_path: str) -> None:
        """Добавление скриншота"""
        self.screenshots.append(screenshot_path)
    
    def set_error(self, error_message: str, stack_trace: str = "") -> None:
        """Установка информации об ошибке"""
        self.details = error_message
        self.error_stack = stack_trace
    
    def is_successful(self) -> bool:
        """Проверка успешности выполнения"""
        return self.status == TestStatus.SUCCESS
    
    def __str__(self) -> str:
        return f"TestResult[{self.test_case.name}]: {self.status.value}"
    
    def to_dict(self) -> dict:
        """Преобразовать объект в словарь"""
        return {
            'test_name': self.test_case.name,
            'test_id': self.test_case.test_id,
            'status': self.status.value,
            'details': self.details,
            'execution_time': self.execution_time.isoformat(),
            'duration': self.duration,
            'log_count': len(self.logs),
            'screenshot_count': len(self.screenshots),
            'has_error': self.error_stack is not None
        }