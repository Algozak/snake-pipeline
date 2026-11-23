"""Environment-backed application settings."""

import os
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
PORT = int(os.getenv("PORT", "6500"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is required; copy .env.example to .env")
if not SECRET_KEY or len(SECRET_KEY) < 32:
    raise RuntimeError("SECRET_KEY is required and must contain at least 32 characters")
