import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import Developer, TestCase, TestSuite, Environment
from enums import EnvironmentType
from services.test_controller import TestController
from services.environment_manager import EnvironmentManager
from services.resource_manager import ResourceManager


def main():
    print("[ДЕМОНСТРАЦИЯ СИСТЕМЫ АВТОМАТИЧЕСКОГО ТЕСТИРОВАНИЯ]")

    print("\n1. СОЗДАНИЕ РАЗРАБОТЧИКА")
    dev = Developer("dev-001", "Алексей Петров")
    print(f"Создан: {dev}")

    print("\n2. СОЗДАНИЕ ТЕСТ-КЕЙСОВ")
    test1 = dev.createTest("Тест авторизации", "/tests/auth.py", "Успешная авторизация")
    test2 = dev.createTest("Тест создания заказа", "/tests/order.py", "Заказ создан")
    print(f"Создан: {test1}")
    print(f"Создан: {test2}")

    print("\n3. СОЗДАНИЕ ТЕСТ-СЬЮТА")
    suite = TestSuite("Регрессионные тесты")
    suite.addTest(test1)
    suite.addTest(test2)
    print(f"Создан: {suite}")

    print("\n4. НАСТРОЙКА СРЕДЫ")
    env_manager = EnvironmentManager()
    config = {"db_host": "localhost", "db_port": "5432"}
    environment = env_manager.setupEnvironment(config)
    print(f"Создана среда: {environment}")

    print("\n5. УПРАВЛЕНИЕ РЕСУРСАМИ")
    resource_manager = ResourceManager()
    resource = resource_manager.requestResource("VM")
    print(f"Выделен ресурс: {resource}")
    resource_manager.releaseResource(resource)
    print(f"Ресурс освобожден")

    print("\n6. ЗАПУСК ТЕСТОВОЙ СЕССИИ")
    controller = TestController()
    session = controller.startTestSession(suite, environment)
    print(f"Создана сессия: {session}")

    print("\n7. ГЕНЕРАЦИЯ ОТЧЕТА")
    if session.report:
        print(f"Создан отчет: {session.report}")
        print(f"Содержимое отчета (первые 500 символов):")
        print(session.report.content[:500] + "...")

    print("\n8. ОСТАНОВКА СЕССИИ")
    controller.stopTestSession(session)
    print(f"Сессия остановлена: {session}")

    print("\n9. УДАЛЕНИЕ СРЕДЫ")
    env_manager.teardownEnvironment(environment)

    print("[ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА]")



if __name__ == "__main__":
    main()