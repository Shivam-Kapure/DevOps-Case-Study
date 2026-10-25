import os
from pathlib import Path
from dotenv import load_dotenv

# Search for .env in current directory and parent directories (workspace root)
base_dir = Path(__file__).resolve().parent.parent.parent
env_paths = [
    Path.cwd() / ".env",
    base_dir / ".env",
    Path(__file__).resolve().parent.parent / ".env"
]
for p in env_paths:
    if p.exists():
        load_dotenv(dotenv_path=p, override=False)
        break
else:
    load_dotenv()

class Settings:
    APP_NAME: str = "Enterprise Payment & Notification Engine"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = os.getenv("APP_ENV", "development")

    # Host & Port configuration
    HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    
    # Check PORT first (standard container/cloud env), then BACKEND_PORT, default to 28081
    PORT: int = int(os.getenv("PORT", os.getenv("BACKEND_PORT", "28081")))

    # CORS Configuration
    CORS_ORIGINS_RAW: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:28080,http://127.0.0.1:28080,http://localhost:30099,*"
    )

    @property
    def cors_origins(self) -> list[str]:
        raw = self.CORS_ORIGINS_RAW.strip()
        if raw == "*":
            return ["*"]
        return [origin.strip() for origin in raw.split(",") if origin.strip()]

settings = Settings()
