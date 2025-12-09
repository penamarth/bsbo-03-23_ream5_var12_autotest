from typing import List, Dict, Any, Optional
from datetime import datetime
from enums import SessionStatus
from models.test_models import TestSuite, TestResult
from models.environment import Environment
from models.report import TestSession, TestReport
from services.test_runner import TestRunner
from services.environment_manager import EnvironmentManager
from services.resource_manager import ResourceManager
from services.report_service import ReportGenerator


class TestController:
    """Контроллер тестирования (оркестратор)"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._active_sessions = {}
            cls._instance._completed_sessions = {}
            cls._instance._statistics = {
                'total_sessions': 0,
                'successful_sessions': 0,
                'failed_sessions': 0,
                'cancelled_sessions': 0
            }
        return cls._instance
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def start_test_session(self, test_suite: TestSuite, 
                          environment: Environment,
                          initiated_by: str = "") -> TestSession:
        print(f"TestController: запуск тестовой сессии для сьюта {test_suite.name}")
        
        if not environment.is_available():
            raise ValueError(f"Среда {environment.env_id} недоступна")
        
        session = TestSession(test_suite, environment, initiated_by)
        session.status = SessionStatus.RUNNING.value
        self._active_sessions[session.session_id] = session
        self._statistics['total_sessions'] += 1
        
        try:
            resource_manager = ResourceManager()
            session.metadata['resource_manager'] = resource_manager.get_statistics()
            
            runner = TestRunner()
            print(f"Выполнение тестов сьюта {test_suite.name}...")
            
            results = runner.run_suite(test_suite, environment)
            for result in results:
                session.add_result(result)
            
            session.metadata['test_runner_stats'] = runner.get_stats()
            
            report_gen = ReportGenerator.get_instance()
            session.report = report_gen.generate_report(session)
            
            session.complete(SessionStatus.COMPLETED)
            
            resources_freed = resource_manager.release_session_resources(session.session_id)
            session.metadata['resources_freed'] = resources_freed
            
            self._active_sessions.pop(session.session_id, None)
            self._completed_sessions[session.session_id] = session
            self._statistics['successful_sessions'] += 1
            
            if initiated_by:
                print(f"Сессия {session.session_id} успешно завершена. Инициатор: {initiated_by}")
            
            return session
            
        except Exception as e:
            print(f"Ошибка во время выполнения тестовой сессии: {e}")
            session.complete(SessionStatus.FAILED)
            session.metadata['error'] = str(e)
            
            resource_manager = ResourceManager()
            resource_manager.release_session_resources(session.session_id)
            
            self._active_sessions.pop(session.session_id, None)
            self._completed_sessions[session.session_id] = session
            self._statistics['failed_sessions'] += 1
            
            raise
    
    def stop_test_session(self, session_id: str) -> bool:
        session = self._active_sessions.get(session_id)
        
        if not session:
            print(f"Сессия {session_id} не найдена или уже завершена")
            return False
        
        print(f"TestController: остановка сессии {session_id}")
        
        session.complete(SessionStatus.CANCELLED)
        session.metadata['cancelled_at'] = datetime.now().isoformat()
        
        resource_manager = ResourceManager()
        resources_freed = resource_manager.release_session_resources(session_id)
        session.metadata['resources_freed_on_cancel'] = resources_freed
        
        self._active_sessions.pop(session_id, None)
        self._completed_sessions[session_id] = session
        self._statistics['cancelled_sessions'] += 1
        
        print(f"Сессия {session_id} успешно остановлена")
        return True
    
    def get_session_by_id(self, session_id: str) -> Optional[TestSession]:
        session = self._active_sessions.get(session_id)
        if session:
            return session
        
        return self._completed_sessions.get(session_id)
    
    def get_session_report(self, session_id: str) -> Optional[TestReport]:
        session = self.get_session_by_id(session_id)
        if session:
            return session.report
        return None
    
    def get_all_sessions(self) -> List[TestSession]:
        all_sessions = list(self._active_sessions.values()) + list(self._completed_sessions.values())
        return sorted(all_sessions, key=lambda s: s.start_time, reverse=True)
    
    def get_active_sessions(self) -> List[TestSession]:
        return list(self._active_sessions.values())
    
    def get_completed_sessions(self) -> List[TestSession]:
        return list(self._completed_sessions.values())
    
    def get_sessions_by_user(self, user_id: str) -> List[TestSession]:
        all_sessions = self.get_all_sessions()
        return [session for session in all_sessions if session.initiated_by == user_id]
    
    def get_sessions_by_status(self, status: SessionStatus) -> List[TestSession]:
        all_sessions = self.get_all_sessions()
        return [session for session in all_sessions if session.status == status.value]
    
    def cleanup_old_sessions(self, max_age_days: int = 30) -> int:
        from datetime import datetime, timedelta
        
        cleanup_time = datetime.now() - timedelta(days=max_age_days)
        removed_count = 0
        
        session_ids_to_remove = []
        for session_id, session in self._completed_sessions.items():
            if session.end_time and session.end_time < cleanup_time:
                session_ids_to_remove.append(session_id)
        
        for session_id in session_ids_to_remove:
            del self._completed_sessions[session_id]
            removed_count += 1
        
        print(f"Очищено {removed_count} старых сессий")
        return removed_count
    
    def get_statistics(self) -> Dict[str, Any]:
        active_sessions = len(self._active_sessions)
        completed_sessions = len(self._completed_sessions)
        
        total_results = 0
        total_success = 0
        
        for session in self._completed_sessions.values():
            stats = session.get_statistics()
            total_results += stats['total']
            total_success += stats['success']
        
        overall_success_rate = (total_success / total_results * 100) if total_results > 0 else 0
        
        return {
            **self._statistics,
            'active_sessions': active_sessions,
            'completed_sessions': completed_sessions,
            'total_results': total_results,
            'total_success': total_success,
            'overall_success_rate': overall_success_rate
        }