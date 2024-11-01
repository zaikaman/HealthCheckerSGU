from flask import Flask, render_template, request, redirect, url_for, flash
import os
from utils.ocr_processing import extract_text_from_image
from utils.gemini_integration import analyze_text_with_gemini

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed if you plan to use flash messages
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit upload size to 16 MB

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Retrieve form data
        username = request.form.get('username')
        password = request.form.get('password')
        print(f"Login attempt with Username: {username}, Password: {password}")  # For testing
        # Placeholder authentication logic (replace with actual logic if needed)
        if username == "admin" and password == "password":  # Dummy check
            flash("Logged in successfully!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password", "danger")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Retrieve form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        print(f"Signup attempt with Username: {username}, Email: {email}, Password: {password}")  # For testing
        # Placeholder registration logic (replace with actual logic if needed)
        flash("Account created successfully!", "success")
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash("No file part in the request", "warning")
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash("No selected file", "warning")
        return redirect(request.url)

    if file:
        # Ensure the 'uploads' folder exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        # Process OCR
        raw_text = extract_text_from_image(filepath)
        
        # Analyze with Gemini AI
        extracted_entities = analyze_text_with_gemini(raw_text).replace('\n', ' ')  # Ensure display on one line
        
        # Delete file after processing
        os.remove(filepath)
        
        # Display results
        return render_template('index.html', extracted_text=raw_text, extracted_entities=extracted_entities)
    
    return redirect(request.url)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    # Bind to the Heroku-specified port
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
