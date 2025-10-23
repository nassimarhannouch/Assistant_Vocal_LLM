import sounddevice as sd
import numpy as np
import whisper
import tempfile
import wave

model = whisper.load_model("tiny")  # modèle plus rapide
DURATION = 10
RATE = 16000

def record_segment():
    print("🎙️ Parlez...")
    audio = sd.rec(int(DURATION * RATE), samplerate=RATE, channels=1, dtype='int16')
    sd.wait()
    return audio

while True:
    segment = record_segment()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        wf = wave.open(tmp.name, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(RATE)
        wf.writeframes(segment.tobytes())
        wf.close()
        filename = tmp.name
    result = model.transcribe(filename, task="transcribe")
    print("Texte :", result['text'])
