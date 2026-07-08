from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # O Pydantic lerá automaticamente as variáveis de ambiente 
    # que correspondam a estes nomes (em maiúsculas por padrão)
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    mongodb_uri: str
    mongodb_db: str
    mongodb_vector_index: str

    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str

    redis_url: str

@lru_cache
def get_settings() -> Settings:
    return Settings()