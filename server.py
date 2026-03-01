import os
import cv2
import uvicorn
from numpy import argmax
from tensorflow.keras.models import load_model
from pydub import AudioSegment
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse

# 1. Initialize Server and Load Model
app = FastAPI()
model = load_model("AHNRmodel.keras")
Audio = "./Recordings/"

# 2. Audio and Text Helpers
def Get(name):
    return AudioSegment.from_wav(os.path.join(Audio, f"{name}.wav"))

def Arabic(Text):
    Text = str(Text)
    Trans = str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩')
    return Text.translate(Trans)

# 3. The Narration Engine (Saves audio to file)
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
    for val in Divisions:
        Sound += Get(val)
        
    # Export the final file instead of playing it
    Sound.export("final_output.wav", format="wav")
    return "final_output.wav"

# 4. The Vision Pipeline
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
        
        # verbose=0 stops Keras from printing progress bars in the terminal
        Prediction = argmax(model.predict(Reshaped, verbose=0))
        StringDigits.append(str(Prediction))
        
    OutputStr = "".join(StringDigits)
    print(f"\n >>> Server Detected: {Arabic(OutputStr)} <<<\n")

    # Handle empty strings just in case the image was blank
    if not OutputStr:
        OutputStr = "0"

    OutputInt = int(OutputStr)
    audio_file_path = Narrate(OutputInt)
    
    return audio_file_path

# 5. The API Endpoint for MIT App Inventor
@app.post("/process_image")
async def process_image(request: Request):
    # Read the raw image bytes sent by the phone
    body = await request.body()
    
    # Save the bytes as an image file
    with open("temp_image.png", "wb") as buffer:
        buffer.write(body)
    
    # Run the vision pipeline and generate the audio
    audio_path = Start("temp_image.png")
    
    # Send the audio file back to the phone
    return FileResponse(audio_path, media_type="audio/wav")

# 6. Start the Server
if __name__ == "__main__":
    uvicorn.run(app, host="192.168.0.134", port=8000)