from ast import stmt
import os
import requests
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import select, update, insert
from .db import engine
from .models import platform_accounts, projects, students
import base64 # this is for reading the read me files
from typing import List, Dict, Any
router = APIRouter()

# env variables
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

GITHUB_BASE_URL = "https://github.com"
API_URL = "https://api.github.com"

def get_repo_readme(access_token: str, owner: str, repo_name: str) -> str:
    """
    Fetches the content of the README.md file for a given repository.
    Returns the decoded content as a string, or a fallback message if not found.
    """
    readme_url = f"{API_URL}/repos/{owner}/{repo_name}/readme"
    
    # Request the README content using the 'raw' Accept header
    res = requests.get(
        readme_url,
        headers={"Authorization": f"Bearer {access_token}", "Accept": "application/vnd.github.v3.raw"}
    )
    
    if res.status_code == 200:
        # If the raw header is used, the response text is the file content
        return res.text
    elif res.status_code == 404:
        # README not found
        print(f"Warning: README not found for {owner}/{repo_name}. Using repository description.")
        return None
    else:
        # Handle other potential errors
        print(f"Error fetching README for {owner}/{repo_name}: Status {res.status_code}, {res.text}")
        return None

def get_student_id_from_token(access_token: str) -> int:
    #Retrieves the student_id associated with the given access token
    stmt= select(platform_accounts.c.student_id).where(
        platform_accounts.c.access_token == access_token
    )
    with engine.connect() as conn:
        student_id = conn.execute(stmt).scalar_one_or_none()
        if student_id is None:
            raise HTTPException(status_code=404, detail="Student not found for this access token. Please link your Github account first")
        return student_id

@router.get("/github/login")
def github_login():
    #Redirects users to github authentication
    return RedirectResponse(
        f"{GITHUB_BASE_URL}/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&scope=repo user"
    )


@router.get("/github/callback")
def github_callback(code: str):
    # Exchanges code into access token
    
    token_res = requests.post(
        f"{GITHUB_BASE_URL}/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": GITHUB_CLIENT_ID,
            "client_secret": GITHUB_CLIENT_SECRET,
            "code": code,
        },
    )

    token_json = token_res.json()
    if "access_token" not in token_json:
        # Improved error handling for token exchange failure
        error_detail = token_json.get("error_description", "GitHub token exchange failed.")
        raise HTTPException(status_code=400, detail=error_detail)

    access_token = token_json["access_token"]
    user_res = requests.get(f"{API_URL}/user",headers={"Authorization": f"Bearer {access_token}"})
    
    if user_res.status_code != 200:
        raise HTTPException(status_code=user_res.status_code, detail="Failed to fetch GitHub user data.")

    user_data = user_res.json()

    # Get Unique Id (must be converted to string as per the DB model)
    github_user_id = str(user_data.get("id"))
    
    if not github_user_id:
        raise HTTPException(status_code=400, detail="Could not retrieve unique GitHub User ID.")


    # Extract key data from GitHub response
    full_name_or_login = user_data.get("name")
    if full_name_or_login is None:
        full_name_or_login = user_data.get("login", "")
        
    name_parts = full_name_or_login.split()

    first_name = name_parts[0] if name_parts else user_data.get("login")
    last_name = name_parts[-1] if len(name_parts) > 1 else ""
    user_email = user_data.get("email", f"user_{github_user_id}@github.com")
    
    current_student_id = None
    
    # Save token in platform_accounts
    with engine.connect() as conn:
        
        # 1. Check if platform account exists
        stmt = select(platform_accounts.c.student_id).where(
            platform_accounts.c.platform_user_id == github_user_id
        )
        existing_student_id = conn.execute(stmt).scalar_one_or_none()
        
        if existing_student_id is None:
            # 2. New user: Insert into students
            student_insert_stmt = insert(students).values( # Use standard insert
                name=first_name,
                surname=last_name,
                university="Not Provided (GitHub)",
                email=user_email
            )
            result = conn.execute(student_insert_stmt)
            # Retrieve the new unique ID (will work on most databases)
            current_student_id = result.lastrowid

            # 3. New user: Insert into platform_accounts
            conn.execute(
                insert(platform_accounts).values( # Use standard insert
                    student_id=current_student_id,
                    platform_name="GitHub",
                    access_token=access_token,
                    platform_user_id=github_user_id 
                )
            )
        else:
            # 2. Existing user: Update student profile
            current_student_id = existing_student_id

            conn.execute(
                update(students).where(students.c.id == current_student_id).values(
                    name=first_name,
                    surname=last_name,
                    email=user_email
                )
            )
        
        # 4. Always update the access token
        conn.execute(
            update(platform_accounts).where(
                platform_accounts.c.platform_user_id == github_user_id
            ).values(access_token=access_token)
        )
        conn.commit()

    return {"message": "GitHub account linked!", "access_token": access_token}


@router.get("/github/repos")
def list_repos(access_token: str):
    """List repositories and store them in projects table"""
    
    # finds student_id dynamically from the token
    stmt = select(platform_accounts.c.student_id).where(
        platform_accounts.c.access_token == access_token
    )
    
    with engine.connect() as conn:
        current_student_id = conn.execute(stmt).scalar_one_or_none()
        
        if current_student_id is None:
            raise HTTPException(status_code=404, detail="Student not found for this access token. Please link your GitHub account first.")

        
        res = requests.get(
            f"{API_URL}/user/repos",
            headers={"Authorization": f"Bearer {access_token}"}
        )
    
        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail=f"Failed to fetch repositories: {res.text}")

        repos = res.json()
        
        
        for repo in repos:
            owner = repo["owner"]["login"]
            repo_name = repo["name"]
            
            read_me_content = get_repo_readme(access_token,owner, repo_name)
            project_content = read_me_content if read_me_content else repo["description"]

            #This makes sure the description is truncuated after it reaches 2000 characters to avoid errors
            if project_content and len(project_content) > 2000:
                project_content = project_content[:1997] + "..." 
                
            
            
            repo_values = {
                "student_id": current_student_id,
                "title": repo["name"],
                "content": project_content or "No description or README provided.", 
                "skills": {"language": repo["language"] or ""},
                "context": "Extracurricular",
                "type": "Code",
                "source_platform": "GitHub",
            }
            
            # 2. Check if project already exists for this student
            project_exists_stmt = select(projects.c.id).where(
                (projects.c.student_id == current_student_id) & (projects.c.title == repo_name)
            )
            existing_project_id = conn.execute(project_exists_stmt).scalar_one_or_none()
            
            if existing_project_id:
                # 3. Project exists: UPDATE the content and skills
                conn.execute(
                    update(projects).where(projects.c.id == existing_project_id).values(
                        content=repo_values["content"],
                        skills=repo_values["skills"]
                    )
                )
            else:
                # 4. Project does not exist: INSERT new record
                conn.execute(
                    insert(projects).values(**repo_values)
                )
        conn.commit()

    return {"message": f"{len(repos)} repositories has been saved to database"}

@router.get("/github/projects", response_model=List[Dict[str, Any]])
def get_all_projects(access_token: str) -> List[Dict[str, Any]]:
    """
    Retrieves all stored projects for the student linked to the provided access_token.
    """
    
    # 1. Get the student ID using the token
    current_student_id = get_student_id_from_token(access_token)
    
    # 2. Select all projects for that student ID
    stmt = select(projects).where(
        projects.c.student_id == current_student_id
    )
    
    projects_list = []
    
    try:
        with engine.connect() as conn:
            result = conn.execute(stmt)
            # Fetch all rows and convert them to a list of dictionaries
            # row._mapping converts the ResultRow to a dictionary for FastAPI response
            for row in result:
                projects_list.append(dict(row._mapping))
                
    except Exception as e:
        # Log the error and raise an HTTPException
        print(f"Error fetching projects for student {current_student_id}: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching projects from the database.")

    return projects_list