import json
import hmac
import hashlib
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app
from app.config import settings

client = TestClient(app)

def create_mock_signature(payload_dict: dict) -> str:
    """Helper to generate a valid HMAC signature for our test payloads."""
    payload_bytes = json.dumps(payload_dict).encode('utf-8')
    hash_obj = hmac.new(
        settings.GITHUB_SECRET.encode('utf-8'), 
        msg=payload_bytes, 
        digestmod=hashlib.sha256
    )
    return f"sha256={hash_obj.hexdigest()}"

def test_missing_signature_rejected():
    """Ensure requests without a signature get bounced immediately."""
    response = client.post("/webhook", json={"test": "data"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Missing signature header"}

def test_invalid_signature_rejected():
    """Ensure requests with a fake signature get bounced."""
    headers = {"x-hub-signature-256": "sha256=fake_hash_value"}
    response = client.post("/webhook", json={"test": "data"}, headers=headers)
    assert response.status_code == 401

@patch("main.parse_requirements_doc")
@patch("main.add_issue_to_project")
@patch("main.update_requirement_field")
def test_valid_issue_opened_syncs_successfully(
    mock_update, mock_add, mock_parse
):
    """
    Simulate a valid GitHub webhook payload and ensure our router 
    calls the correct downstream services.
    """
    # 1. Setup our mock external API responses
    mock_parse.return_value = {"REQ-SEC-01": "Mock compliance text"}
    mock_add.return_value = "mock_project_item_id"
    
    # 2. Build the fake GitHub payload
    payload = {
        "action": "opened",
        "issue": {
            "title": "Implement auth [REQ-SEC-01]",
            "body": "Needs to be secure.",
            "node_id": "ISSUE_123"
        }
    }
    
    # 3. Hash it with our local secret so the app accepts it
    headers = {
        "x-github-event": "issues",
        "x-hub-signature-256": create_mock_signature(payload)
    }
    
    # 4. Fire the request at our local test client
    response = client.post("/webhook", content=json.dumps(payload), headers=headers)
    
    # 5. Assertions
    assert response.status_code == 200
    assert response.json() == {"status": "success", "synced_req": "REQ-SEC-01"}
    
    # Verify our business logic was executed exactly once with the right arguments
    mock_parse.assert_called_once_with(settings.DOC_ID)
    mock_add.assert_called_once_with(settings.PROJECT_ID, "ISSUE_123")
    mock_update.assert_called_once_with(
        settings.PROJECT_ID, 
        "mock_project_item_id", 
        settings.FIELD_ID, 
        "Mock compliance text"
    )