from flask import Flask, render_template, request, flash, send_file, redirect, url_for
import yt_dlp
import os
import uuid

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# مسار مجلد التنزيل
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def download_facebook_video(video_url):
    """تنزيل الفيديو من فيسبوك باستخدام yt_dlp."""
    filename = f"{uuid.uuid4()}.mp4"  # توليد اسم ملف فريد
    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
        'quiet': True,
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, filename),
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        return filename
    except Exception as e:
        print(e)
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        video_url = request.form.get('video_url')
        filename = download_facebook_video(video_url)
        if filename:
            flash("تم جلب الفيديو بنجاح. يمكنك تحميله الآن.", "success")
            return render_template('index.html', filename=filename)
        else:
            flash("فشل في جلب الفيديو. يرجى التحقق من الرابط.", "danger")

    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
