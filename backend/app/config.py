import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", ".env"))
load_dotenv()  # also load root .env if running from project root

def build_sqlalchemy_uri():
    explicit = os.getenv("DATABASE_URL")
    if explicit:
        return explicit
    user = os.getenv("DB_USER", "appuser")
    pwd = os.getenv("DB_PASSWORD", "dbuser123")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5001")
    name = os.getenv("DB_NAME", "myapp")
    return f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{name}"

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = build_sqlalchemy_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=int(os.getenv("SESSION_TOKEN_TTL_SECONDS", "86400")))
    JSON_SORT_KEYS = False
    PROPAGATE_EXCEPTIONS = True
