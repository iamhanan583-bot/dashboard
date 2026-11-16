import os
import urllib.parse
from pathlib import Path

# Load .env if present
env_path = Path(__file__).resolve().parent / '.env'
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            k = k.strip()
            v = v.strip().strip("'\"")
            if k not in os.environ:
                os.environ[k] = v

database_url = os.environ.get("DATABASE_URL", "").strip()

if database_url:
    url = urllib.parse.urlparse(database_url)
    DB_CONFIG = {
        "dbname": url.path.lstrip('/') or "postgres",
        "user": url.username or "postgres",
        "password": url.password or "",
        "host": url.hostname or "localhost",
        "port": int(url.port or 5432),
        "sslmode": "require"
    }
else:
    DB_CONFIG = {
        "dbname": os.environ.get("DB_NAME", "postgres"),
        "user": os.environ.get("DB_USER", "postgres"),
        "password": os.environ.get("DB_PASSWORD", ""),
        "host": os.environ.get("DB_HOST", "localhost"),
        "port": int(os.environ.get("DB_PORT", 5432)),
        "sslmode": os.environ.get("DB_SSLMODE", "prefer")
    }

PORT = int(os.environ.get("PORT", 5000))
ALLOWED_ORIGIN = "*"
