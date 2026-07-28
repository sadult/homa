from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # 9Router / LLM
    NINEROUTER_API_KEY: str = ""
    NINEROUTER_BASE_URL: str = "https://api.9router.ai/v1"
    MODEL: str = "gpt-4o"
    VISION_MODEL: str = "gpt-4o"
    LLM_TIMEOUT: float = 90.0

    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    ALLOWED_TELEGRAM_IDS: str = ""

    # Web
    WEB_HOST: str = "127.0.0.1"
    WEB_PORT: int = 8000
    WEB_AUTH_TOKEN: str = "change-me"

    # Browser
    HEADLESS: bool = True
    CHROME_CDP_URL: str = ""

    # Security
    ENABLE_SYSTEM_TOOLS: bool = True
    ENABLE_SHELL: bool = False
    ENABLE_FILE_WRITE: bool = False
    REQUIRE_CONFIRMATION: bool = True
    MAX_STEPS: int = 30

    # Memory / scheduler
    DB_PATH: str = "homa.db"

    # Mail
    IMAP_HOST: str = ""
    IMAP_USER: str = ""
    IMAP_PASSWORD: str = ""
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587


settings = Settings()


def allowed_telegram_ids() -> set[int]:
    return {int(x) for x in settings.ALLOWED_TELEGRAM_IDS.split(",") if x.strip()}
