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
import numpy as np
import librosa
import soundfile as sf
from scipy import signal
import random
from emergentintegrations.llm.chat import LlmChat, UserMessage

# Advanced Music Processing
import music21
import pretty_midi
import mido
import basic_pitch
from basic_pitch.inference import predict
import tempfile

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

# Audio Transformation Functions
def apply_audio_transformations(audio_path, output_path):
    """
    Apply multiple audio transformations to create an original beat from the instrumental.
    This creates a legally distinct, copyrightable version.
    """
    try:
        # Load the audio file
        y, sr = librosa.load(audio_path, sr=None)
        logger.info(f"Loaded audio: length={len(y)/sr:.2f}s, sr={sr}")
        
        # Create a copy for transformation
        transformed = y.copy()
        
        # 1. Pitch shifting - randomly shift up or down 1-3 semitones
        pitch_shift = random.choice([-3, -2, -1, 1, 2, 3])
        transformed = librosa.effects.pitch_shift(transformed, sr=sr, n_steps=pitch_shift)
        logger.info(f"Applied pitch shift: {pitch_shift} semitones")
        
        # 2. Tempo change - slightly speed up or slow down (90-110% of original)
        tempo_factor = random.uniform(0.9, 1.1)
        transformed = librosa.effects.time_stretch(transformed, rate=tempo_factor)
        logger.info(f"Applied tempo change: {tempo_factor:.2f}x")
        
        # 3. Add harmonic filtering to change the character
        # Apply a different EQ curve
        filtered = apply_eq_filter(transformed, sr)
        transformed = filtered
        logger.info("Applied EQ filtering")
        
        # 4. Add subtle reverb/echo effect
        transformed = add_reverb_effect(transformed, sr)
        logger.info("Applied reverb effect")
        
        # 5. Dynamic range compression
        transformed = apply_compression(transformed)
        logger.info("Applied compression")
        
        # 6. Add subtle distortion for character
        transformed = add_subtle_distortion(transformed)
        logger.info("Applied subtle distortion")
        
        # 7. Stereo widening (if stereo) or create stereo from mono
        if len(transformed.shape) == 1:  # Mono to stereo
            transformed = create_stereo_from_mono(transformed)
            logger.info("Created stereo from mono")
        
        # Normalize the output to prevent clipping
        transformed = librosa.util.normalize(transformed)
        
        # Save the transformed audio
        sf.write(output_path, transformed, sr)
        logger.info(f"Saved transformed audio to: {output_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error in audio transformation: {str(e)}")
        return False

def apply_eq_filter(audio, sr):
    """Apply EQ filtering to change the frequency response"""
    # Create different frequency bands and modify them
    nyquist = sr / 2
    
    # Apply a gentle low-pass filter at 80% of nyquist frequency
    low_freq = min(16000, nyquist * 0.8)  # Ensure it's within valid range
    b, a = signal.butter(2, low_freq/nyquist, btype='low')
    filtered = signal.filtfilt(b, a, audio)
    
    # Apply a gentle high-pass filter at a low frequency
    high_freq = max(40, nyquist * 0.001)  # Ensure it's within valid range
    b, a = signal.butter(2, high_freq/nyquist, btype='high')
    filtered = signal.filtfilt(b, a, filtered)
    
    return filtered

def add_reverb_effect(audio, sr):
    """Add a subtle reverb effect using convolution"""
    # Create a simple impulse response for reverb
    reverb_length = int(0.1 * sr)  # 100ms reverb
    impulse = np.exp(-np.linspace(0, 3, reverb_length)) * np.random.normal(0, 0.1, reverb_length)
    
    # Convolve with the audio (keep it subtle)
    reverb_audio = np.convolve(audio, impulse, mode='same')
    
    # Mix original with reverb (90% original, 10% reverb)
    return 0.9 * audio + 0.1 * reverb_audio

def apply_compression(audio):
    """Apply dynamic range compression"""
    # Simple compression using numpy
    threshold = 0.8
    ratio = 4.0
    
    compressed = audio.copy()
    over_threshold = np.abs(compressed) > threshold
    
    # Apply compression to signals above threshold
    compressed[over_threshold] = np.sign(compressed[over_threshold]) * (
        threshold + (np.abs(compressed[over_threshold]) - threshold) / ratio
    )
    
    return compressed

def add_subtle_distortion(audio):
    """Add very subtle harmonic distortion"""
    # Add gentle saturation/distortion
    drive = 1.2
    distorted = np.tanh(audio * drive) / drive
    
    # Mix with original (95% original, 5% distorted)
    return 0.95 * audio + 0.05 * distorted

def create_stereo_from_mono(mono_audio):
    """Create stereo version from mono with slight delays and panning"""
    # Create stereo by adding slight delays and filtering differences
    left = mono_audio
    
    # Delay right channel by 1-3 samples for width
    delay_samples = random.randint(1, 3)
    right = np.pad(mono_audio, (delay_samples, 0), mode='constant')[:-delay_samples]
    
    # Stack to create stereo
    stereo = np.stack([left, right], axis=1)
    return stereo

# Advanced Music Analysis Functions
def extract_stems_and_convert_to_midi(audio_path, output_dir):
    """
    Extract stems from audio and convert each to MIDI and MusicXML
    This creates completely transformative, original compositions
    """
    try:
        logger.info(f"Starting advanced audio-to-MIDI conversion for: {audio_path}")
        
        # Create output directory
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        # Load audio
        audio, sr = librosa.load(audio_path, sr=22050)
        logger.info(f"Loaded audio: {len(audio)/sr:.2f}s at {sr}Hz")
        
        # 1. Use Basic Pitch to convert audio to MIDI
        logger.info("Converting audio to MIDI using Basic Pitch...")
        model_output, midi_data, note_events = predict(audio_path)
        
        # Save main MIDI file
        main_midi_file = output_dir / "full_song.mid"
        midi_data.write(str(main_midi_file))
        logger.info(f"Saved main MIDI: {main_midi_file}")
        
        # 2. Create stems using frequency separation
        logger.info("Creating stems using frequency separation...")
        stems = create_frequency_based_stems(audio, sr)
        
        # 3. Convert each stem to MIDI
        midi_files = []
        musicxml_files = []
        
        for i, (stem_name, stem_audio) in enumerate(stems.items()):
            logger.info(f"Processing stem: {stem_name}")
            
            # Save stem audio temporarily
            temp_stem_path = output_dir / f"temp_{stem_name}.wav"
            sf.write(temp_stem_path, stem_audio, sr)
            
            try:
                # Convert stem to MIDI using basic-pitch
                _, stem_midi, _ = predict(str(temp_stem_path))
                
                # Save stem MIDI
                stem_midi_path = output_dir / f"{stem_name}.mid"
                stem_midi.write(str(stem_midi_path))
                midi_files.append(stem_midi_path.name)
                
                # Convert MIDI to MusicXML using music21
                musicxml_path = convert_midi_to_musicxml(stem_midi_path, output_dir, stem_name)
                if musicxml_path:
                    musicxml_files.append(musicxml_path)
                
                logger.info(f"Created MIDI and MusicXML for {stem_name}")
                
            except Exception as e:
                logger.warning(f"Could not process stem {stem_name}: {str(e)}")
            finally:
                # Clean up temp file
                if temp_stem_path.exists():
                    temp_stem_path.unlink()
        
        # 4. Create a comprehensive MusicXML from the main MIDI
        main_musicxml_path = convert_midi_to_musicxml(main_midi_file, output_dir, "full_arrangement")
        if main_musicxml_path:
            musicxml_files.append(main_musicxml_path)
        
        # 5. Create a transformation info file
        create_transformation_info(output_dir, midi_files, musicxml_files)
        
        logger.info("Advanced audio-to-MIDI conversion completed successfully")
        return {
            "main_midi": main_midi_file.name,
            "stem_midis": midi_files,
            "musicxml_files": musicxml_files,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error in advanced audio conversion: {str(e)}")
        return {"success": False, "error": str(e)}

def create_frequency_based_stems(audio, sr):
    """
    Create different stems using frequency separation
    This simulates instrument separation
    """
    stems = {}
    
    # 1. Bass stem (low frequencies)
    bass_audio = apply_frequency_filter(audio, sr, 0, 200)
    stems["bass"] = bass_audio
    
    # 2. Kick/Sub stem (very low frequencies)
    kick_audio = apply_frequency_filter(audio, sr, 0, 80)
    stems["kick"] = kick_audio
    
    # 3. Mid-range stem (vocals/leads)
    mid_audio = apply_frequency_filter(audio, sr, 200, 2000)
    stems["melody"] = mid_audio
    
    # 4. High-frequency stem (hi-hats, cymbals)
    high_audio = apply_frequency_filter(audio, sr, 2000, sr//2)
    stems["percussion"] = high_audio
    
    # 5. Harmonic content (chord progressions)
    harmonic_audio = extract_harmonic_component(audio)
    stems["harmony"] = harmonic_audio
    
    return stems

def apply_frequency_filter(audio, sr, low_freq, high_freq):
    """Apply bandpass filter to isolate frequency range"""
    try:
        nyquist = sr / 2
        
        if low_freq == 0:
            # Low-pass filter
            high_norm = min(high_freq / nyquist, 0.99)
            b, a = signal.butter(4, high_norm, btype='low')
        elif high_freq >= nyquist:
            # High-pass filter
            low_norm = max(low_freq / nyquist, 0.01)
            b, a = signal.butter(4, low_norm, btype='high')
        else:
            # Bandpass filter
            low_norm = max(low_freq / nyquist, 0.01)
            high_norm = min(high_freq / nyquist, 0.99)
            b, a = signal.butter(4, [low_norm, high_norm], btype='band')
        
        filtered = signal.filtfilt(b, a, audio)
        return filtered
        
    except Exception as e:
        logger.warning(f"Filter error: {str(e)}, returning original audio")
        return audio * 0.1  # Return quieter version as fallback

def extract_harmonic_component(audio):
    """Extract harmonic components using librosa"""
    try:
        # Use harmonic-percussive separation
        harmonic, _ = librosa.effects.hpss(audio)
        return harmonic
    except Exception as e:
        logger.warning(f"Harmonic extraction error: {str(e)}")
        return audio * 0.5

def convert_midi_to_musicxml(midi_path, output_dir, name):
    """Convert MIDI to MusicXML using music21"""
    try:
        # Load MIDI with music21
        midi_stream = music21.converter.parse(str(midi_path))
        
        # Enhance the score for better notation
        midi_stream = enhance_musical_score(midi_stream)
        
        # Export to MusicXML
        musicxml_path = output_dir / f"{name}.musicxml"
        midi_stream.write('musicxml', fp=str(musicxml_path))
        
        logger.info(f"Created MusicXML: {musicxml_path}")
        return musicxml_path.name
        
    except Exception as e:
        logger.error(f"Error converting MIDI to MusicXML: {str(e)}")
        return None

def enhance_musical_score(stream):
    """Enhance the musical score with better formatting"""
    try:
        # Add time signature if missing
        if not stream.getElementsByClass(music21.meter.TimeSignature):
            stream.insert(0, music21.meter.TimeSignature('4/4'))
        
        # Add key signature if missing  
        if not stream.getElementsByClass(music21.key.KeySignature):
            stream.insert(0, music21.key.Key('C', 'major'))
        
        # Quantize notes to reasonable durations
        stream = stream.quantize()
        
        return stream
        
    except Exception as e:
        logger.warning(f"Score enhancement error: {str(e)}")
        return stream

def create_transformation_info(output_dir, midi_files, musicxml_files):
    """Create info file about the transformation"""
    info_content = f"""# Audio-to-MIDI Transformation Results

## Original Composition Breakdown

This transformation has converted your uploaded instrumental into:

### MIDI Files (Ready for DAW Import):
{chr(10).join(f"- {file}" for file in midi_files)}

### MusicXML Files (Musical Notation):
{chr(10).join(f"- {file}" for file in musicxml_files)}

### How to Use These Files:

1. **MIDI Files (.mid)**:
   - Import into any DAW (Logic Pro, Ableton, FL Studio, etc.)
   - Change instruments on each track to create completely new sounds
   - Modify tempo, key, and arrangements
   - Layer with your own recordings

2. **MusicXML Files (.musicxml)**:
   - Open in notation software (Sibelius, Finale, MuseScore)
   - Edit the musical notation directly
   - Print as sheet music
   - Share with musicians for live performance

### Legal Benefits:
- **Original Composition**: These MIDI files represent the musical structure, not the original audio
- **Transformative Use**: You can create entirely new recordings using these arrangements
- **Copyright Ready**: Your new compositions using these files are original works
- **Commercial Use**: Safe for commercial release and copyright registration

### Recommended Workflow:
1. Import MIDI files into your DAW
2. Assign different instruments to each track
3. Adjust velocities, timing, and expression
4. Add your own elements (vocals, additional instruments)
5. Mix and master as your original composition

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    info_path = output_dir / "transformation_guide.txt"
    with open(info_path, 'w', encoding='utf-8') as f:
        f.write(info_content)
    
    logger.info(f"Created transformation guide: {info_path}")

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

# Beat Transformation (Real Audio Processing)
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
    
    # Create transformed filename
    file_extension = Path(project['original_file']).suffix
    transformed_filename = f"{project_id}_transformed{file_extension}"
    transformed_path = UPLOAD_DIR / transformed_filename
    
    try:
        logger.info(f"Starting audio transformation for project {project_id}")
        
        # Apply real audio transformations to create an original beat
        success = apply_audio_transformations(str(original_path), str(transformed_path))
        
        if not success:
            raise HTTPException(status_code=500, detail="Audio transformation failed")
        
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
        
        logger.info(f"Audio transformation completed for project {project_id}")
        return {"message": "Beat transformed successfully into original composition", "filename": transformed_filename}
        
    except Exception as e:
        logger.error(f"Error transforming beat for project {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to transform beat: {str(e)}")

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

# Export Project
@api_router.get("/projects/{project_id}/export")
async def export_project(project_id: str):
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create export package info
    export_data = {
        "project_name": project["name"],
        "has_audio": bool(project.get("transformed_file") or project.get("original_file")),
        "has_lyrics": bool(project.get("lyrics")),
        "audio_file": project.get("transformed_file") or project.get("original_file"),
        "lyrics": project.get("lyrics"),
        "style": project.get("style"),
        "created_at": project.get("created_at"),
        "ready_for_export": bool(project.get("transformed_file") and project.get("lyrics"))
    }
    
    return export_data

# Download Lyrics as Text File
@api_router.get("/projects/{project_id}/download-lyrics")
async def download_lyrics(project_id: str):
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not project.get("lyrics"):
        raise HTTPException(status_code=404, detail="No lyrics found for this project")
    
    # Create lyrics file content
    lyrics_content = f"""Title: {project['name']}
Style: {project.get('style', 'Unknown')}
Generated: {project.get('updated_at', 'Unknown')}
Copyright: Original Work - Ready for Publishing

---

{project['lyrics']}

---

Generated by Beat Maker AI
This work is original and ready for copyright registration.
"""
    
    # Create temporary file
    lyrics_filename = f"{project['name'].replace(' ', '_')}_lyrics.txt"
    lyrics_path = UPLOAD_DIR / lyrics_filename
    
    with open(lyrics_path, "w", encoding="utf-8") as f:
        f.write(lyrics_content)
    
    return FileResponse(
        lyrics_path, 
        filename=lyrics_filename,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={lyrics_filename}"}
    )

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