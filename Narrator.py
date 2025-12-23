import os
from pydub import AudioSegment
from pydub.playback import play

# Path to your recorded files
Audio = "./Recordings/"

def Get(name):
    """Helper to load a wav file."""
    return AudioSegment.from_wav(os.path.join(Audio, f"{name}.wav"))

def Narrate(i):
    if not (0 <= i <= 9999):
        return "Number out of range"

    # Handle zero immediately
    if i == 0:
        play(Get("0"))
        return

    combined = AudioSegment.empty()
    Divisions = []

    # 1. Break down the number
    Thousands = (i // 1000) * 1000
    Hundreds = ((i % 1000) // 100) * 100
    Remainder = i % 100
    
    # 2. Logic for Thousands
    if Thousands > 0:
        Divisions.append(str(Thousands))

    # 3. Logic for Hundreds
    if Hundreds > 0:
        if Divisions: Divisions.append("and")
        Divisions.append(str(Hundreds))

    # 4. Logic for Units and Tens (The 11-99 rule)
    if 10 <= Remainder <= 19:
        # These are unique files like 11.wav, 12.wav...
        if Divisions: Divisions.append("and")
        Divisions.append(str(Remainder))
    else:
        Ones = Remainder % 10
        Tens = (Remainder // 10) * 10
        
        # Units come BEFORE Tens in Arabic (e.g., 25 is 'five and twenty')
        if Ones > 0:
            if Divisions: Divisions.append("and")
            Divisions.append(str(Ones))
        
        if Tens > 0:
            if Divisions: Divisions.append("and")
            Divisions.append(str(Tens))

    Sound = AudioSegment.empty()
    for i in Divisions:
        Sound += Get(i)
    play(Sound)