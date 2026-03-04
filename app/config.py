from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ZHIPU_API_KEY: str = ""
    OUTPUT_DIR: str = "output"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
