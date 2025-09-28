import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''  # Force CPU

import tempfile
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from TTS.api import TTS

app = Flask(__name__)
CORS(app)  # Enable CORS for n8n

# Force CPU usage with tacotron2-DDC model
print("Initializing Coqui TTS on CPU...")
tts = TTS("tts_models/en/ljspeech/tacotron2-DDC", gpu=False)
print("TTS model loaded successfully!")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "model": "tacotron2-DDC"})

@app.route('/generate', methods=['POST'])
def generate():
    """Main endpoint - returns binary WAV file for n8n"""
    try:
        data = request.json
        text = data.get('text', 'Hello world')
        
        print(f"Generating audio for: {text[:50]}...")
        
        # Create temp file for audio
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        # Generate audio
        tts.tts_to_file(text=text, file_path=output_path)
        
        print(f"Audio generated at: {output_path}")
        
        # Return as binary file (NOT JSON)
        response = send_file(
            output_path,
            mimetype='audio/wav',
            as_attachment=True,
            download_name='tts_output.wav'
        )
        
        # Clean up temp file after sending
        @response.call_on_close
        def cleanup():
            try:
                os.unlink(output_path)
                print("Cleaned up temp file")
            except:
                pass
        
        return response
        
    except Exception as e:
        print(f"Error generating audio: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/generate_base64', methods=['POST'])
def generate_base64():
    """Alternative endpoint - returns base64 JSON (keep for backward compatibility)"""
    try:
        import base64
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
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)
