from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_provider: str = "mock"
    embedding_provider: str = "mock"
    vector_store: str = "memory"
    knowledge_dir: Path = Path("examples/sample_data")
    data_dir: Path = Path("data")
    database_url: str = "sqlite:///./data/runtime/piis.db"
    assessment_dir: Path = Path("data/assessment/questions")

    @property
    def processed_dir(self) -> Path:
        return self.data_dir / "processed"

    @property
    def runtime_dir(self) -> Path:
        return self.data_dir / "runtime"

    def ensure_runtime_dirs(self) -> None:
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.runtime_dir.mkdir(parents=True, exist_ok=True)
