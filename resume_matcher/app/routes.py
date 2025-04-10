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
result_history = []


def init_routes(app):
    from flask import request, render_template, redirect, url_for, session
    from werkzeug.utils import secure_filename
    import os

    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/upload', methods=['POST'])
    def upload_file():
        if 'resumes' not in request.files:
            return 'No file part'

        files = request.files.getlist('resumes')
        if not files or all(f.filename == '' for f in files):
            return 'No files selected'

        uploaded_results = []

        for file in files:
            if file.filename == '':
                continue

            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)

            extracted_text = extract_text_from_pdf(save_path)
            sample_job_description = """
            Looking for a Python developer with Flask, HTML, CSS, SQL and ML experience.
            Must have strong problem-solving skills.
            Familiarity with RESTful APIs and database management is a plus.
            JavaScript knowledge is a bonus.
            """
            resume_keywords = extract_keywords(extracted_text)
            job_keywords = extract_keywords(sample_job_description)
            common_keywords = resume_keywords.intersection(job_keywords)
            match_score = (len(common_keywords) / len(job_keywords)) * 100 if job_keywords else 0

            result = {
                'filename': filename,
                'match_score': f"{match_score:.2f}%",
                'keywords': ', '.join(common_keywords)
            }

            uploaded_resumes.append(result)
            result_history.append(result)
            uploaded_results.append(result)

        # Build result page for multiple uploads
        result_rows = ''.join(
            f"<tr><td>{r['filename']}</td><td>{r['match_score']}</td><td>{r['keywords']}</td></tr>"
            for r in uploaded_results
        )

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta http-equiv="refresh" content="7;url=/admin/dashboard">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" />
        <style>
            body {{
            font-family: 'Segoe UI', sans-serif;
            background: #f4f6f9;
            padding: 40px;
            text-align: center;
            }}
            h2 {{
            color: #28a745;
            }}
            table {{
            width: 80%;
            margin: 20px auto;
            border-collapse: collapse;
            background: white;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }}
            th, td {{
            padding: 12px;
            border-bottom: 1px solid #eee;
            }}
            th {{
            background: #007BFF;
            color: white;
            }}
            .btn {{
            display: inline-block;
            margin-top: 20px;
            background-color: #007BFF;
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            text-decoration: none;
            }}
        </style>
        </head>
        <body>
        <h2><i class="fas fa-check-circle"></i> Resumes Uploaded Successfully</h2>
        <table>
            <tr><th>Filename</th><th>Match Score</th><th>Keywords</th></tr>
            {result_rows}
        </table>
        <a class="btn" href="/admin/dashboard"><i class="fas fa-chart-line"></i> Go to Dashboard</a>
        </body>
        </html>
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

    @app.route('/admin/history')
    def result_history_page():
        if not session.get('admin_logged_in'):
            return redirect('/admin/login')
        return render_template('history.html', history=result_history)



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
