import re
from fastapi import FastAPI, Request, Depends, Header
from app.config import settings
from app.api.security import verify_github_signature

# These are the scripts we built previously, saved into the services folder
from app.services.google_docs import parse_requirements_doc
from app.services.github import add_issue_to_project, update_requirement_field

app = FastAPI(title="Pipeline PM Webhook")
REQ_PATTERN = re.compile(r"(REQ-[A-Z]+-\d+)")

@app.post("/webhook")
async def handle_github_webhook(
    request: Request, 
    x_github_event: str = Header(None),
    # By injecting the security function here, FastAPI runs it automatically!
    raw_payload: bytes = Depends(verify_github_signature) 
):
    data = await request.json()
    
    if x_github_event == "issues" and data.get("action") in ["opened", "labeled"]:
        issue = data.get("issue", {})
        search_text = f"{issue.get('title', '')} {issue.get('body', '')}"
        match = REQ_PATTERN.search(search_text)
        
        if match:
            req_id = match.group(1)
            
            # Delegate to your isolated service modules
            req_data_map = parse_requirements_doc(settings.DOC_ID)
            requirement_text = req_data_map.get(req_id)
            
            if requirement_text:
                project_item_id = add_issue_to_project(settings.PROJECT_ID, issue.get("node_id"))
                update_requirement_field(
                    settings.PROJECT_ID, 
                    project_item_id, 
                    settings.FIELD_ID, 
                    requirement_text
                )
                return {"status": "success", "synced_req": req_id}
                
    return {"status": "ignored", "reason": "Not a matching issue event"}