import uuid
from enums import EnvironmentType
from models.environment import Environment


class EnvironmentManager:
    def setupEnvironment(self, config):
        env_id = str(uuid.uuid4())[:8]
        print(f"EnvironmentManager: настройка среды {env_id}")
        env_type = EnvironmentType.DEVELOPMENT
        environment = Environment(env_id, env_type, config)
        return environment

    def teardownEnvironment(self, env):
        print(f"EnvironmentManager: удаление среды {env.envId}")