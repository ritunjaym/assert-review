import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    github_token: str = ""
    github_webhook_secret: str = ""
    ml_api_url: str = "http://localhost:8000"
    wandb_api_key: str = ""
    wandb_project: str = "assert-review"
    hf_token: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
