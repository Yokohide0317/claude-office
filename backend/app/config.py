from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).parent.parent.resolve()
_DEFAULT_DB_PATH = _BACKEND_DIR / "visualizer.db"


class Settings(BaseSettings):
    PROJECT_NAME: str = "OpenCode Office Visualizer"
    VERSION: str = "0.8.0"
    API_V1_STR: str = "/api/v1"

    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://0.0.0.0:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    DATABASE_URL: str = f"sqlite+aiosqlite:///{_DEFAULT_DB_PATH}"
    GIT_POLL_INTERVAL: int = 5

    # Claude Code Legacy Settings (for backward compatibility)
    CLAUDE_CODE_OAUTH_TOKEN: str = ""
    CLAUDE_PATH_HOST: str = ""
    CLAUDE_PATH_CONTAINER: str = ""

    # Summary Service Settings
    SUMMARY_MODEL: str = "claude-haiku-4-5-20251001"
    SUMMARY_ENABLED: bool = True
    SUMMARY_MAX_TOKENS: int = 1000

    # OpenCode Server Settings
    OPENCODE_SERVER_URL: str = "http://localhost:4096"
    OPENCODE_SERVER_USERNAME: str = "opencode"
    OPENCODE_SERVER_PASSWORD: str = ""
    OPENCODE_ADAPTER_ENABLED: bool = True
    OPENCODE_HEALTH_CHECK_INTERVAL: int = 30
    OPENCODE_RECONNECT_DELAY: int = 5

    # Anthropic API for summaries (optional)
    ANTHROPIC_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env")

    def translate_path(self, path: str) -> str:
        """Translate host path to container path for Docker deployments.

        If CLAUDE_PATH_HOST and CLAUDE_PATH_CONTAINER are set, replaces the
        host prefix with the container prefix. Otherwise returns path unchanged.

        Args:
            path: File path to translate (e.g., transcript_path from hooks)

        Returns:
            Translated path for the current environment
        """
        if (
            self.CLAUDE_PATH_HOST
            and self.CLAUDE_PATH_CONTAINER
            and path.startswith(self.CLAUDE_PATH_HOST)
        ):
            return path.replace(self.CLAUDE_PATH_HOST, self.CLAUDE_PATH_CONTAINER, 1)
        return path


@lru_cache
def get_settings() -> Settings:
    return Settings()
