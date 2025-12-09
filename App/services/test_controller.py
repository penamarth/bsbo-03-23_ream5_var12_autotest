from datetime import datetime
from models.report import TestSession
from services.test_runner import TestRunner
from services.environment_manager import EnvironmentManager
from services.resource_manager import ResourceManager
from services.report_generator import ReportGenerator


class TestController:
    def __init__(self):
        self.test_runner = TestRunner()
        self.environment_manager = EnvironmentManager()
        self.resource_manager = ResourceManager()
        self.report_generator = ReportGenerator()

    def startTestSession(self, suite, env):
        print(f"TestController: запуск тестовой сессии для сьюта {suite.name}")
        
        if not env.isAvailable():
            raise Exception(f"Среда {env.envId} недоступна")
        
        session = TestSession(suite, env)
        session.status = "running"
        
        results = self.test_runner.runSuite(suite, env)
        session.results = results
        
        session.report = self.report_generator.generateReport(session)
        
        session.status = "completed"
        session.endTime = datetime.now()
        
        return session

    def stopTestSession(self, session):
        session.status = "cancelled"
        session.endTime = datetime.now()