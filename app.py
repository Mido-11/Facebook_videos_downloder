from flask import Flask, render_template, request, flash, send_file, redirect, url_for
import yt_dlp
import json
import io
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Load translations from JSON file
with open('translations.json', 'r', encoding='utf-8') as f:
    translations = json.load(f)

def get_translation(language, key):
    """Fetches translation based on selected language and key."""
    return translations.get(language, {}).get(key, key)

def download_facebook_video(video_url):
    """Downloads video from a given Facebook URL using yt_dlp."""
    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
        'quiet': True,
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, 'temp_video.%(ext)s'),
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            filename = ydl.prepare_filename(info_dict)
            with open(filename, 'rb') as f:
                video_data = io.BytesIO(f.read())
            return video_data, filename.split('.')[-1]
    except Exception as e:
        return None, None

@app.route('/', methods=['GET', 'POST'])
def index():
    language = request.args.get('lang', 'en')  # Default language is English
    if request.method == 'POST':
        video_url = request.form.get('video_url')
        video_data, ext = download_facebook_video(video_url)
        if video_data:
            flash(get_translation(language, 'video_fetched_success'), 'success')
            return render_template('index.html', language=language, ext=ext)
        else:
            flash(get_translation(language, 'fetch_failed'), 'danger')

    return render_template('index.html', language=language)

@app.route('/view/<filename>')
def view_file(filename):
    return send_file(filename, mimetype='video/mp4')

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
