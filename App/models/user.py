from enums import UserRole

class User:
    def __init__(self, user_id: str, name: str, role: UserRole):
        self.userId = user_id
        self.name = name
        self.role = role

    def __str__(self):
        return f"{self.name} (ID: {self.userId}, Role: {self.role.value})"


class Developer(User):
    def __init__(self, user_id: str, name: str):
        super().__init__(user_id, name, UserRole.DEVELOPER)

    def createTest(self, name: str, script_path: str, expected_result: str):
        from models.test_models import TestCase
        return TestCase(name, script_path, expected_result)

    def runTestSuite(self, test_suite, environment):
        from services.test_controller import TestController
        controller = TestController()
        return controller.startTestSession(test_suite, environment)