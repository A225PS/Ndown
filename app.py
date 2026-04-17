# Written by: Mohamed El-Sayyad
# Modified for Vercel compatibility

import os
import uuid
import time
from flask import Flask, request, jsonify, send_from_directory, render_template
import yt_dlp
import shutil
import traceback

app = Flask(__name__, template_folder='templates')

# مهم: Vercel بيقبل الكتابة هنا بس
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
            return jsonify(success=False, error='URL required')

        ydl_opts = {
            'quiet': True,
            'skip_download': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = info.get('formats', []) or []
        out = []

        for f in formats:
            out.append({
                'format_id': f.get('format_id'),
                'label': f.get('format_note') or f.get('format'),
                'height': f.get('height'),
                'ext': f.get('ext'),
                'vcodec': f.get('vcodec'),
                'acodec': f.get('acodec'),
                'tbr': f.get('tbr'),
            })

        return jsonify(success=True, formats=out)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'trace': traceback.format_exc()
        })


@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.get_json() or {}
        url = data.get('url')
        fmt = data.get('format', 'best')

        if not url:
            return jsonify({'success': False, 'error': 'URL missing'})

        task_id = str(uuid.uuid4())
        tmp_dir = os.path.join(TMP_FOLDER, task_id)
        os.makedirs(tmp_dir, exist_ok=True)

        output_template = os.path.join(tmp_dir, '%(title)s.%(ext)s')

        ydl_opts = {
            'outtmpl': output_template,
            'quiet': True,
            'format': fmt,
            'noplaylist': True,
            'restrictfilenames': True,
            'merge_output_format': 'mp4',  # يساعد لو في دمج فيديو + صوت
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        produced = None
        for fn in os.listdir(tmp_dir):
            produced = os.path.join(tmp_dir, fn)
            break

        if not produced or not os.path.exists(produced):
            return jsonify({'success': False, 'error': 'No output file'})

        dest_name = f"{task_id}_{os.path.basename(produced)}"
        dest_path = os.path.join(DOWNLOAD_FOLDER, dest_name)

        shutil.move(produced, dest_path)

        return jsonify({
            'success': True,
            'path': f"/file/{dest_name}"
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'trace': traceback.format_exc()
        })


@app.route('/file/<filename>')
def serve_file(filename):
    try:
        file_path = os.path.join(DOWNLOAD_FOLDER, filename)

        if os.path.exists(file_path):
            return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)
        else:
            return "File not found", 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'trace': traceback.format_exc()
        })


# مهم لـ Vercel
app = app
