import os
from pydub import AudioSegment
from pydub.playback import play

Audio = "./Recordings/"

def Get(name):
    return AudioSegment.from_wav(os.path.join(Audio, f"{name}.wav"))

def Narrate(i):
    if not (0 <= i <= 9999):
        return
    
    if i == 0:
        play(Get("0"))
        return

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

    Sound = AudioSegment.silent(duration=2000)
    for i in Divisions:
        Sound += Get(i)
    Sound.export("final_output.wav", format="wav")
    return "final_output.wav"