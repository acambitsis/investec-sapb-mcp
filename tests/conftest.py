"""Pytest configuration file for API tests."""

import logging
import shutil
from pathlib import Path

# Configure logging
logger = logging.getLogger("investec-tests")


def pytest_sessionstart(session):
    """Set up test environment before session starts."""
    # Create .env file from .env.example if it doesn't exist
    root_dir = Path(__file__).parent.parent
    env_file = root_dir / ".env"
    env_example = root_dir / ".env.example"

    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        logger.info("Created .env file from .env.example for testing")
