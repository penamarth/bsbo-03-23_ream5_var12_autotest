from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid
import json
from enums import SessionStatus, TestStatus


class TestSession:
    """Сессия тестирования"""
    
    def __init__(self, test_suite, environment, initiated_by: str = ""):
        self.session_id = str(uuid.uuid4())[:8]
        self.test_suite = test_suite
        self.environment = environment
        self.initiated_by = initiated_by
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.status = SessionStatus.INITIALIZED.value
        self.results: List[Any] = []  # List[TestResult]
        self.report: Optional['TestReport'] = None
        self.metadata: Dict[str, Any] = {}
        self.tags: List[str] = []
    
    def generate_report(self) -> 'TestReport':
        """Генерация отчета по сессии"""
        print(f"Генерация отчета для сессии {self.session_id}")
        
        from services.report_service import ReportGenerator
        report_gen = ReportGenerator()
        self.report = report_gen.generate_report(self)
        return self.report
    
    def complete(self, status: SessionStatus = SessionStatus.COMPLETED) -> None:
        """Завершение тестовой сессии"""
        self.end_time = datetime.now()
        self.status = status.value
        self.metadata['duration'] = (self.end_time - self.start_time).total_seconds()
        print(f"Тестовая сессия {self.session_id} завершена со статусом: {self.status}")
    
    def add_result(self, result) -> None:
        """Добавление результата теста"""
        self.results.append(result)
    
    def get_statistics(self) -> Dict[str, int]:
        """Получение статистики по результатам"""
        stats = {
            'total': len(self.results),
            'success': 0,
            'failure': 0,
            'error': 0,
            'skipped': 0
        }
        
        for result in self.results:
            if result.status == TestStatus.SUCCESS:
                stats['success'] += 1
            elif result.status == TestStatus.FAILURE:
                stats['failure'] += 1
            elif result.status == TestStatus.ERROR:
                stats['error'] += 1
            elif result.status == TestStatus.SKIPPED:
                stats['skipped'] += 1
        
        return stats
    
    def add_tag(self, tag: str) -> None:
        """Добавление тега к сессии"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def __str__(self) -> str:
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0
        return f"TestSession[{self.session_id}]: {self.status} ({duration:.2f} сек)"
    
    def to_dict(self) -> dict:
        """Преобразовать объект в словарь"""
        stats = self.get_statistics()
        return {
            'session_id': self.session_id,
            'test_suite': self.test_suite.name if self.test_suite else None,
            'environment': self.environment.env_id if self.environment else None,
            'initiated_by': self.initiated_by,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'result_count': len(self.results),
            'statistics': stats,
            'tags': self.tags,
            'metadata': self.metadata,
            'has_report': self.report is not None
        }


class TestReport:
    """Отчет о тестировании"""
    
    def __init__(self, test_session):
        self.report_id = str(uuid.uuid4())[:8]
        self.test_session = test_session
        self.generated_at = datetime.now()
        self.content = self._generate_content()
        self.format_version: str = "1.0"
        self.exports: Dict[str, str] = {}  # format -> content
    
    def _generate_content(self) -> Dict[str, Any]:
        """Генерация содержания отчета"""
        session = self.test_session
        stats = session.get_statistics()
        
        content = {
            "report_id": self.report_id,
            "session_id": session.session_id,
            "test_suite": session.test_suite.name if session.test_suite else "N/A",
            "environment": session.environment.env_id if session.environment else "N/A",
            "initiated_by": session.initiated_by,
            "start_time": session.start_time.isoformat(),
            "end_time": session.end_time.isoformat() if session.end_time else None,
            "duration": session.metadata.get('duration', 0),
            "generated_at": self.generated_at.isoformat(),
            "statistics": stats,
            "success_rate": (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0,
            "results_summary": [],
            "tags": session.tags,
            "metadata": session.metadata
        }
        
        for result in session.results[:10]: 
            content["results_summary"].append({
                "test_name": result.test_case.name,
                "status": result.status.value,
                "duration": result.duration,
                "has_error": result.error_stack is not None
            })
        
        return content
    
    def export(self, format: str = "json") -> str:
        """Экспорт отчета в разных форматах"""
        if format in self.exports:
            return self.exports[format]
        
        if format == "json":
            result = json.dumps(self.content, indent=2, ensure_ascii=False, default=str)
        elif format == "html":
            result = self._export_html()
        elif format == "text":
            result = self._export_text()
        elif format == "csv":
            result = self._export_csv()
        else:
            raise ValueError(f"Неподдерживаемый формат: {format}")
        
        self.exports[format] = result
        return result
    
    def _export_html(self) -> str:
        """Экспорт в HTML"""
        content = self.content
        stats = content['statistics']
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Отчет о тестировании</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .stats {{ display: flex; justify-content: space-between; margin: 20px 0; }}
                .stat-card {{ background-color: #e8f4fd; padding: 15px; border-radius: 5px; width: 18%; text-align: center; }}
                .success {{ color: green; font-weight: bold; }}
                .failure {{ color: red; font-weight: bold; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Отчет о тестировании</h1>
                <h2>Сессия: {content['session_id']}</h2>
                <p><strong>Тест-сьют:</strong> {content['test_suite']}</p>
                <p><strong>Среда:</strong> {content['environment']}</p>
                <p><strong>Время выполнения:</strong> {content['duration']:.2f} секунд</p>
                <p><strong>Успешность:</strong> {content['success_rate']:.1f}%</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <h3>Всего тестов</h3>
                    <p>{stats['total']}</p>
                </div>
                <div class="stat-card success">
                    <h3>Успешных</h3>
                    <p>{stats['success']}</p>
                </div>
                <div class="stat-card failure">
                    <h3>Неудачных</h3>
                    <p>{stats['failure']}</p>
                </div>
                <div class="stat-card">
                    <h3>Ошибок</h3>
                    <p>{stats['error']}</p>
                </div>
                <div class="stat-card">
                    <h3>Пропущено</h3>
                    <p>{stats['skipped']}</p>
                </div>
            </div>
            
            <h3>Сводка результатов</h3>
            <table>
                <tr>
                    <th>Тест</th>
                    <th>Статус</th>
                    <th>Длительность</th>
                </tr>
        """
        
        for result in content['results_summary']:
            status_class = "success" if result['status'] == "Успех" else "failure"
            html += f"""
                <tr>
                    <td>{result['test_name']}</td>
                    <td class="{status_class}">{result['status']}</td>
                    <td>{result['duration'] or 'N/A'}</td>
                </tr>
            """
        
        html += """
            </table>
            
            <div style="margin-top: 30px; color: #666; font-size: 12px;">
                <p>Сгенерировано: {}</p>
                <p>Версия отчета: {}</p>
            </div>
        </body>
        </html>
        """.format(content['generated_at'], self.format_version)
        
        return html
    
    def _export_text(self) -> str:
        """Экспорт в текстовом формате"""
        content = self.content
        stats = content['statistics']
        
        text = f"""
        {'=' * 60}
        ОТЧЕТ О ТЕСТИРОВАНИИ
        {'=' * 60}
        
        Сессия: {content['session_id']}
        Тест-сьют: {content['test_suite']}
        Среда: {content['environment']}
        Инициатор: {content['initiated_by']}
        Время выполнения: {content['duration']:.2f} секунд
        Успешность: {content['success_rate']:.1f}%
        
        {'-' * 60}
        СТАТИСТИКА:
        {'-' * 60}
        Всего тестов: {stats['total']}
        Успешных: {stats['success']}
        Неудачных: {stats['failure']}
        Ошибок: {stats['error']}
        Пропущено: {stats['skipped']}
        
        {'-' * 60}
        СВОДКА РЕЗУЛЬТАТОВ (первые 10):
        {'-' * 60}
        """
        
        for i, result in enumerate(content['results_summary'], 1):
            text += f"{i}. {result['test_name']} - {result['status']} ({result['duration'] or 'N/A'} сек)\n"
        
        text += f"""
        {'=' * 60}
        Сгенерировано: {content['generated_at']}
        Версия отчета: {self.format_version}
        {'=' * 60}
        """
        
        return text
    
    def _export_csv(self) -> str:
        """Экспорт в CSV формате"""
        content = self.content
        
        csv_lines = [
            "Параметр,Значение",
            f"ID отчета,{content['report_id']}",
            f"ID сессии,{content['session_id']}",
            f"Тест-сьют,{content['test_suite']}",
            f"Среда,{content['environment']}",
            f"Инициатор,{content['initiated_by']}",
            f"Начало,{content['start_time']}",
            f"Окончание,{content['end_time'] or 'N/A'}",
            f"Длительность,{content['duration']}",
            f"Успешность,{content['success_rate']}%",
            "",
            "Статистика",
            "Всего тестов," + str(content['statistics']['total']),
            "Успешных," + str(content['statistics']['success']),
            "Неудачных," + str(content['statistics']['failure']),
            "Ошибок," + str(content['statistics']['error']),
            "Пропущено," + str(content['statistics']['skipped']),
            "",
            "Результаты,Статус,Длительность"
        ]
        
        for result in content['results_summary']:
            csv_lines.append(f"{result['test_name']},{result['status']},{result['duration'] or ''}")
        
        return "\n".join(csv_lines)
    
    def __str__(self) -> str:
        return f"TestReport[{self.report_id}]: {self.test_session.session_id}"
    
    def to_dict(self) -> dict:
        """Преобразовать объект в словарь"""
        return {
            'report_id': self.report_id,
            'session_id': self.test_session.session_id,
            'generated_at': self.generated_at.isoformat(),
            'format_version': self.format_version,
            'available_formats': list(self.exports.keys())
        }