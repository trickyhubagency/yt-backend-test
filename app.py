from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route("/get_link", methods=["POST"])
def get_link():
    url = request.json.get("url")
    try:
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'skip_download': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info['url']
        return jsonify({"cdn_link": video_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
