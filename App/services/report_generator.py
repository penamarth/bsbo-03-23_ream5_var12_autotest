import json
from models.report import TestReport


class ReportGenerator:
    def generateReport(self, session):
        print(f"ReportGenerator: генерация отчета для сессии {session.sessionId}")
        
        content = {
            "session_id": session.sessionId,
            "start_time": session.startTime.isoformat(),
            "end_time": session.endTime.isoformat() if session.endTime else None,
            "status": session.status,
            "environment": session.environment.envId,
            "test_suite": session.test_suite.name,
            "results": [
                {
                    "test_name": r.test_case.name,
                    "status": r.status.value,
                    "details": r.details
                }
                for r in session.results
            ]
        }
        
        report_content = json.dumps(content, indent=2, ensure_ascii=False)
        report = TestReport(report_content, "json")
        return report

    def sendNotification(self, report):
        print(f"ReportGenerator: отправка уведомления об отчете {report.reportId}")