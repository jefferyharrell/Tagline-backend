import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Ensure project root is in path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Removed REDIS_URL override
# Use Dockerized Postgres DB for E2E tests
os.environ["DB_URL"] = "postgresql+psycopg://tagline:tagline@postgres:5432/tagline_test"

# Load environment variables from .env file using pathlib
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
