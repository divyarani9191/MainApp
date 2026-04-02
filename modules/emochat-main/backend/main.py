# ================= CAMERA + VOICE APIs =================

from fastapi import File, UploadFile
import numpy as np
import cv2
import soundfile as sf
from fer import FER
from transformers import pipeline

# -------- CAMERA SETUP --------
detector = FER(mtcnn=False)

@app.post("/detect-emotion")
async def detect_emotion(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        np_arr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        faces = detector.detect_emotions(image)

        if not faces:
            return {"emotion": "no_face"}

        emotions = faces[0]["emotions"]
        emotion = max(emotions, key=emotions.get)

        return {"emotion": emotion}

    except Exception as e:
        return {"error": str(e)}


# -------- VOICE SETUP --------
audio_model = pipeline(
    "audio-classification",
    model="ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"
)

@app.post("/detect-voice")
async def detect_voice(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        with open("temp.wav", "wb") as f:
            f.write(contents)

        speech, sr_rate = sf.read("temp.wav")

        if len(speech.shape) > 1:
            speech = np.mean(speech, axis=1)

        result = audio_model({"array": speech, "sampling_rate": sr_rate})
        label = result[0]['label'].lower()

        return {"emotion": label}

    except Exception as e:
        return {"error": str(e)}