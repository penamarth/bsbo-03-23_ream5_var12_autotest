import uuid
from datetime import datetime
from enums import SessionStatus

class TestSession:
    def __init__(self, test_suite, environment):
        self.sessionId = str(uuid.uuid4())[:8]
        self.startTime = datetime.now()
        self.endTime = None
        self.status = SessionStatus.INITIALIZED.value
        self.test_suite = test_suite
        self.environment = environment
        self.results = []
        self.report = None

    def generateReport(self):
        from services.report_generator import ReportGenerator
        generator = ReportGenerator()
        self.report = generator.generateReport(self)
        return self.report

    def __str__(self):
        duration = (self.endTime - self.startTime).total_seconds() if self.endTime else 0
        return f"TestSession[{self.sessionId}]: {self.status} ({duration:.2f} сек)"


class TestReport:
    def __init__(self, content: str, format: str = "json"):
        self.reportId = str(uuid.uuid4())[:8]
        self.content = content
        self.format = format

    def export(self, format: str):
        return f"Report exported in {format} format"

    def __str__(self):
        return f"TestReport[{self.reportId}]: format={self.format}"