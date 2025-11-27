from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
import shutil
import uuid
from datetime import datetime, timezone
from typing import List

from models import (
    StatusCheck, StatusCheckCreate, Project, ProjectCreate,
    UserStyle, UserStyleCreate, LyricsRequest, LyricsResponse
)
from audio_processing import apply_audio_transformations
from audio_processing.stem_separation import extract_stems_and_convert_to_midi
from services import generate_lyrics, generate_lyrics_with_user_style

logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Upload directory
UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Create router
api_router = APIRouter(prefix="/api")


# Health check
@api_router.get("/")
async def root():
    return {"message": "LyricsBeats API is running", "version": "2.0"}


# Status endpoints
@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_check = StatusCheck(client_name=input.client_name)
    
    await db.status_checks.insert_one(status_check.model_dump())
    logger.info(f"Created status check for client: {input.client_name}")
    
    return status_check


@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(100)
    
    # Convert string timestamps back to datetime if needed
    for check in status_checks:
        if isinstance(check.get('timestamp'), str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return [StatusCheck(**check) for check in status_checks]


# Project endpoints
@api_router.post("/projects", response_model=Project)
async def create_project(project: ProjectCreate):
    new_project = Project(name=project.name)
    
    await db.projects.insert_one(new_project.model_dump())
    logger.info(f"Created project: {new_project.name}")
    
    return new_project


@api_router.get("/projects", response_model=List[Project])
async def get_projects():
    projects = await db.projects.find().to_list(100)
    
    # Convert string timestamps back to datetime if needed
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


# Beat Transformation (Advanced Audio-to-MIDI Conversion)
@api_router.post("/projects/{project_id}/transform")
async def transform_beat(project_id: str):
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not project.get('original_file'):
        raise HTTPException(status_code=400, detail="No original file found. Please upload a file first.")
    
    original_path = UPLOAD_DIR / project['original_file']
    if not original_path.exists():
        raise HTTPException(status_code=404, detail="Original file not found")
    
    try:
        logger.info(f"Starting advanced audio-to-MIDI transformation for project {project_id}")
        
        # Create transformation output directory
        transform_dir = UPLOAD_DIR / f"{project_id}_stems"
        transform_dir.mkdir(exist_ok=True)
        
        # Apply advanced audio-to-MIDI conversion
        logger.info("Calling extract_stems_and_convert_to_midi...")
        transformation_result = extract_stems_and_convert_to_midi(str(original_path), str(transform_dir))
        
        if not transformation_result.get("success"):
            logger.error(f"Transformation failed: {transformation_result.get('error', 'Unknown error')}")
            raise HTTPException(status_code=500, detail=f"Audio transformation failed: {transformation_result.get('error', 'Unknown error')}")
        
        logger.info(f"Transformation successful. Files created: {transformation_result.get('stem_midis', [])}")
        
        # Update project with transformation results
        await db.projects.update_one(
            {"id": project_id},
            {
                "$set": {
                    "stems_directory": f"{project_id}_stems",
                    "midi_files": transformation_result.get("stem_midis", []),
                    "musicxml_files": transformation_result.get("musicxml_files", []),
                    "main_midi": transformation_result.get("main_midi"),
                    "transformation_type": "advanced_stems_midi",
                    "transformation_complete": True,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        logger.info(f"Advanced transformation completed for project {project_id}")
        return {
            "message": "Beat successfully converted to MIDI stems and MusicXML files",
            "main_midi": transformation_result.get("main_midi"),
            "stem_midis": transformation_result.get("stem_midis", []),
            "musicxml_files": transformation_result.get("musicxml_files", []),
            "stems_created": transformation_result.get("stems_created", [])
        }
        
    except Exception as e:
        logger.error(f"Error in beat transformation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Beat transformation failed: {str(e)}")


# Download stems
@api_router.get("/projects/{project_id}/download-stems")
async def download_stems(project_id: str):
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not project.get('stems_directory'):
        raise HTTPException(status_code=400, detail="No stems available for this project")
    
    stems_dir = UPLOAD_DIR / project['stems_directory']
    if not stems_dir.exists():
        raise HTTPException(status_code=404, detail="Stems directory not found")
    
    # Create a zip file of all stems
    import zipfile
    zip_path = UPLOAD_DIR / f"{project_id}_stems.zip"
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file_path in stems_dir.glob("*"):
            if file_path.is_file():
                zipf.write(file_path, file_path.name)
    
    return FileResponse(
        path=zip_path,
        filename=f"{project['name']}_stems.zip",
        media_type="application/zip"
    )


# Lyrics Generation
@api_router.post("/projects/{project_id}/generate-lyrics", response_model=LyricsResponse)
async def generate_project_lyrics(project_id: str, request: LyricsRequest):
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        if request.user_style_id:
            # Use custom user style
            user_style = await db.user_styles.find_one({"id": request.user_style_id})
            if not user_style:
                raise HTTPException(status_code=404, detail="User style not found")
            
            lyrics = await generate_lyrics_with_user_style(user_style, request.custom_prompt)
            style_name = user_style['name']
        else:
            # Use predefined style
            lyrics_response = await generate_lyrics(request)
            lyrics = lyrics_response.lyrics
            style_name = request.style
        
        # Update project with lyrics
        await db.projects.update_one(
            {"id": project_id},
            {
                "$set": {
                    "lyrics": lyrics,
                    "style": style_name,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        logger.info(f"Generated lyrics for project {project_id} in {style_name} style")
        return LyricsResponse(lyrics=lyrics, style=style_name)
        
    except Exception as e:
        logger.error(f"Error generating lyrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate lyrics: {str(e)}")


# User Styles
@api_router.post("/user-styles", response_model=UserStyle)
async def create_user_style(user_style: UserStyleCreate):
    new_style = UserStyle(**user_style.model_dump())
    
    await db.user_styles.insert_one(new_style.model_dump())
    logger.info(f"Created user style: {new_style.name}")
    
    return new_style


@api_router.get("/user-styles", response_model=List[UserStyle])
async def get_user_styles():
    styles = await db.user_styles.find().to_list(100)
    
    for style in styles:
        if isinstance(style.get('created_at'), str):
            style['created_at'] = datetime.fromisoformat(style['created_at'])
    
    return [UserStyle(**style) for style in styles]


@api_router.delete("/user-styles/{style_id}")
async def delete_user_style(style_id: str):
    result = await db.user_styles.delete_one({"id": style_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User style not found")
    
    logger.info(f"Deleted user style: {style_id}")
    return {"message": "User style deleted successfully"}


# File serving
@api_router.get("/files/{filename}")
async def serve_file(filename: str):
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(path=file_path)


# Export project
@api_router.get("/projects/{project_id}/export")
async def export_project(project_id: str):
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create export data
    export_data = {
        "project": project,
        "exported_at": datetime.now(timezone.utc).isoformat()
    }
    
    return export_data


# Download lyrics
@api_router.get("/projects/{project_id}/download-lyrics")
async def download_lyrics(project_id: str):
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not project.get('lyrics'):
        raise HTTPException(status_code=400, detail="No lyrics available for this project")
    
    # Create a text file with lyrics
    lyrics_file = UPLOAD_DIR / f"{project_id}_lyrics.txt"
    
    with open(lyrics_file, 'w', encoding='utf-8') as f:
        f.write(f"Lyrics for {project['name']}\n")
        f.write(f"Style: {project.get('style', 'Unknown')}\n")
        f.write("=" * 40 + "\n\n")
        f.write(project['lyrics'])
    
    return FileResponse(
        path=lyrics_file,
        filename=f"{project['name']}_lyrics.txt",
        media_type="text/plain"
    )
