from abc import ABC, abstractmethod
from typing import List, Dict
from datetime import datetime


class TestExecutionStrategy(ABC):
    @abstractmethod
    def run_tests(
        self,
        tests: List["TestCase"],
        env_manager: "EnvironmentManager"
    ) -> List["TestResult"]:
        pass


class SequentialExecutionStrategy(TestExecutionStrategy):
    def run_tests(self, tests: List["TestCase"], env_manager: "EnvironmentManager") -> List["TestResult"]:
        print("Используется последовательная стратегия")
        results = []

        if not env_manager.environment.is_ready:
            return [
                TestResult(f"res_{t.test_id}", "FAIL", "Окружение не готово")
                for t in tests
            ]

        for test in tests:
            results.append(
                TestResult(
                    result_id=f"res_{test.test_id}",
                    status="PASS",
                    actual_result=f"Тест '{test.name}' выполнен успешно"
                )
            )
        return results
class ParallelExecutionStrategy(TestExecutionStrategy):
    def run_tests(self, tests: List["TestCase"], env_manager: "EnvironmentManager") -> List["TestResult"]:
        print("Используется параллельная стратегия")

        if not env_manager.environment.is_ready:
            return [
                TestResult(f"res_{t.test_id}", "FAIL", "Окружение не готово")
                for t in tests
            ]

        return [
            TestResult(
                f"res_{t.test_id}",
                "PASS",
                f"Параллельный запуск теста '{t.name}'"
            )
            for t in tests
        ]
class User:
    def __init__(self, user_id: str, name: str, role: str):
        self.user_id = user_id
        self.name = name
        self.role = role


class Developer(User):
    def create_test(self, test_id: str, name: str, script_path: str, expected_result: str) -> "TestCase":
        return TestCase(test_id, name, script_path, expected_result)

    def start_test_session(
        self,
        suite: "TestSuite",
        strategy: TestExecutionStrategy | None = None
    ) -> "TestSession":
        controller = TestController()
        return controller.start_session(suite, strategy)

    def stop_test_session(self, session: "TestSession") -> None:
        controller = TestController()
        controller.stop_session(session)


class TestCase:
    def __init__(self, test_id: str, name: str, script_path: str, expected_result: str):
        self.test_id = test_id
        self.name = name
        self.script_path = script_path
        self.expected_result = expected_result


class TestSuite:
    def __init__(self, suite_id: str, name: str):
        self.suite_id = suite_id
        self.name = name
        self.tests: List[TestCase] = []

    def add_test(self, test: TestCase) -> None:
        self.tests.append(test)

class Environment:
    def __init__(self, env_id: str, env_type: str, config: Dict[str, str]):
        self.env_id = env_id
        self.env_type = env_type
        self.config = config
        self.is_ready = False


class EnvironmentManager:
    def __init__(self):
        self.environment = Environment("env_1", "TEST", {"url": "localhost"})

    def setup_environment(self) -> None:
        print("Окружение подготовлено")
        self.environment.is_ready = True

    def teardown_environment(self) -> None:
        print("Окружение очищено")
        self.environment.is_ready = False

class TestRunner:
    def __init__(self, strategy: TestExecutionStrategy):
        self.strategy = strategy
        self.env_manager = EnvironmentManager()

    def run_suite(self, suite: TestSuite) -> List["TestResult"]:
        self.env_manager.setup_environment()
        results = self.strategy.run_tests(suite.tests, self.env_manager)
        self.env_manager.teardown_environment()
        return results

    def change_strategy(self, new_strategy: TestExecutionStrategy) -> None:
        print(f"Смена стратегии на {new_strategy.__class__.__name__}")
        self.strategy = new_strategy


class TestSession:
    def __init__(self, session_id: str, test_suite: TestSuite, runner: TestRunner):
        self.session_id = session_id
        self.status = "RUNNING"
        self.start_time = datetime.now()
        self.end_time: datetime | None = None
        self.test_suite = test_suite
        self.runner = runner
        self.results: List[TestResult] = []

    def run(self) -> List["TestResult"]:
        self.results = self.runner.run_suite(self.test_suite)
        return self.results

    def finish(self) -> "TestReport":
        self.status = "FINISHED"
        self.end_time = datetime.now()
        return TestReport.from_results(self.session_id, self.results)


class TestController:
    def start_session(
        self,
        suite: TestSuite,
        strategy: TestExecutionStrategy | None = None
    ) -> TestSession:
        runner = TestRunner(strategy or SequentialExecutionStrategy())
        return TestSession(
            session_id=f"sess_{int(datetime.now().timestamp())}",
            test_suite=suite,
            runner=runner
        )

    def stop_session(self, session: TestSession) -> None:
        session.status = "STOPPED"
        session.end_time = datetime.now()

class TestResult:
    def __init__(self, result_id: str, status: str, actual_result: str):
        self.result_id = result_id
        self.status = status
        self.actual_result = actual_result


class TestReport:
    def __init__(self, report_id: str, created_at: datetime, results: List[TestResult]):
        self.report_id = report_id
        self.created_at = created_at
        self.results = results

    @classmethod
    def from_results(cls, session_id: str, results: List[TestResult]) -> "TestReport":
        return cls(
            report_id=f"rep_{session_id}",
            created_at=datetime.now(),
            results=results
        )

if __name__ == "__main__":
    dev = Developer("user_1", "Maxim", "Developer")

    test1 = dev.create_test("1", "Login Test", "/login.py", "OK")
    test2 = dev.create_test("2", "Logout Test", "/logout.py", "OK")

    suite = TestSuite("suite_1", "Auth Suite")
    suite.add_test(test1)
    suite.add_test(test2)

    print("\n=== Последовательная стратегия ===")
    session = dev.start_test_session(suite)
    results = session.run()
    report = session.finish()

    for r in results:
        print(f"{r.result_id}: {r.status} — {r.actual_result}")

    print("\n=== Параллельная стратегия ===")
    parallel_session = dev.start_test_session(suite, ParallelExecutionStrategy())
    results = parallel_session.run()

    for r in results:
        print(f"{r.result_id}: {r.status} — {r.actual_result}")
