from flask import Flask, request, jsonify, send_file
import yt_dlp
import os, glob

app = Flask(__name__)

# Azure File Share mount se cookies uthayega
COOKIE_PATH = os.getenv("COOKIE_PATH", "/app/data/cookies.txt")

@app.get("/")
def health():
    return "OK", 200

@app.post("/download_mp4")
def download_mp4():
    data = request.get_json(force=True) or {}
    url = data.get("url")
    if not url:
        return jsonify({"error": "Missing 'url'"}), 400

    # /tmp pe likho (container ephemeral storage)
    outtmpl = "/tmp/%(id)s.%(ext)s"

    # 1080p tak best video + best audio → merge → mp4
    ydl_opts = {
        "quiet": True,
        "noplaylist": True,
        "cookiefile": COOKIE_PATH,                # file optional hai, hogi to use hogi
        "format": "bv*[height<=1080]+ba/best[ext=mp4]",
        "merge_output_format": "mp4",
        "outtmpl": outtmpl,
        "nocheckcertificate": True,
        "geo_bypass": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            vid_id = info.get("id")

        files = []
        if vid_id:
            files += glob.glob(f"/tmp/{vid_id}*.mp4")
        files += glob.glob("/tmp/*.mp4")
        if not files:
            return jsonify({"error": "MP4 not found after merge"}), 500

        filepath = max(files, key=os.path.getmtime)
        filename = os.path.basename(filepath)
        return send_file(filepath, mimetype="video/mp4",
                         as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")), debug=False)
