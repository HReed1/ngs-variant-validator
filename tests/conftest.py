import pytest
import os

@pytest.fixture
def temp_workspace(tmp_path):
    """
    Creates a temporary directory for testing file I/O operations.
    The tmp_path fixture is built into pytest and automatically cleans up after itself.
    """
    original_dir = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(original_dir)