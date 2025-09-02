from flask import Flask, request, jsonify, send_file
import yt_dlp
import os
import glob
import uuid

app = Flask(__name__)

@app.route("/", methods=["GET"])
def health():
    return "OK", 200

@app.post("/download_mp4")
def download_mp4():
    data = request.get_json(force=True) or {}
    url = data.get("url")
    if not url:
        return jsonify({"error": "Missing 'url'"}), 400

    tmp = f"/tmp/{uuid.uuid4()}.mp4"
    # cookies path (optional): mount karo to env se UTHA sakta hai
    COOKIE_PATH = os.getenv("COOKIE_PATH", "/app/data/cookies.txt")

    ydl_opts = {
        "quiet": True,
        "noplaylist": True,
        "outtmpl": tmp,
        "merge_output_format": "mp4",
        "cookiefile": COOKIE_PATH if os.path.exists(COOKIE_PATH) else None,
        # 1080p tak best video+audio ko merge karke mp4
        "format": "bv*[height<=1080][ext=mp4]+ba/b[height<=1080][ext=mp4]/bv*+ba/b",
    }

    # None values hata do
    ydl_opts = {k: v for k, v in ydl_opts.items() if v is not None}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return send_file(tmp, as_attachment=True, download_name="video_1080p.mp4")
    except Exception as e:
        return jsonify({"error": str(e)}), 500
