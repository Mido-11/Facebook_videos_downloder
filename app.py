from flask import Flask, render_template_string, request, flash
from flask_babel import Babel
import yt_dlp
import io
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'
babel = Babel(app)

DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(['en', 'ar'])

def download_facebook_video(video_url):
    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
        'quiet': True,
        'outtmpl': 'temp_video.%(ext)s',
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
    if request.method == 'POST':
        video_url = request.form.get('video_url')
        video_data, ext = download_facebook_video(video_url)
        if video_data:
            flash('Video fetched successfully!', 'success')
            return render_template_string(HTML_TEMPLATE, video_data=video_data, ext=ext)
        else:
            flash('Failed to fetch the video. Please check the URL and try again.', 'danger')

    return render_template_string(HTML_TEMPLATE)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="{{ g.locale }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facebook Video Downloader</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
    <style>
        body { background-color: #f8f9fa; font-family: 'Poppins', sans-serif; }
        .container { max-width: 800px; margin-top: 50px; text-align: center; background-color: white; padding: 20px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); border-radius: 8px; }
        .banner { font-size: 2.5em; font-weight: bold; color: #3b5998; margin-bottom: 20px; }
        .alert { margin-top: 20px; }
        .footer { margin-top: 30px; font-size: 0.9em; color: #888; }
        .btn-custom { margin-top: 15px; background-color: #3b5998; color: white; }
        .btn-custom:hover { background-color: #2d4373; }
        input[type="text"] { width: 70%; margin-right: 10px; }
        .toggle { font-size: 2rem; border: .125em solid currentcolor; border-radius: 2em; cursor: pointer; display: block; height: 2em; position: relative; width:3.75em; }
        .toggle span { background-color: currentcolor; border-radius: 2em; display: block;height: 1.5em;left: .25em;position: absolute;top: .25em;width: 1.5em;transition: left .25s;}
        input:checked ~ .toggle span { left: 2em; }
        body.dark-mode { background-color: #121212; color: white; }
        body.dark-mode .container { background-color: #2a2a2a; }
        body.dark-mode .banner { color: #ffc409; }
        body.dark-mode .btn-custom { background-color: #5901d8; }
    </style>
</head>
<body>
    <div class="container">
        <div class="banner">FB Video Downloader</div>
        <p>{{ 'Download any Facebook video easily!' | translate }}</p>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div class="alert alert-{{ messages[0][0] }}" role="alert">
                    {{ messages[0][1] }}
                </div>
            {% endif %}
        {% endwith %}
        <form action="/" method="POST" class="mt-4">
            <div class="mb-3">
                <input type="text" name="video_url" class="form-control" id="video_url" placeholder="{{ 'Enter Facebook video URL' | translate }}" required>
                <button type="submit" class="btn btn-primary">{{ 'Verify Link' | translate }}</button>
            </div>
        </form>

        {% if video_data %}
            <div class="video-container">
                <video controls width="100%">
                    <source src="{{ url_for('view_file', filename='video.' + ext) }}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
                <br>
                <a href="{{ url_for('download_file', filename='video.' + ext) }}" class="btn btn-custom"><i class="fas fa-download"></i> {{ 'Download Video' | translate }}</a>
            </div>
        {% endif %}

        <div class="footer">
            <p>@powered by Mido</p>
            <label for="darkmode-toggle" class="toggle">
                <span>{{ 'Toggle dark mode' | translate }}</span>
            </label>
            <input type="checkbox" class="sr-only" id="darkmode-toggle" onchange="document.body.classList.toggle('dark-mode')">
        </div>
    </div>
</body>
</html>
'''

@app.route('/view/<filename>')
def view_file(filename):
    return send_file(filename, mimetype='video/mp4')

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
