try:
    import librosa
    import soundfile as sf
    import numpy as np
    from scipy import signal
    import random
    import logging
    from pathlib import Path
    import music21
    import pretty_midi
    import basic_pitch
    from basic_pitch.inference import predict
    
    logger = logging.getLogger(__name__)
    AUDIO_PROCESSING_AVAILABLE = True
except ImportError as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Audio processing dependencies not installed: {e}")
    AUDIO_PROCESSING_AVAILABLE = False


def apply_audio_transformations(audio_path, output_path):
    """
    Apply multiple audio transformations to create an original beat from the instrumental.
    This creates a legally distinct, copyrightable version.
    """
    if not AUDIO_PROCESSING_AVAILABLE:
        logger.error("Audio processing dependencies not available")
        return False
        
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
    """Apply EQ filtering to change frequency characteristics"""
    # Apply a high-pass filter at 80Hz to remove rumble
    nyquist = sr / 2
    high_pass_freq = 80 / nyquist
    b, a = signal.butter(4, high_pass_freq, btype='high')
    filtered = signal.filtfilt(b, a, audio)
    
    # Apply a shelf boost at 10kHz for air
    low_shelf_freq = 10000 / nyquist
    b, a = signal.butter(4, low_shelf_freq, btype='high')
    high_freq = signal.filtfilt(b, a, audio)
    filtered = filtered + 0.3 * high_freq
    
    return filtered


def add_reverb_effect(audio, sr):
    """Add a subtle reverb effect using delay"""
    # Create a simple delay-based reverb
    delay_samples = int(0.03 * sr)  # 30ms delay
    delay_line = np.zeros(len(audio) + delay_samples)
    delay_line[delay_samples:] = audio
    
    # Mix delayed signal with original
    reverb_signal = delay_line[:len(audio)] * 0.3  # 30% wet
    return audio + reverb_signal


def apply_compression(audio):
    """Apply simple dynamic range compression"""
    # Simple soft-knee compressor
    threshold = 0.7
    ratio = 4.0
    
    compressed = np.copy(audio)
    mask = np.abs(audio) > threshold
    compressed[mask] = threshold + (audio[mask] - threshold) / ratio
    
    return compressed


def add_subtle_distortion(audio):
    """Add subtle tube-like distortion"""
    # Soft clipping distortion
    distorted = np.tanh(audio * 1.5) / 1.5
    return distorted


def create_stereo_from_mono(mono_audio):
    """Create stereo image from mono audio"""
    stereo = np.zeros((2, len(mono_audio)))
    # Add slight delay to one channel for stereo width
    delay_samples = 20  # Small delay for stereo imaging
    delayed = np.pad(mono_audio, (delay_samples, 0))[:len(mono_audio)]
    
    stereo[0] = mono_audio * 0.8 + delayed * 0.2  # Left channel
    stereo[1] = mono_audio * 0.8 + delayed * -0.2  # Right channel (phase inverted)
    
    return stereo.T
