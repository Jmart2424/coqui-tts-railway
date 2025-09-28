import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''  # Force CPU

import base64
import tempfile
from flask import Flask, request, jsonify, send_file
from TTS.api import TTS

app = Flask(__name__)

# Force CPU usage - exactly as you had it
print("Initializing TTS on CPU...")
tts = TTS("tts_models/en/ljspeech/tacotron2-DDC", gpu=False)
print("TTS model loaded!")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

@app.route('/generate', methods=['POST'])
def generate():
    """FIXED ENDPOINT - Returns binary WAV file for n8n"""
    try:
        data = request.json
        text = data.get('text', 'Hello world')
        
        print(f"Generating audio for text: {text[:50]}...")
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        tts.tts_to_file(text=text, file_path=output_path)
        
        # CRITICAL FIX: Return actual WAV file, not JSON
        response = send_file(
            output_path,
            mimetype='audio/wav',
            as_attachment=True,
            download_name='output.wav'
        )
        
        @response.call_on_close
        def cleanup():
            try:
                os.unlink(output_path)
            except:
                pass
        
        return response
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/generate_base64', methods=['POST'])
def generate_base64():
    """ORIGINAL ENDPOINT - Keep this if you need base64 JSON anywhere else"""
    try:
        data = request.json
        text = data.get('text', 'Hello world')
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        tts.tts_to_file(text=text, file_path=output_path)
        
        with open(output_path, 'rb') as audio_file:
            audio_data = audio_file.read()
        
        os.unlink(output_path)
        
        # Returns JSON with base64 (your original format)
        return jsonify({
            "audio": base64.b64encode(audio_data).decode('utf-8'),
            "format": "wav"
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)
