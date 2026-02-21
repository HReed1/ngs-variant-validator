from unittest.mock import MagicMock, patch
from app.services.google_docs import extract_all_text, parse_requirements_doc

def test_extract_all_text_from_ast():
    """Ensure our recursive function successfully navigates the Google AST."""
    mock_ast = [
        {"paragraph": {"elements": [{"textRun": {"content": "REQ-SYS-01: First req\n"}}]}},
        {"table": {"tableRows": [{"tableCells": [{"content": [{"paragraph": {"elements": [{"textRun": {"content": "REQ-SYS-02: Table req"}}]}}]}]}]}}
    ]
    
    result = extract_all_text(mock_ast)
    assert "REQ-SYS-01: First req" in result
    assert "REQ-SYS-02: Table req" in result

@patch("app.services.google_docs.get_docs_service")
def test_parse_requirements_doc(mock_get_service):
    """Ensure we correctly map REQ-IDs to their full text strings."""
    # Build a fake Google Docs API response chain
    mock_service = MagicMock()
    mock_execute = MagicMock()
    
    mock_execute.execute.return_value = {
        "body": {
            "content": [
                {"paragraph": {"elements": [{"textRun": {"content": "* REQ-SEC-01 (PHI): Must be secure.\n"}}]}},
                {"paragraph": {"elements": [{"textRun": {"content": "Random text without a requirement ID."}}]}}
            ]
        }
    }
    mock_service.documents().get.return_value = mock_execute
    mock_get_service.return_value = mock_service
    
    # Run the function
    result = parse_requirements_doc("fake_doc_id")
    
    # Assertions
    assert "REQ-SEC-01" in result
    assert result["REQ-SEC-01"] == "REQ-SEC-01 (PHI): Must be secure."
    assert len(result) == 1