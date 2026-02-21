import requests
from app.config import settings

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

def _get_headers():
    """Helper to generate headers dynamically with the latest PAT."""
    return {
        "Authorization": f"Bearer {settings.GITHUB_PAT}",
        "Content-Type": "application/json"
    }

def execute_graphql(query: str, variables: dict = None) -> dict:
    """Executes a GraphQL query/mutation and handles errors."""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
        
    response = requests.post(GITHUB_GRAPHQL_URL, json=payload, headers=_get_headers())
    
    if response.status_code != 200:
        raise Exception(f"GraphQL request failed: {response.status_code} {response.text}")
        
    result = response.json()
    if "errors" in result:
        raise Exception(f"GraphQL Errors: {result['errors']}")
        
    return result

def add_issue_to_project(project_id: str, issue_node_id: str) -> str:
    """Adds an Issue to a Project V2 board and returns the new Item ID."""
    mutation = """
    mutation($projectId: ID!, $issueId: ID!) {
      addProjectV2ItemById(input: {projectId: $projectId, contentId: $issueId}) {
        item { id }
      }
    }
    """
    variables = {"projectId": project_id, "issueId": issue_node_id}
    result = execute_graphql(mutation, variables)
    return result["data"]["addProjectV2ItemById"]["item"]["id"]

def update_requirement_field(project_id: str, item_id: str, field_id: str, text_value: str):
    """Updates a Custom Text Field on a Project Item."""
    mutation = """
    mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: String!) {
      updateProjectV2ItemFieldValue(
        input: {
          projectId: $projectId
          itemId: $itemId
          fieldId: $fieldId
          value: { text: $value }
        }
      ) {
        projectV2Item { id }
      }
    }
    """
    variables = {
        "projectId": project_id,
        "itemId": item_id,
        "fieldId": field_id,
        "value": text_value
    }
    execute_graphql(mutation, variables)