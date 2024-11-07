import os
from flask import Flask, render_template_string, request
import yt_dlp
from flask_babel import Babel, _

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')

# Initialize Babel for multi-language support
babel = Babel(app)

# Set default language to English
app.config['LANGUAGES'] = ['en', 'ar']
app.config['BABEL_DEFAULT_LOCALE'] = 'en'

# Make sure the static folder is correctly handled
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static')

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
            video_title = info_dict.get('title', 'Unknown Title')
            video_uploader = info_dict.get('uploader', 'Unknown Uploader')
            filename = ydl.prepare_filename(info_dict)
            return filename
    except Exception as e:
        return None

# Route for selecting language
@babel.init_app
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        video_url = request.form.get('video_url')
        filename = download_facebook_video(video_url)
        if filename:
            return render_template_string(HTML_TEMPLATE, video_url=video_url, filename=filename)
        else:
            return render_template_string(HTML_TEMPLATE, error="Failed to fetch video. Please check the URL.")

    return render_template_string(HTML_TEMPLATE)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="{{ g.locale }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ _('Facebook Video Downloader') }}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f2f5;
            color: #333;
            transition: background-color 0.5s ease;
        }
        .dark-mode {
            background-color: #181818;
            color: #fff;
        }
        .container {
            max-width: 800px;
            margin-top: 50px;
            text-align: center;
            padding: 20px;
            border-radius: 8px;
            background-color: white;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }
        .btn-custom {
            background-color: #3b5998;
            color: white;
            margin-top: 20px;
        }
        .btn-custom:hover {
            background-color: #2d4373;
        }
        .toggle {
            font-size: 2rem;
            border-radius: 2em;
            cursor: pointer;
            display: inline-block;
            width: 3.75em;
            height: 2em;
        }
        .toggle span {
            display: block;
            background-color: currentcolor;
            border-radius: 2em;
            height: 1.5em;
            width: 1.5em;
            transition: left .25s;
        }
        input:checked ~ .toggle span {
            left: 2em;
        }
        input {
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ _('Facebook Video Downloader') }}</h1>
        <form action="/" method="POST">
            <input type="text" name="video_url" class="form-control" placeholder="{{ _('Enter Facebook Video URL') }}" required>
            <button type="submit" class="btn btn-primary mt-3">{{ _('Verify Link') }}</button>
        </form>
        {% if video_url %}
            <br><br>
            <video width="100%" controls>
                <source src="{{ url_for('static', filename=filename) }}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
            <br>
            <a href="{{ url_for('static', filename=filename) }}" class="btn btn-custom">{{ _('Download Video') }}</a>
        {% endif %}
        {% if error %}
            <div class="alert alert-danger mt-4">{{ error }}</div>
        {% endif %}
        <div class="mt-4">
            <label class="toggle">
                <input type="checkbox" onchange="toggleDarkMode()">
                <span>{{ _('Toggle Dark Mode') }}</span>
            </label>
        </div>
    </div>
    <script>
        function toggleDarkMode() {
            document.body.classList.toggle('dark-mode');
        }
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    # Bind the app to the correct host and port for Koyeb
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
