import time
import random
from enums import TestStatus
from models.test_models import TestResult


class TestRunner:
    def runTest(self, test, env):
        print(f"TestRunner: выполнение теста {test.name}")
        time.sleep(random.uniform(0.1, 0.5))
        
        status = random.choice([
            TestStatus.SUCCESS, 
            TestStatus.SUCCESS, 
            TestStatus.FAILURE,
            TestStatus.ERROR
        ])
        
        details = "Тест выполнен успешно" if status == TestStatus.SUCCESS else "Тест не пройден"
        return TestResult(test, status, details)

    def runSuite(self, suite, env):
        print(f"TestRunner: выполнение сьюта {suite.name}")
        results = []
        for test in suite.tests:
            result = self.runTest(test, env)
            results.append(result)
        return results