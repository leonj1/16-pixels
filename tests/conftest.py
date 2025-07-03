import pytest
import os
from pathlib import Path
import tempfile


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    # Set test API keys (these should be replaced with real keys for integration tests)
    test_vars = {
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY', 'test_google_key'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', 'test_openai_key'),
        'FREEPIK_API_KEY': os.getenv('FREEPIK_API_KEY', 'test_freepik_key'),
    }
    
    for key, value in test_vars.items():
        if value and value != f'test_{key.lower()}':
            monkeypatch.setenv(key, value)
    
    return test_vars


@pytest.fixture
def sample_prompts():
    """Sample prompts for testing."""
    return {
        'valid_image_prompts': [
            "create a cute pixel art cat",
            "generate an 8-bit style warrior character",
            "draw a retro spaceship sprite",
            "design a pixelated forest scene",
            "make a 16x16 icon of a magic potion"
        ],
        'invalid_prompts': [
            "what is the capital of France?",
            "calculate 2 + 2",
            "explain quantum physics",
            "write a Python function",
            "how does photosynthesis work?"
        ]
    }