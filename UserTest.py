from tensorflow.keras.models import load_model
import cv2
from numpy import argmax 
from Narrator import Narrate


def Arabic(Text):
    Text=str(Text)
    Trans = str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩')
    return Text.translate(Trans)

def Start(BasePath,ModelPath):
    model = load_model(ModelPath)

    OriginalImage = cv2.imread(BasePath)
    CopyImage = OriginalImage.copy()

    GrayImage = cv2.cvtColor(OriginalImage, cv2.COLOR_BGR2GRAY)
    _, Thresh = cv2.threshold(GrayImage, 127, 255, cv2.THRESH_BINARY_INV)
    Contours, _ = cv2.findContours(Thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    Contours = sorted(Contours, key=lambda c: cv2.boundingRect(c)[0])
    StringDigits = []
    
    for i in Contours:
        x, y, w, h = cv2.boundingRect(i)

        Digit = GrayImage[y:y+h, x:x+w]
        Resized = cv2.resize(Digit, (20, 20))
        Reshaped = Resized.reshape(1, 20, 20, 1)
        
        Prediction = argmax(model.predict(Reshaped))
        StringDigits.append(str(Prediction))
        
        cv2.rectangle(CopyImage, (x, y), (x + w, y + h), (230, 210, 170), 2)
        cv2.putText(CopyImage, str(Prediction), (x, y - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 0, 0), 1)
        
    Output = "".join(StringDigits)
    print(f"\n Detected Numbers: {Arabic(Output)}\n")

    cv2.imshow("Predictions", CopyImage)
    cv2.waitKey(1)
    
    Output = int(Output)
    Narrate(Output)
    cv2.waitKey(0)