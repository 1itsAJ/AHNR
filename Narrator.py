import os
from pydub import AudioSegment
from pydub.playback import play
from pydub.effects import speedup

# Path to your recorded files
Audio = "./Recordings/"

def Get(name):
    return AudioSegment.from_wav(os.path.join(Audio, f"{name}.wav"))

def Narrate(i):
    if not (0 <= i <= 9999):
        return "Number out of range"
    
    if i == 0:
        play(Get("0"))
        return

    combined = AudioSegment.empty()
    Divisions = []

    Thousands = (i // 1000) * 1000
    Hundreds = ((i % 1000) // 100) * 100
    Remainder = i % 100
    
    if Thousands > 0:
        Divisions.append(str(Thousands))

    if Hundreds > 0:
        if Divisions: Divisions.append("and")
        Divisions.append(str(Hundreds))

    if 10 <= Remainder <= 19:
        if Divisions: Divisions.append("and")
        Divisions.append(str(Remainder))
    else:
        Ones = Remainder % 10
        Tens = (Remainder // 10) * 10
        
        if Ones > 0:
            if Divisions: Divisions.append("and")
            Divisions.append(str(Ones))
        
        if Tens > 0:
            if Divisions: Divisions.append("and")
            Divisions.append(str(Tens))

    Sound = AudioSegment.empty() + AudioSegment.silent(duration=1000)
    for i in Divisions:
        Sound += Get(i) + AudioSegment.silent(duration=10)
    play(Sound)
Narrate(7263)