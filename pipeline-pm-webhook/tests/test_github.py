import pytest
from unittest.mock import patch
from app.services.github import execute_graphql, add_issue_to_project

@patch("app.services.github.requests.post")
def test_execute_graphql_success(mock_post):
    """Ensure valid GraphQL responses are parsed correctly."""
    # Fake a successful 200 OK response from GitHub
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"data": {"some_field": "some_value"}}
    
    result = execute_graphql("query { viewer { login } }")
    assert result["data"]["some_field"] == "some_value"

@patch("app.services.github.requests.post")
def test_execute_graphql_api_error(mock_post):
    """Ensure we raise an Exception if GitHub returns a GraphQL error."""
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "data": None,
        "errors": [{"message": "Field 'invalidField' doesn't exist"}]
    }
    
    with pytest.raises(Exception, match="GraphQL Errors"):
        execute_graphql("query { invalidField }")

@patch("app.services.github.execute_graphql")
def test_add_issue_to_project(mock_execute):
    """Ensure the extraction of the Item ID from the nested GraphQL response works."""
    mock_execute.return_value = {
        "data": {
            "addProjectV2ItemById": {
                "item": {"id": "NEW_ITEM_123"}
            }
        }
    }
    
    item_id = add_issue_to_project("PROJ_1", "ISSUE_1")
    assert item_id == "NEW_ITEM_123"