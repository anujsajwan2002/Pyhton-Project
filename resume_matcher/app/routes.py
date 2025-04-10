import os
from flask import render_template, request
import PyPDF2  
from io import BytesIO
import spacy
nlp = spacy.load("en_core_web_sm")
from werkzeug.utils import secure_filename
from flask import session, redirect, url_for
from flask import send_from_directory



UPLOAD_FOLDER = "app/uploads"
        
uploaded_resumes = []  # Global list to hold resume information

def init_routes(app):
    from flask import request, render_template, redirect, url_for, session
    from werkzeug.utils import secure_filename
    import os

    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/upload', methods=['POST'])
    def upload_file():
        if 'resume' not in request.files:
            return 'No file part'

        file = request.files['resume']
        if file.filename == '':
            return 'No selected file'

        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)

        # Simulated NLP extraction
        extracted_text = extract_text_from_pdf(save_path)
        sample_job_description = """
        Looking for a Python developer with Flask, HTML, CSS, and ML experience.
        Must have strong problem-solving skills and be able to work in a team.
        Responsibilities include developing web applications, collaborating with cross-functional teams, and ensuring code quality.
        Familiarity with RESTful APIs and database management is a plus.
        JavaScript knowledge is a bonus.
        """
        resume_keywords = extract_keywords(extracted_text)
        job_keywords = extract_keywords(sample_job_description)
        common_keywords = resume_keywords.intersection(job_keywords)
        match_score = (len(common_keywords) / len(job_keywords)) * 100 if job_keywords else 0

        uploaded_resumes.append({
            'filename': filename,
            'match_score': f"{match_score:.2f}%",
            'keywords': ', '.join(common_keywords)
        })

        return f"""
        <h3>✅ Resume Uploaded Successfully</h3>
        <p><strong>Match Score:</strong> {match_score:.2f}%</p>
        <p><strong>Matched Keywords:</strong> {', '.join(common_keywords)}</p>
        """

    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        if request.method == 'POST':
            if request.form['username'] == 'admin' and request.form['password'] == 'admin123':
                session['admin_logged_in'] = True
                return redirect('/admin/dashboard')
            else:
                return 'Invalid credentials'
        return render_template('login.html')

    @app.route('/admin/dashboard')
    def admin_dashboard():
        if not session.get('admin_logged_in'):
            return redirect('/admin/login')
        return render_template('dashboard.html', resumes=uploaded_resumes)

    @app.route('/admin/logout')
    def admin_logout():
        session.pop('admin_logged_in', None)
        return redirect('/admin/login')


    @app.route('/uploads/<filename>')
    def download_resume(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)



def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text


def extract_keywords(text):
    doc = nlp(text.lower())
    keywords = set()
    for token in doc:
        if token.is_alpha and not token.is_stop:
            keywords.add(token.lemma_)  # Lemmatize to normalize
    return keywords
