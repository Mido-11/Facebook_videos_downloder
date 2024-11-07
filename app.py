from flask import Flask, render_template, request, redirect, url_for, send_file
import json
import os
import yt_dlp
import io

app = Flask(__name__)
app.secret_key = 'supersecretkey'
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def load_translation(language_code):
    try:
        with open(f'translations/{language_code}.json') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def download_facebook_video(video_url):
    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
        'quiet': True,
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, 'temp_video.%(ext)s'),
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info_dict)
            ext = filename.split('.')[-1]
            return filename, ext
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None, None

@app.route('/', methods=['GET', 'POST'])
def index():
    lang = request.args.get('lang', 'en')
    translations = load_translation(lang)
    
    if request.method == 'POST':
        video_url = request.form.get('video_url')
        filename, ext = download_facebook_video(video_url)
        
        if filename:
            return render_template('index.html', translations=translations, video_file=filename, ext=ext)
    
    return render_template('index.html', translations=translations)

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(DOWNLOAD_FOLDER, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
