#!/usr/bin/env python3
"""Cross-platform backend bootstrap (Windows / Linux / macOS). Safe to re-run."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IS_WIN = sys.platform.startswith("win")

SERVICES = {
    "auth-service": 8001,
    "chat-service": 8002,
    "decision-service": 8003,
    "history-service": 8004,
}

EXTRA_ENV = {
    "decision-service": (
        "OLLAMA_URL=http://127.0.0.1:11434\n"
        "OLLAMA_MODEL=\n"
        "OLLAMA_TIMEOUT_SECONDS=30\n"
    ),
}

REQUIREMENTS = """fastapi
uvicorn[standard]
pydantic-settings
httpx
sqlalchemy[asyncio]
asyncpg
alembic
pytest
pytest-asyncio
"""

CONFIG_PY = '''from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    service_name: str = "service"
    host: str = "127.0.0.1"
    port: int = 8000
    database_url: str = ""


settings = Settings()
'''

MAIN_PY = '''from fastapi import FastAPI

from app.config import settings

app = FastAPI(title=settings.service_name)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": settings.service_name}
'''


def write(path: Path, text: str) -> None:
    """Create the file only if it does not already exist."""
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def run(cmd: list) -> None:
    print("+", " ".join(map(str, cmd)))
    subprocess.run(cmd, check=True)


def main() -> None:
    write(ROOT / "shared/api-contracts/.gitkeep", "")
    write(ROOT / "docs/architecture.md", "# Architecture\n")
    write(ROOT / "docs/api-specification.md", "# API specification\n")

    for name, port in SERVICES.items():
        d = ROOT / "services" / name
        write(d / "app/__init__.py", "")
        write(d / "tests/__init__.py", "")
        write(d / "app/config.py", CONFIG_PY)
        write(d / "app/main.py", MAIN_PY)
        write(d / "requirements.txt", REQUIREMENTS)

        env = (
            f"SERVICE_NAME={name}\nHOST=127.0.0.1\nPORT={port}\n"
            "DATABASE_URL=postgresql+asyncpg://gateway_app:CHANGE_ME@127.0.0.1:5432/gateway\n"
            + EXTRA_ENV.get(name, "")
        )
        write(d / ".env.example", env)
        write(d / ".env", env)  # git-ignored local copy

        venv = d / ".venv"
        if not venv.exists():
            run([sys.executable, "-m", "venv", str(venv)])
        py = venv / ("Scripts/python.exe" if IS_WIN else "bin/python")
        run([str(py), "-m", "pip", "install", "--upgrade", "pip"])
        run([str(py), "-m", "pip", "install", "-r", str(d / "requirements.txt")])
        freeze = subprocess.run(
            [str(py), "-m", "pip", "freeze"], check=True, capture_output=True, text=True
        ).stdout
        (d / "requirements.lock.txt").write_text(freeze, encoding="utf-8", newline="\n")

    print("\nBootstrap complete. Now edit the DATABASE_URL password in each services/*/.env")


if __name__ == "__main__":
    main()