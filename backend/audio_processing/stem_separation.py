try:
    import librosa
    import soundfile as sf
    import numpy as np
    from scipy import signal
    import logging
    from pathlib import Path
    import music21
    import pretty_midi
    import basic_pitch
    from basic_pitch.inference import predict
    
    logger = logging.getLogger(__name__)
    STEM_PROCESSING_AVAILABLE = True
except ImportError as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Stem processing dependencies not installed: {e}")
    STEM_PROCESSING_AVAILABLE = False


def extract_stems_and_convert_to_midi(audio_path, output_dir):
    """
    Extract stems from audio and convert each to MIDI and MusicXML
    This creates completely transformative, original compositions
    """
    if not STEM_PROCESSING_AVAILABLE:
        logger.error("Stem processing dependencies not available")
        return {
            "success": False,
            "error": "Audio processing dependencies not installed"
        }
        
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
                    musicxml_files.append(musicxml_path.name)
                
                logger.info(f"Created {stem_name} MIDI and MusicXML")
                
            except Exception as e:
                logger.warning(f"Failed to process {stem_name} stem: {str(e)}")
            
            finally:
                # Clean up temp file
                if temp_stem_path.exists():
                    temp_stem_path.unlink()
        
        # 4. Create transformation info file
        create_transformation_info(output_dir, midi_files, musicxml_files)
        
        return {
            "success": True,
            "main_midi": main_midi_file.name,
            "stem_midis": midi_files,
            "musicxml_files": musicxml_files,
            "stems_created": list(stems.keys())
        }
        
    except Exception as e:
        logger.error(f"Error in stem extraction and MIDI conversion: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


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
        logger.error(f"Error in frequency filtering: {str(e)}")
        return audio


def extract_harmonic_component(audio):
    """Extract harmonic component using median filtering"""
    try:
        # Use median filter to extract harmonic component
        harmonic = librosa.effects.harmonic(y=audio)
        return harmonic
    except Exception as e:
        logger.error(f"Error extracting harmonic component: {str(e)}")
        return audio


def convert_midi_to_musicxml(midi_path, output_dir, name):
    """Convert MIDI file to MusicXML using music21"""
    try:
        # Load MIDI file
        midi_path = Path(midi_path)
        if not midi_path.exists():
            logger.error(f"MIDI file not found: {midi_path}")
            return None
        
        # Convert using music21
        midi_data = music21.converter.parse(str(midi_path))
        
        # Enhance the musical score
        midi_data = enhance_musical_score(midi_data)
        
        # Save as MusicXML
        musicxml_path = output_dir / f"{name}.xml"
        midi_data.write('musicxml', fp=str(musicxml_path))
        
        logger.info(f"Converted {midi_path.name} to MusicXML")
        return musicxml_path.name
        
    except Exception as e:
        logger.error(f"Error converting MIDI to MusicXML: {str(e)}")
        return None


def enhance_musical_score(stream):
    """Enhance the musical score with proper notation"""
    try:
        # Add key signature if missing
        if not stream.getElementsByClass('KeySignature'):
            stream.insert(0, music21.key.KeySignature(0))  # C major
        
        # Add time signature if missing
        if not stream.getElementsByClass('TimeSignature'):
            stream.insert(0, music21.meter.TimeSignature('4/4'))
        
        # Add tempo marking
        if not stream.getElementsByClass('MetronomeMark'):
            stream.insert(0, music21.tempo.MetronomeMark(number=120))
        
        return stream
        
    except Exception as e:
        logger.error(f"Error enhancing musical score: {str(e)}")
        return stream


def create_transformation_info(output_dir, midi_files, musicxml_files):
    """Create a transformation info file"""
    try:
        info_path = output_dir / "transformation_info.txt"
        
        with open(info_path, 'w') as f:
            f.write("Audio Transformation Information\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Generated MIDI Files:\n")
            for midi_file in midi_files:
                f.write(f"  - {midi_file}\n")
            
            f.write(f"\nGenerated MusicXML Files:\n")
            for musicxml_file in musicxml_files:
                f.write(f"  - {musicxml_file}\n")
            
            f.write(f"\nTransformation Type: Advanced Stem Separation with MIDI Conversion\n")
            f.write(f"Processing Method: Frequency-based stem extraction + Basic Pitch AI conversion\n")
        
        logger.info(f"Created transformation info: {info_path}")
        
    except Exception as e:
        logger.error(f"Error creating transformation info: {str(e)}")
