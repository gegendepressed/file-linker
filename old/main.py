from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
from gofilepy import GofileClient
import requests
import re
import os

app = Flask(__name__)
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app.config['SECRET_KEY'] = 'your_secret_key'

url = "https://spoo.me"
headers = {
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded"
}

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','docx','csv'}

client = GofileClient()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_valid_password(password):
    if len(password) < 8:
        return False
    if not re.search(r'[a-zA-Z]', password):  
        return False
    if not re.search(r'\d', password):  
        return False
    if not re.search(r'[@.]', password):  
        return False
    if re.search(r'[@.]{2,}', password):  
        return False
    return True

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        short_name = request.form.get('short_name')
        password = request.form.get('password')
        file = request.files['file']

        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if password and not is_valid_password(password):
            flash("Password must be at least 8 characters long, contain a letter, a number, and a special character (@ or .), and not have consecutive special characters.")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            gofile_response = client.upload(file=file)
            page_link = gofile_response.page_link

            shortened_url = None
            if short_name:
                payload = {
                    "url": page_link,
                    "alias": short_name,
                }
            if password:
                    payload["password"] = password

            response = requests.post(url, data=payload, headers=headers)

            if response.status_code == 200:
                shortened_url = response.json().get('short_url')
            else:
                flash(f"Choose a different name for the URL.")

        return render_template('upload.html', shortened_url=shortened_url)

    return render_template('upload.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
