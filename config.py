import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / "community_help_portal.db"


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "community-help-portal-secret")

    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = os.getenv(
            "SQLALCHEMY_DATABASE_URI",
            f"sqlite:///{DEFAULT_DB_PATH}"
        )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
