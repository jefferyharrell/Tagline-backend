import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Ensure project root is in path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Override Redis URL for integration tests (local)
os.environ["REDIS_URL"] = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# Load environment variables from .env file using pathlib
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
