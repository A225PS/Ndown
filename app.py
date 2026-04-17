# Simple Video Downloader API (Vercel/Render compatible)

import os
import uuid
import shutil
import traceback
from flask import Flask, request, jsonify, send_from_directory, render_template
import yt_dlp

app = Flask(__name__, template_folder='templates')

DOWNLOAD_FOLDER = "/tmp/downloads"
TMP_FOLDER = "/tmp/tmp"

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(TMP_FOLDER, exist_ok=True)


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/formats', methods=['POST'])
def formats():
    try:
        data = request.get_json() or {}
        url = data.get('url')

        if not url:
            return jsonify(success=False, error="URL required")

        ydl_opts = {
            'quiet': True,
            'skip_download': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = info.get('formats', [])

        result = []
        for f in formats:
            result.append({
                "format_id": f.get("format_id"),
                "ext": f.get("ext"),
                "height": f.get("height"),
                "vcodec": f.get("vcodec"),
                "acodec": f.get("acodec"),
                "label": f.get("format_note") or f.get("format"),
            })

        return jsonify(success=True, formats=result)

    except Exception as e:
        return jsonify(success=False, error=str(e), trace=traceback.format_exc())


@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.get_json() or {}
        url = data.get('url')
        fmt = data.get('format', 'best')

        if not url:
            return jsonify(success=False, error="URL missing")

        task_id = str(uuid.uuid4())
        tmp_dir = os.path.join(TMP_FOLDER, task_id)
        os.makedirs(tmp_dir, exist_ok=True)

        output = os.path.join(tmp_dir, '%(title)s.%(ext)s')

        ydl_opts = {
            'outtmpl': output,
            'quiet': True,
            'format': fmt,
            'noplaylist': True,
            'restrictfilenames': True,
            'merge_output_format': 'mp4',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        file_name = os.listdir(tmp_dir)[0]
        file_path = os.path.join(tmp_dir, file_name)

        final_name = f"{task_id}_{file_name}"
        final_path = os.path.join(DOWNLOAD_FOLDER, final_name)

        shutil.move(file_path, final_path)

        return jsonify({
            "success": True,
            "download": f"/file/{final_name}"
        })

    except Exception as e:
        return jsonify(success=False, error=str(e), trace=traceback.format_exc())


@app.route('/file/<filename>')
def file(filename):
    path = os.path.join(DOWNLOAD_FOLDER, filename)

    if os.path.exists(path):
        return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

    return "File not found", 404


# Vercel entry
app = app
