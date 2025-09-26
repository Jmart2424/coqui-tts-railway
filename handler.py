import os
import base64
import json
from flask import Flask, request, jsonify
from TTS.api import TTS
import torch
import tempfile

app = Flask(__name__)

# Initialize TTS
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Initializing TTS on {device}...")

# Use a model that works out of the box
tts = TTS("tts_models/en/ljspeech/tacotron2-DDC").to(device)
print("TTS model loaded!")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        text = data.get('text', 'Hello world')
        
        # Generate audio
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            output_path = tmp_file.name
            
        tts.tts_to_file(text=text, file_path=output_path)
        
        # Read and encode
        with open(output_path, 'rb') as audio_file:
            audio_data = audio_file.read()
        
        # Clean up
        os.unlink(output_path)
        
        # Return base64 audio
        return jsonify({
            "audio": base64.b64encode(audio_data).decode('utf-8'),
            "format": "wav"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
