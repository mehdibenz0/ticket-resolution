from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    llm_mode: str = 'mock'
    anthropic_api_key: str | None = None
    anthropic_model: str = 'claude-sonnet-4-6'

    app_env: str = 'development'
    api_host: str = '0.0.0.0'
    api_port: int = 8000

    similarity_threshold: float = 0.34
    escalation_confidence_threshold: float = 0.72

    generated_ticket_dir: Path = Path('data/generated_tickets')
    run_log_path: Path = Path('data/run_log.jsonl')

    slack_webhook_url: str | None = None
    email_webhook_url: str | None = None


settings = Settings()
