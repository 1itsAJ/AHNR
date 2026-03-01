from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import FileResponse, PlainTextResponse
import uvicorn
import shutil
import os
import cv2
from numpy import argmax
from tensorflow.keras.models import load_model
from pydub import AudioSegment

# 1. Initialize the Server and Load the Model ONCE (for speed)
app = FastAPI()
model = load_model("AHNRmodel.keras")
Audio = "./Recordings/"

# 2. Your exact Audio Helpers
def Get(name):
    return AudioSegment.from_wav(os.path.join(Audio, f"{name}.wav"))

def Arabic(Text):
    Text=str(Text)
    Trans = str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩')
    return Text.translate(Trans)

# 3. Your modified Narrate Function (Saves instead of plays)
def Narrate(i):
    if not (0 <= i <= 9999):
        return None
    
    if i == 0:
        zero_sound = Get("0")
        zero_sound.export("final_output.wav", format="wav")
        return "final_output.wav"

    Divisions = []
    Thousands = (i // 1000) * 1000
    Hundreds = ((i % 1000) // 100) * 100
    Remainder = i % 100
    
    if Thousands > 0: Divisions.append(str(Thousands))
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
    for val in Divisions:
        Sound += Get(val)
        
    # NEW: Export the file instead of playing it
    Sound.export("final_output.wav", format="wav")
    return "final_output.wav"

# 4. Your modified Vision Pipeline (Returns audio instead of printing)
def Start(ImagePath):
    OriginalImage = cv2.imread(ImagePath)
    GrayImage = cv2.cvtColor(OriginalImage, cv2.COLOR_BGR2GRAY)
    _, Thresh = cv2.threshold(GrayImage, 120, 255, cv2.THRESH_BINARY_INV)
    Contours, _ = cv2.findContours(Thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    Contours = sorted(Contours, key=lambda c: cv2.boundingRect(c)[0])
    StringDigits = []
    
    for i in Contours:
        x, y, w, h = cv2.boundingRect(i)
        Digit = GrayImage[y:y+h, x:x+w]
        Resized = cv2.resize(Digit, (20, 20))
        Reshaped = Resized.reshape(1, 20, 20, 1)
        
        Prediction = argmax(model.predict(Reshaped, verbose=0))
        StringDigits.append(str(Prediction))
        
    Output = "".join(StringDigits)
    print(f"\n Server Detected: {Arabic(Output)}\n")

    # NEW: Call Narrate directly and return the file name
    OutputInt = int(Output)
    audio_file_path = Narrate(OutputInt)
    return audio_file_path

# 5. The Web Server "Listener"
@app.post("/process_image")
async def process_image(file: UploadFile = File(...)):
    # Save the incoming image from the phone
    with open("temp_image.png", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Send it through your AI pipeline
    audio_path = Start("temp_image.png")
    
    # Send the generated audio file back to the phone
    return FileResponse(audio_path, media_type="audio/wav")

# Run the server using Python
if __name__ == "__main__":
    uvicorn.run(app, host="192.168.0.134", port=8000)