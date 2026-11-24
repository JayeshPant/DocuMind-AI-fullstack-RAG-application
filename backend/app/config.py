import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Search for .env in backend/ or root directory
backend_dir = Path(__file__).resolve().parent.parent
root_dir = backend_dir.parent

env_path = backend_dir / ".env"
if not env_path.exists():
    env_path = root_dir / ".env"

load_dotenv(dotenv_path=env_path)


class Settings:
    PROJECT_NAME: str = "DocuMind AI"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Your Intelligent PDF Question Answering Assistant"

    # API Keys & Secrets
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "").strip()
    MONGODB_URI: str = os.getenv("MONGODB_URI", "").strip()
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "documind").strip()

    # Model & RAG parameters (strictly preserving working config)
    NVIDIA_MODEL: str = "nvidia/nemotron-3.5-lightning-30b-a3b"
    TEMPERATURE: float = 0.2
    MAX_COMPLETION_TOKENS: int = 2500
    CHUNK_SIZE: int = 600
    CHUNK_OVERLAP: int = 80
    RETRIEVER_K: int = 3
    VECTOR_SIZE: int = 384

    # Storage paths
    BASE_DIR: Path = backend_dir
    UPLOAD_DIR: Path = backend_dir / "uploads"
    DOCUMENT_LOADER_DIR: Path = root_dir / "document_loader"

    # CORS
    _raw_cors = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000")
    CORS_ORIGINS: List[str] = [origin.strip() for origin in _raw_cors.split(",") if origin.strip()]

    def is_nvidia_configured(self) -> bool:
        return bool(self.NVIDIA_API_KEY and self.NVIDIA_API_KEY.startswith("nvapi-"))

    def is_mongodb_configured(self) -> bool:
        return bool(self.MONGODB_URI)


settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
