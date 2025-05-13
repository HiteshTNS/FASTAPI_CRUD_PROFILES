# app/core/config.py
import os
import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field
load_dotenv()

class DatabaseConfig(BaseModel):
    driver: str
    host: str
    port: int
    database: str
    username: str
    password: str
    encrypt: bool
    trust_server_certificate: bool
    domain: str
    secret_key: str
    jwt_algorithm: str
    jwt_expiration_minutes: int

class AppConfig(BaseModel):
    db: DatabaseConfig

    @classmethod
    def load_from_yaml(cls):
        # Get the environment
        env = os.getenv('FASTAPI_ENV', 'dev')
        config_file = os.path.join(os.path.dirname(__file__), f"../profiles/{env}.yml")

        print(f"Loading configuration from: {config_file}")

        # Load YAML
        with open(config_file, "r") as file:
            config_data = yaml.safe_load(file)

        print(f"RAW YAML DATA LOADED:\n{config_data}")
        return cls(**config_data)  ##initializes the AppConfig Object and validated with DataBaseconfig defined above


settings = AppConfig.load_from_yaml()

