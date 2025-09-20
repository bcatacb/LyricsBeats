from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import shutil
import asyncio
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create upload directory
UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Pydantic Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    original_file: Optional[str] = None
    transformed_file: Optional[str] = None
    lyrics: Optional[str] = None
    style: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProjectCreate(BaseModel):
    name: str

class UserStyle(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    sample_lyrics: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserStyleCreate(BaseModel):
    name: str
    description: str
    sample_lyrics: str

class LyricsRequest(BaseModel):
    project_id: str
    style: str
    custom_prompt: Optional[str] = None
    user_style_id: Optional[str] = None

class LyricsResponse(BaseModel):
    lyrics: str
    style: str

# Initialize LLM Chat
def get_llm_chat():
    return LlmChat(
        api_key=os.environ.get('EMERGENT_LLM_KEY'),
        session_id="beat_maker_session",
        system_message="You are a professional rap lyricist and songwriter. You create original, creative rap lyrics in various styles. You understand different rap genres like trap, boom bap, drill, conscious rap, and more. You can adapt to different flows, rhyme schemes, and themes."
    ).with_model("openai", "gpt-4o")

# Routes
@api_router.get("/")
async def root():
    return {"message": "Beat Maker API Ready"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Project Management
@api_router.post("/projects", response_model=Project)
async def create_project(project: ProjectCreate):
    project_obj = Project(**project.dict())
    project_dict = project_obj.dict()
    project_dict['created_at'] = project_dict['created_at'].isoformat()
    project_dict['updated_at'] = project_dict['updated_at'].isoformat()
    await db.projects.insert_one(project_dict)
    return project_obj

@api_router.get("/projects", response_model=List[Project])
async def get_projects():
    projects = await db.projects.find().to_list(1000)
    for project in projects:
        if isinstance(project.get('created_at'), str):
            project['created_at'] = datetime.fromisoformat(project['created_at'])
        if isinstance(project.get('updated_at'), str):
            project['updated_at'] = datetime.fromisoformat(project['updated_at'])
    return [Project(**project) for project in projects]

@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if isinstance(project.get('created_at'), str):
        project['created_at'] = datetime.fromisoformat(project['created_at'])
    if isinstance(project.get('updated_at'), str):
        project['updated_at'] = datetime.fromisoformat(project['updated_at'])
    
    return Project(**project)

# File Upload
@api_router.post("/projects/{project_id}/upload")
async def upload_file(project_id: str, file: UploadFile = File(...)):
    # Check if project exists
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Validate file type
    allowed_types = ['audio/mpeg', 'audio/wav', 'audio/mp3', 'audio/x-wav']
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload audio files only.")
    
    # Save file
    file_extension = Path(file.filename).suffix
    filename = f"{project_id}_original{file_extension}"
    file_path = UPLOAD_DIR / filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update project
    await db.projects.update_one(
        {"id": project_id},
        {
            "$set": {
                "original_file": filename,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    return {"message": "File uploaded successfully", "filename": filename}

# Beat Transformation (Simulated for MVP)
@api_router.post("/projects/{project_id}/transform")
async def transform_beat(project_id: str):
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not project.get('original_file'):
        raise HTTPException(status_code=400, detail="No original file found. Please upload a file first.")
    
    # Simulate processing time
    await asyncio.sleep(2)
    
    # For MVP, just copy the original file with a new name (simulating transformation)
    original_path = UPLOAD_DIR / project['original_file']
    if not original_path.exists():
        raise HTTPException(status_code=404, detail="Original file not found")
    
    file_extension = Path(project['original_file']).suffix
    transformed_filename = f"{project_id}_transformed{file_extension}"
    transformed_path = UPLOAD_DIR / transformed_filename
    
    shutil.copy2(original_path, transformed_path)
    
    # Update project
    await db.projects.update_one(
        {"id": project_id},
        {
            "$set": {
                "transformed_file": transformed_filename,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    return {"message": "Beat transformed successfully", "filename": transformed_filename}

# Lyrics Generation
@api_router.post("/projects/{project_id}/generate-lyrics", response_model=LyricsResponse)
async def generate_lyrics(project_id: str, request: LyricsRequest):
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get user style if specified
    style_context = ""
    if request.user_style_id:
        user_style = await db.user_styles.find_one({"id": request.user_style_id})
        if user_style:
            style_context = f"\n\nUser's Style Reference:\nName: {user_style['name']}\nDescription: {user_style['description']}\nSample: {user_style['sample_lyrics']}\n\nCreate lyrics that match this user's style and flow."
    
    # Create prompt based on style
    style_prompts = {
        "trap": "Create trap-style rap lyrics with modern slang, references to success, money, and lifestyle. Use a confident, boastful tone with catchy hooks.",
        "boom_bap": "Write old-school boom bap rap lyrics with clever wordplay, storytelling, and conscious themes. Focus on lyrical complexity and meaningful content.",
        "drill": "Generate drill rap lyrics with dark, aggressive themes and street narratives. Use hard-hitting, direct language and repetitive hooks.",
        "conscious": "Create conscious rap lyrics that address social issues, personal growth, and meaningful topics. Use thoughtful, reflective language.",
        "melodic": "Write melodic rap lyrics that flow smoothly with singing elements. Focus on catchy melodies and emotional themes.",
        "freestyle": "Generate freestyle rap lyrics with creative wordplay, metaphors, and spontaneous flow. Mix different themes and showcase lyrical skill.",
    }
    
    base_prompt = style_prompts.get(request.style, "Create original rap lyrics with creative wordplay and engaging flow.")
    
    if request.custom_prompt:
        base_prompt += f"\n\nAdditional Requirements: {request.custom_prompt}"
    
    base_prompt += style_context
    base_prompt += "\n\nGenerate 16-32 bars of original rap lyrics. Include natural pauses and flow markers. Make it ready for recording."
    
    try:
        chat = get_llm_chat()
        user_message = UserMessage(text=base_prompt)
        response = await chat.send_message(user_message)
        
        generated_lyrics = response.strip()
        
        # Update project with generated lyrics
        await db.projects.update_one(
            {"id": project_id},
            {
                "$set": {
                    "lyrics": generated_lyrics,
                    "style": request.style,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        return LyricsResponse(lyrics=generated_lyrics, style=request.style)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate lyrics: {str(e)}")

# User Style Management
@api_router.post("/user-styles", response_model=UserStyle)
async def create_user_style(style: UserStyleCreate):
    style_obj = UserStyle(**style.dict())
    style_dict = style_obj.dict()
    style_dict['created_at'] = style_dict['created_at'].isoformat()
    await db.user_styles.insert_one(style_dict)
    return style_obj

@api_router.get("/user-styles", response_model=List[UserStyle])
async def get_user_styles():
    styles = await db.user_styles.find().to_list(1000)
    for style in styles:
        if isinstance(style.get('created_at'), str):
            style['created_at'] = datetime.fromisoformat(style['created_at'])
    return [UserStyle(**style) for style in styles]

@api_router.delete("/user-styles/{style_id}")
async def delete_user_style(style_id: str):
    result = await db.user_styles.delete_one({"id": style_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User style not found")
    return {"message": "User style deleted successfully"}

# File Download
@api_router.get("/files/{filename}")
async def download_file(filename: str):
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()