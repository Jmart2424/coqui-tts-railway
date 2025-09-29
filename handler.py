import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''  # Force CPU

import base64
import tempfile
from flask import Flask, request, jsonify, send_file
from TTS.api import TTS
import TTS

app = Flask(__name__)

# === EASY VOICE SWITCHING ===
# Just change this one variable to switch voices!
VOICE_MODEL = "jenny"  # Change this to switch voices

# Voice presets (add more as you find them)
VOICE_MODELS = {
    "jenny": "tts_models/en/jenny/jenny",
    "ljspeech": "tts_models/en/ljspeech/tacotron2-DDC", 
    "glow": "tts_models/en/ljspeech/glow-tts",
    "vctk": "tts_models/en/vctk/vits",
    "bark": "tts_models/multilingual/multi-dataset/bark",
    "xtts": "tts_models/multilingual/multi-dataset/xtts_v2"
}

# Load the selected model
model_path = VOICE_MODELS.get(VOICE_MODEL, VOICE_MODELS["jenny"])
print(f"Loading voice model: {VOICE_MODEL} ({model_path})")
tts = TTS(model_path, gpu=False)
print("TTS model loaded!")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "current_voice": VOICE_MODEL,
        "available_voices": list(VOICE_MODELS.keys())
    })

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        text = data.get('text', 'Hello world')
        
        print(f"Generating audio for text: {text[:50]}...")
        
        # Optional: Allow voice switching per request
        requested_voice = data.get('voice', None)
        if requested_voice and requested_voice in VOICE_MODELS:
            global tts
            tts = TTS(VOICE_MODELS[requested_voice], gpu=False)
        
        # For multi-speaker models
        speaker = data.get('speaker', None)
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        if speaker and hasattr(tts, 'speakers'):
            tts.tts_to_file(text=text, file_path=output_path, speaker=speaker)
        else:
            tts.tts_to_file(text=text, file_path=output_path)
        
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
    """Keep this endpoint for backward compatibility"""
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

# === NEW: List ALL available Coqui models ===
@app.route('/list_all_models', methods=['GET'])
def list_all_models():
    try:
        # This lists ALL models Coqui has available
        all_models = TTS.TTS().list_models()
        
        # Filter for English models that work on CPU
        english_models = [m for m in all_models if 'en/' in m]
        
        return jsonify({
            "english_models": english_models,
            "total_models": len(all_models),
            "all_models": all_models  # Full list if you want to explore
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === NEW: Test a model before committing ===
@app.route('/test_model', methods=['POST'])
def test_model():
    try:
        data = request.json
        model_name = data.get('model', 'tts_models/en/jenny/jenny')
        text = data.get('text', 'Testing new voice')
        
        # Load model temporarily
        test_tts = TTS(model_name, gpu=False)
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        test_tts.tts_to_file(text=text, file_path=output_path)
        
        response = send_file(
            output_path,
            mimetype='audio/wav',
            as_attachment=True,
            download_name='test_voice.wav'
        )
        
        @response.call_on_close
        def cleanup():
            try:
                os.unlink(output_path)
            except:
                pass
        
        return response
        
    except Exception as e:
        return jsonify({"error": str(e), "message": "Model might not be compatible with CPU"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)
