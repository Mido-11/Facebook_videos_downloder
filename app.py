from flask import Flask, render_template_string, request, flash, send_file, redirect, url_for
import yt_dlp
import io
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

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
            video_duration = info_dict.get('duration', 0)
            video_size = info_dict.get('filesize', 0)
            video_quality = info_dict.get('format', 'Unknown')
            video_thumbnail = info_dict.get('thumbnail', 'https://via.placeholder.com/150')

            filename = ydl.prepare_filename(info_dict)
            with open(filename, 'rb') as f:
                video_data = io.BytesIO(f.read())

            return video_data, filename.split('.')[-1], video_title, video_uploader, video_duration, video_size, video_quality, video_thumbnail
    except Exception as e:
        return None, None, None, None, None, None, None, None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        video_url = request.form.get('video_url')
        video_data, ext, video_title, video_uploader, video_duration, video_size, video_quality, video_thumbnail = download_facebook_video(video_url)
        if video_data:
            flash('Video details fetched successfully!', 'success')
            video_duration_str = str(video_duration // 60) + 'm ' + str(video_duration % 60) + 's' if video_duration else 'Unknown Duration'
            video_size_str = f"{video_size / 1048576:.2f} MB" if video_size else 'Unknown Size'
            return render_template_string(HTML_TEMPLATE, video_title=video_title, video_uploader=video_uploader, video_duration=video_duration_str, video_size=video_size_str, video_quality=video_quality, video_thumbnail=video_thumbnail, ext=ext, video_data=video_data)
        else:
            flash('Failed to fetch the video details. Please check the URL and try again.', 'danger')

    return render_template_string(HTML_TEMPLATE)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
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
        .video-info { margin-top: 20px; background-color: #f1f3f5; padding: 20px; border-radius: 8px; }
        .video-thumbnail { width: 100%; max-width: 400px; border-radius: 8px; }
        .alert { margin-top: 20px; }
        .footer { margin-top: 30px; font-size: 0.9em; color: #888; }
        .btn-custom { margin-top: 15px; background-color: #3b5998; color: white; }
        .btn-custom:hover { background-color: #2d4373; }
        .btn-paste { margin-top: 15px; background-color: #4CAF50; color: white; font-size: 1.2em; }
        .btn-paste:hover { background-color: #45a049; }
        input[type="text"] { width: 70%; margin-right: 10px; }
        .video-container { margin-top: 20px; }
        .video-container iframe { width: 100%; height: 400px; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="banner">FB Video Downloader</div>
        <p>Download any Facebook video easily!</p>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div class="alert alert-{{ messages[0][0] }}" role="alert">
                    {{ messages[0][1] }}
                </div>
            {% endif %}
        {% endwith %}
        {% if video_title %}
            <div class="video-info">
                <h3>{{ video_title }}</h3>
                <p><strong>Uploader:</strong> {{ video_uploader }}</p>
                <p><strong>Duration:</strong> {{ video_duration }}</p>
                <p><strong>Size:</strong> {{ video_size }}</p>
                <p><strong>Quality:</strong> {{ video_quality }}</p>
                <img src="{{ video_thumbnail }}" alt="Video Thumbnail" class="video-thumbnail">
                <br>
                <a href="{{ url_for('download_file', filename='video.' + ext) }}" class="btn btn-custom"><i class="fas fa-download"></i> Download Video</a>
            </div>
            <div class="video-container">
                <iframe src="https://www.youtube.com/embed/{{ video_url }}" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
            </div>
        {% else %}
            <form action="/" method="POST" class="mt-4">
                <div class="mb-3">
                    <input type="text" name="video_url" class="form-control" id="video_url" placeholder="Enter Facebook video URL" required>
                    <button type="button" class="btn btn-paste" onclick="pasteClipboard()">Paste</button>
                </div>
                <button type="submit" class="btn btn-primary">Verify Link</button>
            </form>
        {% endif %}
        <div class="footer">
            <p>@powered by Mido</p>
        </div>
    </div>

    <script>
        function pasteClipboard() {
            navigator.clipboard.readText().then(function(text) {
                document.getElementById("video_url").value = text;
            });
        }
    </script>
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
