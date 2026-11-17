import os
import urllib.parse
from pathlib import Path
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
        "dbname": urllib.parse.unquote(url.path.lstrip('/')) or "postgres",
        "user": urllib.parse.unquote(url.username or "postgres"),
        "password": urllib.parse.unquote(url.password or ""),
        "host": url.hostname or "localhost",
        "port": int(url.port or 5432),
        "sslmode": "require"
    }
else:
    _host = os.environ.get("DB_HOST", "localhost")
    DB_CONFIG = {
        "dbname": os.environ.get("DB_NAME", "postgres"),
        "user": os.environ.get("DB_USER", "postgres"),
        "password": os.environ.get("DB_PASSWORD", ""),
        "host": _host,
        "port": int(os.environ.get("DB_PORT", 5432)),
        
        "sslmode": os.environ.get(
            "DB_SSLMODE",
            "prefer" if _host in ("localhost", "127.0.0.1") else "require"
        )
    }

if not DB_CONFIG["password"]:
    raise RuntimeError(
        "Database password is missing. Set DB_PASSWORD (or DATABASE_URL) in the .env file "
        "or in the hosting Secrets."
    )

PORT = int(os.environ.get("PORT", 5000))
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", f"http://localhost:{PORT}")
