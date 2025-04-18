"""Configuration for API tests."""

# Import the main config module's function and create a test version
from config import load_config

# Create a test instance with test_mode=True
# This will use the sandbox environment and provide test defaults if credentials aren't set
config = load_config(test_mode=True)
