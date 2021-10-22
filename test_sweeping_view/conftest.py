
from pathlib import Path
import pytest

@pytest.fixture
def replay_path():
    return Path(__file__).parent / "replays"
