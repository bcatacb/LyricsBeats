#!/usr/bin/env python3
"""
Test script to verify the reorganized backend structure
"""
import sys
import os
sys.path.append('.')

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing Backend Structure...")
    
    try:
        from models import Project, UserStyle, LyricsRequest
        print("✅ Models module: OK")
    except Exception as e:
        print(f"❌ Models module: {e}")
        return False
    
    try:
        from audio_processing import apply_audio_transformations
        print("✅ Audio processing module: OK")
    except Exception as e:
        print(f"❌ Audio processing module: {e}")
        return False
    
    try:
        from services import generate_lyrics
        print("✅ Services module: OK")
    except Exception as e:
        print(f"❌ Services module: {e}")
        return False
    
    try:
        # Test basic FastAPI app creation without dependencies
        from fastapi import FastAPI
        app = FastAPI()
        print("✅ FastAPI core: OK")
    except Exception as e:
        print(f"❌ FastAPI core: {e}")
        return False
    
    return True

def test_project_model():
    """Test that the Project model works"""
    try:
        from models import Project, ProjectCreate
        
        # Test creating a project
        project_data = ProjectCreate(name="Test Project")
        project = Project(name=project_data.name)
        
        print(f"✅ Project model: Created project '{project.name}' with ID {project.id}")
        return True
    except Exception as e:
        print(f"❌ Project model: {e}")
        return False

def main():
    print("=" * 50)
    print("🎵 LyricsBeats Backend Structure Test")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed")
        return False
    
    # Test models
    if not test_project_model():
        print("\n❌ Model tests failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All structural tests passed!")
    print("📝 Note: Full functionality requires installing dependencies")
    print("📦 Run: pip install -r requirements_new.txt")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
