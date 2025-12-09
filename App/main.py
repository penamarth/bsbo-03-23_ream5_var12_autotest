import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import Developer, QAEngineer, DevOps, TestCase, TestSuite, Environment, Resource, TestSession, TestReport
from enums import UserRole, EnvironmentType, ResourceType, TestStatus, SessionStatus
from services import TestController, EnvironmentManager, ResourceManager, ReportService, TestRunner


class TestAutomationSystemDemo:
    
    def __init__(self):
        self.users = []
        self.test_suites = []
        self.environments = []
        self.sessions = []
        
    def run_demo(self):
        print("[ДЕМОНСТРАЦИЯ СИСТЕМЫ АВТОМАТИЧЕСКОГО ТЕСТИРОВАНИЯ]")
        
        try:
            self.demo_setup_users()
            self.demo_setup_environments()
            self.demo_create_test_cases()
            self.demo_run_test_session()
            self.demo_report_generation()
            self.demo_resource_management()
            self.demo_system_statistics()
            
            print("[ДЕМОНСТРАЦИЯ УСПЕШНО ЗАВЕРШЕНА!]")
            
        except Exception as e:
            print(f"\nОшибка во время демонстрации: {e}")
            import traceback
            traceback.print_exc()
    
    def demo_setup_users(self):
        print("\n1. НАСТРОЙКА ПОЛЬЗОВАТЕЛЕЙ")
        print("-" * 40)
        
        dev = Developer("dev-001", "Алексей Петров")
        dev.email = "alexey.petrov@example.com"
        dev.add_permission("create_tests")
        dev.add_permission("run_tests")
        dev.add_permission("view_reports")
        dev.login()
        
        qa = QAEngineer("qa-001", "Мария Сидорова")
        qa.email = "maria.sidorova@example.com"
        qa.add_permission("manage_test_suites")
        qa.add_permission("run_tests")
        qa.add_permission("view_all_reports")
        qa.login()
        
        devops = DevOps("devops-001", "Иван Кузнецов")
        devops.email = "ivan.kuznetsov@example.com"
        devops.add_permission("manage_environments")
        devops.add_permission("manage_resources")
        devops.add_permission("view_system_stats")
        devops.login()
        
        self.users = [dev, qa, devops]
        
        for user in self.users:
            print(f"Создан: {user}")
            print(f"  Email: {user.email}")
            print(f"  Разрешения: {', '.join(user.permissions)}")
    
    def demo_setup_environments(self):
        print("\n2. НАСТРОЙКА ТЕСТОВЫХ СРЕД")
        print("-" * 40)
        
        env_manager = EnvironmentManager.get_instance()
        
        dev_config = {
            "db_host": "localhost",
            "db_port": 5432,
            "api_url": "http://dev-api.example.com",
            "timeout": 30,
            "debug": True
        }
        
        dev_env = env_manager.setup_environment(EnvironmentType.DEVELOPMENT, dev_config)
        dev_env.version = "1.0.0"
        dev_env.isolation_level = "shared"
        
        staging_config = {
            "db_host": "staging-db.example.com",
            "db_port": 5432,
            "api_url": "http://staging-api.example.com",
            "timeout": 60,
            "load_balancer": "enabled",
            "monitoring": "enabled"
        }
        
        staging_env = env_manager.setup_environment(EnvironmentType.STAGING, staging_config)
        staging_env.version = "2.0.0"
        staging_env.isolation_level = "dedicated"
        
        self.environments = [dev_env, staging_env]
        
        for env in self.environments:
            print(f"Создана среда: {env}")
            print(f"  Тип: {env.type.value}")
            print(f"  Ресурсов: {len(env.resources)}")
            print(f"  Доступна: {'Да' if env.is_available() else 'Нет'}")
            print(f"  Конфигурация: {list(env.config.keys())}")
    
    def demo_create_test_cases(self):
        print("\n3. СОЗДАНИЕ ТЕСТ-КЕЙСОВ И ТЕСТ-СЬЮТОВ")
        print("-" * 40)
        
        developer = self.users[0]
        
        test_cases = [
            developer.create_test_case(
                "Тест авторизации пользователя",
                "/tests/auth/test_login.py",
                "Пользователь успешно авторизуется в системе"
            ),
            developer.create_test_case(
                "Тест создания нового заказа",
                "/tests/orders/test_create_order.py",
                "Новый заказ успешно создается в системе"
            ),
            developer.create_test_case(
                "Тест оплаты заказа",
                "/tests/payments/test_process_payment.py",
                "Оплата заказа проходит успешно"
            ),
            developer.create_test_case(
                "Тест отправки уведомления",
                "/tests/notifications/test_send_notification.py",
                "Уведомление успешно отправляется пользователю"
            ),
            developer.create_test_case(
                "Тест экспорта данных",
                "/tests/reports/test_export_data.py",
                "Данные успешно экспортируются в CSV формат"
            )
        ]
        
        test_cases[0].add_tag("авторизация")
        test_cases[0].add_tag("безопасность")
        test_cases[0].timeout = 15
        
        test_cases[1].add_tag("заказы")
        test_cases[1].add_tag("бизнес-логика")
        test_cases[1].add_dependency(test_cases[0].test_id)
        
        test_cases[2].add_tag("оплаты")
        test_cases[2].add_tag("интеграция")
        test_cases[2].add_dependency(test_cases[1].test_id)
        
        regression_suite = TestSuite("Регрессионные тесты", developer.user_id)
        regression_suite.description = "Основные регрессионные тесты приложения"
        regression_suite.category = "regression"
        
        for test_case in test_cases[:3]:
            regression_suite.add_test(test_case)
        
        smoke_suite = TestSuite("Smoke тесты", developer.user_id)
        smoke_suite.description = "Быстрые smoke тесты для проверки основных функций"
        smoke_suite.category = "smoke"
        
        for test_case in test_cases[:2]:
            smoke_suite.add_test(test_case)
        
        self.test_suites = [regression_suite, smoke_suite]
        
        print("Созданы тест-кейсы:")
        for i, test_case in enumerate(test_cases, 1):
            print(f"  {i}. {test_case.name}")
            print(f"     ID: {test_case.test_id}")
            print(f"     Теги: {', '.join(test_case.tags) if test_case.tags else 'нет'}")
        
        print("\nСозданы тест-сьюты:")
        for suite in self.test_suites:
            print(f"  - {suite.name}")
            print(f"    Тестов: {len(suite.tests)}")
            print(f"    Категория: {suite.category}")
    
    def demo_run_test_session(self):
        print("\n4. ЗАПУСК ТЕСТОВОЙ СЕССИИ")
        print("-" * 40)
        
        developer = self.users[0]
        test_suite = self.test_suites[0]
        environment = self.environments[1]
        
        print(f"Запуск тестовой сессии:")
        print(f"  Разработчик: {developer.name}")
        print(f"  Тест-сьют: {test_suite.name}")
        print(f"  Среда: {environment.env_id} ({environment.type.value})")
        
        controller = TestController.get_instance()
        session = controller.start_test_session(test_suite, environment, developer.user_id)
        
        self.sessions.append(session)
        
        print(f"\nРезультаты сессии {session.session_id}:")
        stats = session.get_statistics()
        print(f"  Всего тестов: {stats['total']}")
        print(f"  Успешных: {stats['success']}")
        print(f"  Неудачных: {stats['failure']}")
        print(f"  Ошибок: {stats['error']}")
        print(f"  Длительность: {session.metadata.get('duration', 0):.2f} сек")
        
        if session.report:
            print(f"  Отчет сгенерирован: {session.report.report_id}")
    
    def demo_report_generation(self):
        print("\n5. ГЕНЕРАЦИЯ И ПРОСМОТР ОТЧЕТОВ")
        print("-" * 40)
        
        if not self.sessions:
            print("Нет доступных сессий для генерации отчетов")
            return
        
        session = self.sessions[0]
        report_service = ReportService()
        
        print("Экспорт отчета в различных форматах:")
        
        json_report = report_service.view_report(session.session_id, "json")
        if json_report:
            print(f"  JSON: {len(json_report)} символов (первые 300 символов):")
            print(f"    {json_report[:300]}...")
        
        text_report = report_service.view_report(session.session_id, "text")
        if text_report:
            print(f"\n  Текст: {len(text_report)} символов")
            lines = text_report.split('\n')[:15]
            for line in lines:
                print(f"    {line}")
        
        html_report = report_service.view_report(session.session_id, "html")
        if html_report:
            print(f"\n  HTML: {len(html_report)} символов")
            print(f"    Содержит HTML теги: {'<html>' in html_report[:100]}")
        
        report_details = report_service.get_report_details(session.session_id)
        if report_details:
            print(f"\nДетали отчета:")
            print(f"  ID отчета: {report_details['report_info']['report_id']}")
            print(f"  Доступные форматы: {', '.join(report_details['available_formats'])}")
            print(f"  Статистика: {report_details['statistics']}")
    
    def demo_resource_management(self):
        print("\n6. УПРАВЛЕНИЕ РЕСУРСАМИ")
        print("-" * 40)
        
        resource_manager = ResourceManager.get_instance()
        env_manager = EnvironmentManager.get_instance()
        
        utilization = resource_manager.get_resource_utilization()
        print("Статистика использования ресурсов:")
        print(f"  Всего ресурсов: {utilization['total_resources']}")
        print(f"  Выделено: {utilization['allocated']}")
        print(f"  Доступно: {utilization['available']}")
        print(f"  Загрузка: {utilization['utilization_percent']:.1f}%")
        
        print("\nЗапрос нового ресурса:")
        new_resource = resource_manager.request_resource(
            ResourceType.VM,
            capacity={'cpu': 4, 'memory_mb': 8192, 'storage_mb': 51200}
        )
        
        if new_resource:
            print(f"  Выделен ресурс: {new_resource}")
            print(f"  Характеристики: {new_resource.capacity}")
            
            resource_manager.release_resource(new_resource)
            print(f"  Ресурс освобожден")
        
        available_envs = env_manager.get_available_environments()
        print(f"\nДоступные тестовые среды: {len(available_envs)}")
        
        for env in available_envs[:2]:
            print(f"  - {env.env_id}: {env.type.value} ({len(env.resources)} ресурсов)")
    
    def demo_system_statistics(self):
        print("\n7. СТАТИСТИКА СИСТЕМЫ")
        print("-" * 40)
        
        controller = TestController.get_instance()
        env_manager = EnvironmentManager.get_instance()
        resource_manager = ResourceManager.get_instance()
        report_service = ReportService()
        
        controller_stats = controller.get_statistics()
        print("Статистика TestController:")
        print(f"  Всего сессий: {controller_stats['total_sessions']}")
        print(f"  Успешных: {controller_stats['successful_sessions']}")
        print(f"  Неудачных: {controller_stats['failed_sessions']}")
        print(f"  Отмененных: {controller_stats['cancelled_sessions']}")
        print(f"  Активных сессий: {controller_stats['active_sessions']}")
        print(f"  Общая успешность: {controller_stats['overall_success_rate']:.1f}%")
        
        all_envs = env_manager.get_all_environments()
        print(f"\nСтатистика EnvironmentManager:")
        print(f"  Всего сред: {len(all_envs)}")
        print(f"  Доступных сред: {len(env_manager.get_available_environments())}")
        
        report_stats = report_service.get_report_statistics()
        print(f"\nСтатистика ReportService:")
        print(f"  Всего отчетов: {report_stats['total_reports']}")
        print(f"  Средняя успешность: {report_stats['success_rate_avg']:.1f}%")
        print(f"  Средняя длительность: {report_stats['avg_duration']:.2f} сек")
        
        print(f"\nСтатистика пользователей:")
        print(f"  Всего пользователей: {len(self.users)}")
        
        dev = self.users[0]
        if isinstance(dev, Developer):
            print(f"  Разработчик {dev.name}:")
            print(f"    Создано тест-кейсов: {dev.test_cases_created}")
            print(f"    Запущено сессий: {dev.test_sessions_run}")


def main():
    demo = TestAutomationSystemDemo()
    demo.run_demo()


if __name__ == "__main__":
    main()