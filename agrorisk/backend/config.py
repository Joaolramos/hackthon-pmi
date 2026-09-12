"""
Configurações centrais da aplicação via pydantic-settings.
Lê do arquivo .env automaticamente.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # IBM watsonx
    watsonx_api_key: str = ""
    watsonx_project_id: str = ""
    watsonx_url: str = "https://us-south.ml.cloud.ibm.com"

    # Banco de dados
    database_url: str = "postgresql+asyncpg://agrorisk:agrorisk@localhost:5432/agrorisk"
    redis_url: str = "redis://localhost:6379/0"

    # APIs públicas
    receitaws_base_url: str = "https://receitaws.com.br/v1"
    cnpja_base_url: str = "https://api.cnpja.com"
    datajud_base_url: str = "https://api-publica.datajud.cnj.jus.br"
    pgfn_base_url: str = "https://www.regularize.pgfn.gov.br"

    # App
    app_env: str = "development"
    log_level: str = "INFO"
    monitoring_enabled: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
