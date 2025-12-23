import os
from pydub import AudioSegment
from pydub.playback import play

# Path to your recorded files
AUDIO_PATH = "./Recordings/"

def get_clip(name):
    """Helper to load a wav file."""
    return AudioSegment.from_wav(os.path.join(AUDIO_PATH, f"{name}.wav"))

def narrate_number(n):
    if not (0 <= n <= 9999):
        return "Number out of range"

    # Handle zero immediately
    if n == 0:
        play(get_clip("0"))
        return

    combined = AudioSegment.empty()
    segments = []

    # 1. Break down the number
    th = (n // 1000) * 1000
    hu = ((n % 1000) // 100) * 100
    remainder = n % 100
    
    # 2. Logic for Thousands
    if th > 0:
        segments.append(str(th))

    # 3. Logic for Hundreds
    if hu > 0:
        if segments: segments.append("and")
        segments.append(str(hu))

    # 4. Logic for Units and Tens (The 11-99 rule)
    if 10 <= remainder <= 19:
        # These are unique files like 11.wav, 12.wav...
        if segments: segments.append("and")
        segments.append(str(remainder))
    else:
        unit = remainder % 10
        ten = (remainder // 10) * 10
        
        # Units come BEFORE Tens in Arabic (e.g., 25 is 'five and twenty')
        if unit > 0:
            if segments: segments.append("and")
            segments.append(str(unit))
        
        if ten > 0:
            if segments: segments.append("and")
            segments.append(str(ten))

    # 5. Stitching the Audio
    final_audio = AudioSegment.empty()
    for s in segments:
        # Add a tiny 50ms silence between clips for a natural gap
        final_audio += get_clip(s) + AudioSegment.silent(duration=50)

    # 6. Play the result
    play(final_audio)

def playsound(number):
    narrate_number(number) # ألف ومئتان وأربعة وثلاثون