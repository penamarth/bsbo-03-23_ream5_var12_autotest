from typing import List, Optional, Dict, Any
from datetime import datetime
from models.report import TestReport, TestSession
from models.user import User


class ReportGenerator:
    """Генератор отчетов"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._generated_reports = {}
            cls._instance._statistics = {
                'total_generated': 0,
                'last_generated': None
            }
        return cls._instance
    
    @classmethod
    def get_instance(cls):
        """Получение экземпляра синглтона"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def generate_report(self, test_session: TestSession) -> TestReport:
        """Генерация отчета по тестовой сессии"""
        print(f"ReportGenerator: генерация отчета для сессии {test_session.session_id}")
        
        report = TestReport(test_session)
        self._generated_reports[report.report_id] = report
        self._statistics['total_generated'] += 1
        self._statistics['last_generated'] = datetime.now().isoformat()
        
        print(f"Отчет {report.report_id} успешно сгенерирован")
        return report
    
    def send_notification(self, report: TestReport, user: User) -> None:
        """Отправка уведомления пользователю"""
        print(f"ReportGenerator: отправка уведомления пользователю {user.name}")
        print(f"Отчет {report.report_id} готов к просмотру")
        
        notification_message = f"""
        Уведомление от системы автоматического тестирования
        
        Уважаемый(ая) {user.name},
        
        Тестовая сессия {report.test_session.session_id} завершена.
        
        Основные метрики:
        - Тест-сьют: {report.content.get('test_suite', 'N/A')}
        - Всего тестов: {report.content.get('statistics', {}).get('total', 0)}
        - Успешных: {report.content.get('statistics', {}).get('success', 0)}
        - Неудачных: {report.content.get('statistics', {}).get('failure', 0)}
        - Успешность: {report.content.get('success_rate', 0):.1f}%
        
        Для просмотра подробного отчета обратитесь в систему.
        
        С уважением,
        Система автоматического тестирования
        """
        
        print(f"Уведомление отправлено:\n{notification_message}")
    
    def get_report_by_id(self, report_id: str) -> Optional[TestReport]:
        """Получение отчета по ID"""
        return self._generated_reports.get(report_id)
    
    def get_session_report(self, session_id: str) -> Optional[TestReport]:
        """Получение отчета по ID сессии"""
        for report in self._generated_reports.values():
            if report.test_session.session_id == session_id:
                return report
        return None
    
    def export_report(self, report_id: str, format: str = "json") -> Optional[str]:
        """Экспорт отчета в указанном формате"""
        report = self.get_report_by_id(report_id)
        if report:
            return report.export(format)
        return None
    
    def get_all_reports(self) -> List[TestReport]:
        """Получение всех отчетов"""
        return list(self._generated_reports.values())
    
    def get_reports_by_user(self, user_id: str) -> List[TestReport]:
        """Получение отчетов по пользователю"""
        user_reports = []
        for report in self._generated_reports.values():
            if report.test_session.initiated_by == user_id:
                user_reports.append(report)
        return user_reports
    
    def cleanup_old_reports(self, max_age_days: int = 30) -> int:
        """Очистка старых отчетов"""
        from datetime import datetime, timedelta
        
        cleanup_time = datetime.now() - timedelta(days=max_age_days)
        removed_count = 0
        
        report_ids_to_remove = []
        for report_id, report in self._generated_reports.items():
            if report.generated_at < cleanup_time:
                report_ids_to_remove.append(report_id)
        
        for report_id in report_ids_to_remove:
            del self._generated_reports[report_id]
            removed_count += 1
        
        print(f"Очищено {removed_count} старых отчетов")
        return removed_count
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики генератора отчетов"""
        return {
            **self._statistics,
            'stored_reports': len(self._generated_reports)
        }


class ReportService:
    """Сервис для работы с отчетами"""
    
    def __init__(self):
        self.report_generator = ReportGenerator.get_instance()
        self._session_cache: Dict[str, TestSession] = {}
    
    def get_available_sessions(self, user_id: Optional[str] = None) -> List[TestSession]:
        """Получение списка доступных сессий"""
        from services.test_controller import TestController
        
        controller = TestController.get_instance()
        all_sessions = controller.get_all_sessions()
        
        if user_id:
            return [session for session in all_sessions if session.initiated_by == user_id]
        
        return all_sessions
    
    def view_report(self, session_id: str, export_format: str = "json") -> Optional[str]:
        """Просмотр отчета"""
        report = self.report_generator.get_session_report(session_id)
        
        if not report:
            from services.test_controller import TestController
            controller = TestController.get_instance()
            session = controller.get_session_by_id(session_id)
            
            if session:
                report = self.report_generator.generate_report(session)
        
        if report:
            return report.export(export_format)
        
        return None
    
    def get_report_details(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Получение деталей отчета"""
        report = self.report_generator.get_session_report(session_id)
        if report:
            return {
                'report_info': report.to_dict(),
                'session_info': report.test_session.to_dict(),
                'statistics': report.content.get('statistics', {}),
                'available_formats': list(report.exports.keys())
            }
        return None
    
    def export_multiple_reports(self, session_ids: List[str], format: str = "json") -> Dict[str, str]:
        """Экспорт нескольких отчетов"""
        results = {}
        for session_id in session_ids:
            report_content = self.view_report(session_id, format)
            if report_content:
                results[session_id] = report_content
        
        return results
    
    def get_report_statistics(self) -> Dict[str, Any]:
        """Получение статистики по отчетам"""
        all_reports = self.report_generator.get_all_reports()
        total_reports = len(all_reports)
        
        if total_reports == 0:
            return {
                'total_reports': 0,
                'success_rate_avg': 0,
                'avg_duration': 0
            }
        
        total_success_rate = 0
        total_duration = 0
        
        for report in all_reports:
            total_success_rate += report.content.get('success_rate', 0)
            total_duration += report.content.get('duration', 0)
        
        return {
            'total_reports': total_reports,
            'success_rate_avg': total_success_rate / total_reports,
            'avg_duration': total_duration / total_reports,
            'generator_stats': self.report_generator.get_statistics()
        }