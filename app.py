import os
import json
from flask import Flask, request, Response, jsonify
from elevenlabs.client import ElevenLabs
from elevenlabs import play

app = Flask(__name__)

ELEAPI_KEY = os.environ.get("ELEVENLABS_API_KEY")
API_KEY = os.environ.get("API_KEY")
client = ElevenLabs(api_key=ELEAPI_KEY)


@app.route("/")
def health():
    return {"status": "ok"}

@app.route("/tts", methods=["POST"])
def tts():
    data = request.json or {}
    text = data.get("text", "")
    voice_id = data.get("voice", "c4ZwDxrFaobUF5e1KlEM")
    password = data.get("pass", "")
    if not password or password != API_KEY:
        return jsonify({"error": "invalid authentication"}), 400

    if not text:
        return jsonify({"error": "text missing"}), 400

    try:
        audio_bytes = client.text_to_speech.convert(
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            text=text,
            #output_format="mp3_44100_128"
        )

        return Response(
            audio_bytes,
            mimetype="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=tts.mp3"}
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/stt", methods=["POST"])
def stt():
    password = request.form.get("pass", "")
    if not password or password != API_KEY:
        return jsonify({"error": "invalid authentication"}), 400

    if "file" not in request.files:
        return {"error": "file missing"}, 400
    audio_file = request.files["file"]

    # Muodosta puskuri datasta
    from io import BytesIO
    audio_bytes = BytesIO(audio_file.read())

    # Kutsu ElevenLabs STT (Scribe v1)
    result = client.speech_to_text.convert(
        file=audio_bytes,
        model_id="scribe_v1",
        diarize=False,
        tag_audio_events=False,
    )

    output = {
        "text": result.text
    }

    return json.dumps(output)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

