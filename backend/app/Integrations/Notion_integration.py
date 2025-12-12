import os
from fastapi import APIRouter, HTTPException
from .db import engine
from .models import platform_accounts, projects
from sqlalchemy import select, insert
from notion_client import Client

# Load token from .env
NOTION_TOKEN = os.getenv("NOTION_API_KEY")
print("NOTION TOKEN LOADED:", NOTION_TOKEN)
print("ENV NOTION TOKEN RAW:", repr(os.getenv("NOTION_API_KEY")))
# New Notion SDK format for ntn_ tokens
notion = Client(auth=os.environ["NOTION_TOKEN"])

router = APIRouter()


# --------------------------
# Helper: Find student by token
# --------------------------
def get_student_id_from_token(access_token: str) -> int:
    stmt = select(platform_accounts.c.student_id).where(
        platform_accounts.c.access_token == access_token
    )
    with engine.connect() as conn:
        student_id = conn.execute(stmt).scalar_one_or_none()
        if student_id is None:
            raise HTTPException(
                status_code=404,
                detail="Student not found for this access token."
            )
        return student_id

#Test whether notion even works
@router.get("/notion/test")
def notion_test():
    try:
        # Just do a simple search for any page
        response = notion.search(page_size=1)
        results = response.get("results", [])
        
        if results:
            # Return the first found object's type to confirm access
            first_result = results[0]
            return {
                "status": "success",
                "first_result_type": first_result.get("object"),
                "first_result_id": first_result.get("id")
            }
        else:
            return {"status": "success", "message": "No pages found, but token recognized."}
    
    except Exception as e:
        return {"status": "error", "detail": str(e)}



# --------------------------
# 1. LIST ALL PAGES (works with teamspaces)
# --------------------------
@router.get("/notion/pages")
def list_notion_pages():
    try:
        results = notion.search(query="", filter={"value": "page", "property": "object"})

        pages = []
        for item in results["results"]:
            title_prop = item["properties"].get("title", [])
            title = ""

            if title_prop:
                text_list = title_prop[0].get("title", [])
                if text_list:
                    title = text_list[0].get("plain_text", "")

            pages.append({
                "id": item["id"],
                "title": title or "Untitled Page"
            })

        return pages

    except Exception as e:
        print("NOTION ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------
# 2. GET PAGE CONTENT (blocks)
# --------------------------
@router.get("/notion/page/{page_id}")
def get_page_content(page_id: str):
    try:
        blocks = notion.blocks.children.list(page_id)
        return blocks
    except Exception as e:
        print("NOTION ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------
# 3. IMPORT ALL PAGES INTO PROJECTS TABLE
# --------------------------
@router.get("/notion/load_pages")
def load_notion_pages(access_token: str):
    student_id = get_student_id_from_token(access_token)

    try:
        results = notion.search(query="", filter={"value": "page", "property": "object"})
        pages = results["results"]

        with engine.connect() as conn:
            for item in pages:
                # Extract page title
                title_prop = item["properties"].get("title", [])
                title = ""

                if title_prop:
                    text_list = title_prop[0].get("title", [])
                    if text_list:
                        title = text_list[0].get("plain_text", "")

                title = title or "Untitled Page"

                record = {
                    "student_id": student_id,
                    "title": title,
                    "content": f"Imported Notion Page ID: {item['id']}",
                    "skills": {"source": "Notion"},
                    "context": "Notes",
                    "type": "Documentation",
                    "source_platform": "Notion"
                }

                conn.execute(insert(projects).values(**record))

            conn.commit()

        return {"message": f"Imported {len(pages)} Notion pages."}

    except Exception as e:
        print("NOTION ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))
