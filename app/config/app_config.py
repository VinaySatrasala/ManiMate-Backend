# config.py
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class DatabaseConfig:
    postgres_url: str

@dataclass  
class RedisConfig:
    host: str = "localhost"
    port: int = 6379
    db: int = 0


@dataclass
class AppConfig:
    database: DatabaseConfig
    redis: RedisConfig
    sync_interval: int = 300  # seconds

# Example configuration
def get_default_config() -> AppConfig:
    return AppConfig(
        database=DatabaseConfig(
            postgres_url="postgresql://memory_owner:npg_fPl60KdDCMuL@ep-patient-feather-a8fp9aqu-pooler.eastus2.azure.neon.tech/memory?sslmode=require"
        ),
        redis=RedisConfig(),
    )