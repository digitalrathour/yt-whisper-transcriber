from flask import Flask, request, jsonify
import whisper
import yt_dlp
import os
import uuid

app = Flask(__name__)
model = whisper.load_model("base")

@app.route('/')
def home():
    return 'Whisper Transcription API is running!'

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.json
    video_url = data.get('url')
    if not video_url:
        return jsonify({"error": "Missing YouTube URL"}), 400

    filename = f"audio_{uuid.uuid4()}.mp3"
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': filename,
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        result = model.transcribe(filename)
        os.remove(filename)
        return jsonify({"transcript": result["text"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
