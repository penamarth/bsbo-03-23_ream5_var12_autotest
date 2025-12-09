import time
import random
from typing import List
from datetime import datetime
from enums import TestStatus
from models.test_models import TestCase, TestResult, TestSuite


class TestRunner:
    """Выполнение тестов"""
    
    def __init__(self):
        self.current_test: TestCase = None
        self.start_time: datetime = None
        self.execution_stats = {
            'total_executed': 0,
            'total_duration': 0.0
        }
    
    def run_test(self, test_case: TestCase, environment) -> TestResult:
        """Выполнение одного тест-кейса"""
        self.current_test = test_case
        self.start_time = datetime.now()
        
        print(f"TestRunner: выполняется тест {test_case.name}")
        
        execution_time = random.uniform(0.1, 2.0)
        time.sleep(execution_time)
        
        status = random.choices(
            [TestStatus.SUCCESS, TestStatus.FAILURE, TestStatus.ERROR],
            weights=[0.7, 0.2, 0.1]
        )[0]
        
        result = TestResult(test_case, status)
        result.duration = execution_time
        
        if status == TestStatus.SUCCESS:
            result.details = f"Тест '{test_case.name}' выполнен успешно"
            result.add_log(f"Ожидаемый результат: {test_case.expected_result}")
            result.add_log("Фактический результат соответствует ожидаемому")
        
        elif status == TestStatus.FAILURE:
            result.details = f"Тест '{test_case.name}' провален"
            result.add_log(f"Ожидалось: {test_case.expected_result}")
            result.add_log("Фактический результат не соответствует ожидаемому")

            result.add_screenshot(f"/screenshots/failure_{test_case.test_id}.png")
        
        elif status == TestStatus.ERROR:
            result.details = f"Ошибка выполнения теста '{test_case.name}'"
            result.add_log("Произошла ошибка во время выполнения")
            result.set_error(
                "RuntimeError: Something went wrong",
                "Traceback (most recent call last):\n  File 'test.py', line 10, in test_function\n    raise RuntimeError('Something went wrong')\nRuntimeError: Something went wrong"
            )
        
        result.add_log(f"Время выполнения: {execution_time:.2f} секунд")
        result.add_log(f"Тестовая среда: {environment.env_id}")
        
        self.execution_stats['total_executed'] += 1
        self.execution_stats['total_duration'] += execution_time
        
        return result
    
    def run_suite(self, test_suite: TestSuite, environment) -> List[TestResult]:
        """Выполнение всего тест-сьюта"""
        print(f"TestRunner: выполняется сьют {test_suite.name}")
        
        results = []
        suite_start = datetime.now()
        
        for i, test_case in enumerate(test_suite.tests, 1):
            print(f"  [{i}/{len(test_suite.tests)}] Запуск теста: {test_case.name}")
            result = self.run_test(test_case, environment)
            results.append(result)
        
        suite_duration = (datetime.now() - suite_start).total_seconds()
        print(f"TestRunner: сьют {test_suite.name} выполнен за {suite_duration:.2f} секунд")
        
        return results
    
    def get_stats(self) -> dict:
        """Получение статистики выполнения"""
        avg_duration = (
            self.execution_stats['total_duration'] / self.execution_stats['total_executed']
            if self.execution_stats['total_executed'] > 0 else 0
        )
        
        return {
            **self.execution_stats,
            'average_duration': avg_duration
        }