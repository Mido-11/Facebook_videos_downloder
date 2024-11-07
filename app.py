from flask import Flask, render_template, request, flash, send_file, url_for, redirect
import yt_dlp
import json
import os
import uuid

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# إنشاء مجلد للتحميلات
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# إعداد الترجمات البسيطة
translations = {
    "ar": {
        "title": "محمل فيديوهات فيسبوك",
        "description": "أدخل رابط الفيديو من فيسبوك لتحميله.",
        "enter_url": "أدخل رابط الفيديو",
        "verify_link": "تحقق من الرابط",
        "view": "عرض",
        "download": "تحميل الفيديو",
        "fetch_failed": "فشل في جلب الفيديو. يرجى التحقق من الرابط.",
        "video_fetched_success": "تم جلب الفيديو بنجاح. يمكنك تحميله الآن.",
        "dark_mode": "الوضع الداكن",
        "light_mode": "الوضع الفاتح"
    },
    "en": {
        "title": "Facebook Video Downloader",
        "description": "Enter the Facebook video URL to download.",
        "enter_url": "Enter the video URL",
        "verify_link": "Verify the Link",
        "view": "View",
        "download": "Download Video",
        "fetch_failed": "Failed to fetch video. Please check the URL.",
        "video_fetched_success": "Video fetched successfully. You can download it now.",
        "dark_mode": "Dark Mode",
        "light_mode": "Light Mode"
    }
}

def get_translation(language, key):
    """احصل على الترجمة المناسبة بناءً على اللغة والمفتاح."""
    return translations.get(language, translations["en"]).get(key, key)

def download_facebook_video(video_url):
    """تنزيل الفيديو من رابط Facebook باستخدام yt_dlp."""
    unique_filename = f"{uuid.uuid4()}.mp4"
    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
        'quiet': True,
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, unique_filename),
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        return unique_filename
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    language = request.args.get('lang', 'en')  # اللغة الافتراضية هي الإنجليزية
    if request.method == 'POST':
        video_url = request.form.get('video_url')
        filename = download_facebook_video(video_url)
        if filename:
            flash(get_translation(language, 'video_fetched_success'), 'success')
            return render_template('index.html', language=language, filename=filename, get_translation=get_translation)
        else:
            flash(get_translation(language, 'fetch_failed'), 'danger')

    return render_template('index.html', language=language, get_translation=get_translation)

@app.route('/view/<filename>')
def view_file(filename):
    return send_file(os.path.join(DOWNLOAD_FOLDER, filename), mimetype='video/mp4')

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    return send_file(file_path, as_attachment=True)

# تمرير دالة الترجمة إلى Jinja
app.jinja_env.globals['get_translation'] = get_translation

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
