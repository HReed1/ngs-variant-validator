import os
from dotenv import load_dotenv

load_dotenv()

# We raise a RuntimeError if critical variables are missing on startup
def get_env_or_fail(var_name: str) -> str:
    value = os.getenv(var_name)
    if not value:
        raise RuntimeError(f"CRITICAL: Environment variable {var_name} is not set.")
    return value

class Config:
    GITHUB_SECRET = get_env_or_fail("GITHUB_WEBHOOK_SECRET")
    GITHUB_PAT = get_env_or_fail("GITHUB_PAT")
    PROJECT_ID = get_env_or_fail("GITHUB_PROJECT_ID")
    FIELD_ID = get_env_or_fail("GITHUB_CUSTOM_FIELD_ID")
    DOC_ID = get_env_or_fail("GOOGLE_DOC_ID")

settings = Config()