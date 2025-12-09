import uuid
from datetime import datetime
from enums import TestStatus

class TestCase:
    def __init__(self, name: str, script_path: str, expected_result: str):
        self.testId = str(uuid.uuid4())[:8]
        self.name = name
        self.scriptPath = script_path
        self.expectedResult = expected_result

    def execute(self, environment):
        from services.test_runner import TestRunner
        runner = TestRunner()
        return runner.runTest(self, environment)

    def __str__(self):
        return f"TestCase[{self.testId}]: {self.name}"


class TestSuite:
    def __init__(self, name: str):
        self.suiteId = str(uuid.uuid4())[:8]
        self.name = name
        self.tests = []

    def addTest(self, test: TestCase):
        self.tests.append(test)

    def runAll(self, environment):
        results = []
        for test in self.tests:
            result = test.execute(environment)
            results.append(result)
        return results

    def __str__(self):
        return f"TestSuite[{self.suiteId}]: {self.name} ({len(self.tests)} tests)"


class TestResult:
    def __init__(self, test_case: TestCase, status: TestStatus, details: str = ""):
        self.test_case = test_case
        self.status = status
        self.details = details
        self.execution_time = datetime.now()

    def __str__(self):
        return f"TestResult[{self.test_case.name}]: {self.status.value}"