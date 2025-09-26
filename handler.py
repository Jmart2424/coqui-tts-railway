import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''  # Force CPU

import base64
import tempfile
from flask import Flask, request, jsonify
from TTS.api import TTS

app = Flask(__name__)

# Force CPU usage
print("Initializing TTS on CPU...")
tts = TTS("tts_models/en/ljspeech/tacotron2-DDC", gpu=False)
print("TTS model loaded!")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        text = data.get('text', 'Hello world')
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        tts.tts_to_file(text=text, file_path=output_path)
        
        with open(output_path, 'rb') as audio_file:
            audio_data = audio_file.read()
        
        os.unlink(output_path)
        
        return jsonify({
            "audio": base64.b64encode(audio_data).decode('utf-8'),
            "format": "wav"
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
