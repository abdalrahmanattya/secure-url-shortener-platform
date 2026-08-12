from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = (
        "postgresql+asyncpg://shortener:local-development-only@localhost:5432/shortener"
    )
    environment: str = "local"
    owner_tokens: str = "owner-demo:local-owner-token"
    admin_tokens: str = "admin:local-admin-token-change-me"
    local_rate_limit: int = 60
    rate_window_seconds: int = 60
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def token_map(self, value: str) -> dict[str, str]:
        result: dict[str, str] = {}
        for item in value.split(","):
            if ":" in item:
                identity, token = item.split(":", 1)
                if identity and token:
                    result[identity] = token
        return result

    def identities(self) -> tuple[dict[str, str], dict[str, str]]:
        owners = self.token_map(self.owner_tokens)
        admins = self.token_map(self.admin_tokens)
        if self.environment != "local" and not owners and not admins:
            raise RuntimeError("non-local environments require externally supplied identity tokens")
        return owners, admins


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
