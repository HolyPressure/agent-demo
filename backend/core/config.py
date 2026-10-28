from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "My AI Project"

    # DeepSeek（Agent 主模型）
    deepseek_api_key: str | None = None
    deepseek_model: str = "deepseek-chat"
    deepseek_api_base: str = "https://api.deepseek.com/v1"


settings = Settings()
