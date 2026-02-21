import json
import os
import re
from google.oauth2 import service_account
from googleapiclient.discovery import build

REQ_PATTERN = re.compile(r"(REQ-[A-Z]+-\d+)")
SCOPES = ['https://www.googleapis.com/auth/documents.readonly']

def get_docs_service():
    """Authenticates and returns the Google Docs API service."""
    # Check if we are in the cloud and JSON was passed as an env var
    service_account_info = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    
    if service_account_info:
        creds_dict = json.loads(service_account_info)
        creds = service_account.Credentials.from_service_account_info(
            creds_dict, scopes=SCOPES)
    else:
        # Fallback to local file for development
        creds = service_account.Credentials.from_service_account_file(
            'service_account.json', scopes=SCOPES)
            
    return build('docs', 'v1', credentials=creds)

def extract_all_text(elements: list) -> str:
    """Recursively extracts all text from Google Docs structural elements."""
    text = ''
    for value in elements:
        if 'paragraph' in value:
            for elem in value.get('paragraph').get('elements', []):
                if 'textRun' in elem:
                    text += elem.get('textRun').get('content', '')
        elif 'table' in value:
            for row in value.get('table').get('tableRows', []):
                for cell in row.get('tableCells', []):
                    text += extract_all_text(cell.get('content', []))
        elif 'tableOfContents' in value:
            text += extract_all_text(value.get('tableOfContents').get('content', []))
    return text

def parse_requirements_doc(document_id: str) -> dict:
    """Traverses the AST and maps Requirement IDs to their text."""
    service = get_docs_service()
    doc = service.documents().get(documentId=document_id).execute()
    content = doc.get('body').get('content', [])
    
    full_document_text = extract_all_text(content)
    requirements_map = {}

    for line in full_document_text.split('\n'):
        match = REQ_PATTERN.search(line)
        if match:
            req_id = match.group(1)
            # Clean up markdown formatting and whitespace
            clean_text = line.replace('*', '').strip()
            requirements_map[req_id] = clean_text
                        
    return requirements_map