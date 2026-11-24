import os
import json
from datetime import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for, flash,
    session, jsonify, send_file, abort
)
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Database and Utilities
from database.db import (
    init_db, create_user, get_user_by_email, get_user_by_id,
    update_user_password, update_user_profile, delete_user_account,
    get_user_resumes, create_resume, get_full_resume,
    update_resume_metadata, duplicate_resume, delete_resume,
    save_full_resume_data, save_cover_letter, get_user_cover_letters, get_cover_letter
)
from utils.ai_helper import (
    is_ai_configured, generate_summary, improve_text,
    generate_job_description, suggest_skills, review_resume_feedback,
    generate_cover_letter_content, OPENROUTER_MODEL
)
from utils.pdf_generator import generate_resume_pdf, generate_cover_letter_pdf
from utils.resume_parser import extract_text_from_pdf, analyze_resume_text

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'resumeai-super-secret-key-2026')
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB max upload
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in to access your dashboard and resumes.", "warning")
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Context processor for global template variables
@app.context_processor
def inject_global_data():
    current_user = None
    if 'user_id' in session:
        current_user = get_user_by_id(session['user_id'])
    return {
        'current_user': current_user,
        'ai_configured': is_ai_configured(),
        'ai_model': OPENROUTER_MODEL,
        'current_year': datetime.now().year
    }

# ----------------- Public Routes -----------------

@app.route('/')
def index():
    """Landing Page"""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User Registration"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return render_template('register.html', name=name, email=email)

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template('register.html', name=name, email=email)

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('register.html', name=name, email=email)

        existing_user = get_user_by_email(email)
        if existing_user:
            flash("An account with that email already exists. Please log in.", "warning")
            return redirect(url_for('login'))

        user_id = create_user(name, email, password)
        if user_id:
            session['user_id'] = user_id
            session['user_name'] = name
            
            # Create a starter resume for new user
            starter_id = create_resume(user_id, title="My Professional Resume", template="modern")
            # Populate with candidate name
            starter_data = {
                'title': "My Professional Resume",
                'template': 'modern',
                'accent_color': '#6366f1',
                'personal_info': {
                    'full_name': name,
                    'email': email,
                    'professional_title': 'Software Engineer / Professional',
                    'summary': 'Dedicated and detail-oriented professional with a strong foundation in problem solving and collaborative project delivery.'
                },
                'skills': [
                    {'name': 'Problem Solving', 'category': 'soft'},
                    {'name': 'Project Management', 'category': 'technical'}
                ]
            }
            save_full_resume_data(starter_id, user_id, starter_data)

            flash(f"Welcome to ResumeAI, {name}! Your account is ready.", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Failed to create account. Please try again.", "danger")

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User Login"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = get_user_by_email(email)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash(f"Welcome back, {user['name']}!", "success")
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('dashboard'))
        else:
            flash("Invalid email or password. Please try again.", "danger")

    return render_template('login.html')

@app.route('/logout')
def logout():
    """User Logout"""
    session.clear()
    flash("You have been securely logged out.", "info")
    return redirect(url_for('index'))

# ----------------- Dashboard & Resumes -----------------

@app.route('/dashboard')
@login_required
def dashboard():
    """User Dashboard with real metrics and resumes list"""
    user_id = session['user_id']
    resumes = get_user_resumes(user_id)
    cover_letters = get_user_cover_letters(user_id)
    
    total_resumes = len(resumes)
    last_edited = resumes[0]['updated_at'] if resumes else "No resumes yet"
    
    return render_template(
        'dashboard.html',
        resumes=resumes,
        total_resumes=total_resumes,
        last_edited=last_edited,
        cover_letters=cover_letters
    )

@app.route('/templates')
def template_gallery():
    """Showcase available templates"""
    return render_template('templates.html')

@app.route('/resume/create', methods=['GET', 'POST'])
@login_required
def resume_create():
    """Creates a new resume and redirects to builder"""
    user_id = session['user_id']
    template = request.args.get('template', 'modern')
    title = request.args.get('title', 'New Resume')
    
    resume_id = create_resume(user_id, title=title, template=template)
    flash("New resume initialized! Fill in your details below.", "success")
    return redirect(url_for('resume_builder', resume_id=resume_id))

@app.route('/resume/builder/<int:resume_id>')
@login_required
def resume_builder(resume_id):
    """Interactive multi-step resume builder wizard"""
    user_id = session['user_id']
    resume = get_full_resume(resume_id, user_id)
    if not resume:
        flash("Resume not found or access denied.", "danger")
        return redirect(url_for('dashboard'))

    return render_template('resume_builder.html', resume=resume, resume_json=json.dumps(resume))

@app.route('/resume/preview/<int:resume_id>')
@login_required
def resume_preview(resume_id):
    """Full-screen preview page before printing or downloading"""
    user_id = session['user_id']
    resume = get_full_resume(resume_id, user_id)
    if not resume:
        flash("Resume not found.", "danger")
        return redirect(url_for('dashboard'))

    return render_template('resume_preview.html', resume=resume, resume_json=json.dumps(resume))

@app.route('/resume/save/<int:resume_id>', methods=['POST'])
@login_required
def resume_save(resume_id):
    """API endpoint to save full resume data from builder"""
    user_id = session['user_id']
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data received'}), 400

    success, msg = save_full_resume_data(resume_id, user_id, data)
    if success:
        return jsonify({'success': True, 'message': msg})
    else:
        return jsonify({'success': False, 'message': msg}), 403

@app.route('/resume/duplicate/<int:resume_id>', methods=['POST'])
@login_required
def resume_duplicate(resume_id):
    """Duplicates an existing resume"""
    user_id = session['user_id']
    new_id = duplicate_resume(resume_id, user_id)
    if new_id:
        flash("Resume duplicated successfully!", "success")
    else:
        flash("Could not duplicate resume.", "danger")
    return redirect(url_for('dashboard'))

@app.route('/resume/delete/<int:resume_id>', methods=['POST'])
@login_required
def resume_delete(resume_id):
    """Deletes a resume"""
    user_id = session['user_id']
    if delete_resume(resume_id, user_id):
        flash("Resume deleted successfully.", "info")
    else:
        flash("Resume not found or could not be deleted.", "danger")
    return redirect(url_for('dashboard'))

@app.route('/resume/export/pdf/<int:resume_id>')
@login_required
def export_pdf(resume_id):
    """Downloads resume as clean, formatted PDF"""
    user_id = session['user_id']
    template_override = request.args.get('template')
    
    resume = get_full_resume(resume_id, user_id)
    if not resume:
        flash("Resume not found.", "danger")
        return redirect(url_for('dashboard'))

    template = template_override or resume.get('template', 'modern')
    pdf_stream = generate_resume_pdf(resume, template=template)
    
    clean_title = secure_filename(resume.get('title', 'resume')) or 'resume'
    filename = f"{clean_title}.pdf"
    
    return send_file(
        pdf_stream,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )

@app.route('/resume/upload-photo/<int:resume_id>', methods=['POST'])
@login_required
def upload_photo(resume_id):
    """Uploads a profile photo for the resume"""
    user_id = session['user_id']
    resume = get_full_resume(resume_id, user_id)
    if not resume:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    if 'photo' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'}), 400

    file = request.files['photo']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        new_filename = f"avatar_{resume_id}_{int(datetime.now().timestamp())}.{ext}"
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        file.save(save_path)
        
        rel_url = f"/static/uploads/{new_filename}"
        return jsonify({'success': True, 'photo_url': rel_url})

    return jsonify({'success': False, 'message': 'File type not allowed (use png, jpg, jpeg)'}), 400

# ----------------- AI Assistant Endpoints -----------------

@app.route('/api/ai/generate-summary', methods=['POST'])
@login_required
def api_ai_summary():
    """Generates professional summary using OpenRouter or Demo Mode"""
    data = request.get_json() or {}
    success, result, is_demo = generate_summary(
        full_name=data.get('full_name'),
        title=data.get('title'),
        skills=data.get('skills'),
        experience_years=data.get('experience_years'),
        target_role=data.get('target_role'),
        existing_summary=data.get('existing_summary')
    )
    return jsonify({'success': success, 'content': result, 'is_demo': is_demo})

@app.route('/api/ai/improve-text', methods=['POST'])
@login_required
def api_ai_improve():
    """Improves bullet point or text with action verbs and impact"""
    data = request.get_json() or {}
    text = data.get('text', '')
    context_type = data.get('context_type', 'Work Experience')
    success, result, is_demo = improve_text(text, context_type)
    return jsonify({'success': success, 'content': result, 'is_demo': is_demo})

@app.route('/api/ai/job-description', methods=['POST'])
@login_required
def api_ai_job_description():
    """Generates standard responsibilities for a job title"""
    data = request.get_json() or {}
    job_title = data.get('job_title', '')
    company = data.get('company_name', '')
    keywords = data.get('keywords', '')
    success, result, is_demo = generate_job_description(job_title, company, keywords)
    return jsonify({'success': success, 'content': result, 'is_demo': is_demo})

@app.route('/api/ai/suggest-skills', methods=['POST'])
@login_required
def api_ai_skills():
    """Suggests relevant skills for target role"""
    data = request.get_json() or {}
    role = data.get('role', '')
    current_skills = data.get('current_skills', '')
    success, result, is_demo = suggest_skills(role, current_skills)
    return jsonify({'success': success, 'content': result, 'is_demo': is_demo})

@app.route('/api/ai/review-resume', methods=['POST'])
@login_required
def api_ai_review():
    """Critiques resume and provides feedback"""
    data = request.get_json() or {}
    resume_data = data.get('resume_data', {})
    success, result, is_demo = review_resume_feedback(resume_data)
    return jsonify({'success': success, 'content': result, 'is_demo': is_demo})

# ----------------- ATS Resume Checker -----------------

@app.route('/ats-checker', methods=['GET', 'POST'])
@login_required
def ats_checker():
    """ATS Resume Scanner page with file upload and job description matching"""
    result = None
    extracted_text = ""
    job_description = ""

    if request.method == 'POST':
        job_description = request.form.get('job_description', '')
        
        # Check if text was pasted or PDF uploaded
        pasted_text = request.form.get('resume_text', '').strip()
        uploaded_file = request.files.get('resume_file')

        if uploaded_file and uploaded_file.filename != '':
            if not allowed_file(uploaded_file.filename) or not uploaded_file.filename.lower().endswith('.pdf'):
                flash("Please upload a valid PDF file.", "danger")
                return render_template('ats_checker.html', result=None)

            # Save temporary PDF to parse
            temp_filename = f"temp_ats_{session['user_id']}_{int(datetime.now().timestamp())}.pdf"
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
            uploaded_file.save(temp_path)

            extracted_text, error = extract_text_from_pdf(temp_path)
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

            if error:
                flash(f"Error parsing PDF: {error}", "danger")
                return render_template('ats_checker.html', result=None)
        elif pasted_text:
            extracted_text = pasted_text
        else:
            flash("Please either upload a PDF resume or paste your resume text.", "warning")
            return render_template('ats_checker.html', result=None)

        result = analyze_resume_text(extracted_text, job_description)

    return render_template('ats_checker.html', result=result, extracted_text=extracted_text, job_description=job_description)

# ----------------- Cover Letter Generator -----------------

@app.route('/cover-letter', methods=['GET', 'POST'])
@login_required
def cover_letter():
    """Generate, edit, and download AI cover letters"""
    user_id = session['user_id']
    resumes = get_user_resumes(user_id)
    letters = get_user_cover_letters(user_id)

    generated_letter = None
    job_title = ""
    company_name = ""
    recipient_name = ""
    job_description = ""
    selected_resume_id = None
    is_demo = False

    if request.method == 'POST':
        action = request.form.get('action')
        job_title = request.form.get('job_title', '').strip()
        company_name = request.form.get('company_name', '').strip()
        recipient_name = request.form.get('recipient_name', '').strip()
        job_description = request.form.get('job_description', '').strip()
        selected_resume_id = request.form.get('resume_id')

        if action == 'generate':
            if not job_title or not company_name:
                flash("Please provide at least a Job Title and Company Name.", "warning")
            else:
                resume_data = {}
                if selected_resume_id:
                    resume_data = get_full_resume(selected_resume_id, user_id) or {}

                success, content, is_demo = generate_cover_letter_content(
                    resume_data=resume_data,
                    job_title=job_title,
                    company_name=company_name,
                    job_description=job_description,
                    recipient_name=recipient_name
                )
                generated_letter = content
                if is_demo:
                    flash("AI generated cover letter in Demo Mode (add OpenRouter API key in .env for custom AI).", "info")

        elif action == 'save':
            letter_content = request.form.get('content', '').strip()
            title = f"Cover Letter - {job_title} at {company_name}"
            save_cover_letter(user_id, title, job_title, company_name, recipient_name, letter_content, selected_resume_id)
            flash("Cover letter saved successfully!", "success")
            return redirect(url_for('cover_letter'))

    return render_template(
        'cover_letter.html',
        resumes=resumes,
        letters=letters,
        generated_letter=generated_letter,
        job_title=job_title,
        company_name=company_name,
        recipient_name=recipient_name,
        job_description=job_description,
        selected_resume_id=selected_resume_id,
        is_demo=is_demo
    )

@app.route('/cover-letter/download/<int:letter_id>')
@login_required
def download_cover_letter_pdf(letter_id):
    """Downloads saved cover letter as PDF"""
    user_id = session['user_id']
    letter = get_cover_letter(letter_id, user_id)
    if not letter:
        flash("Cover letter not found.", "danger")
        return redirect(url_for('cover_letter'))

    pdf_stream = generate_cover_letter_pdf(letter, user_name=session.get('user_name', 'Applicant'))
    clean_title = secure_filename(letter.get('title', 'cover_letter'))
    return send_file(
        pdf_stream,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"{clean_title}.pdf"
    )

# ----------------- Settings & Profile -----------------

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """User profile, security, and application settings"""
    user_id = session['user_id']
    user = get_user_by_id(user_id)

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_profile':
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip().lower()
            if not name or not email:
                flash("Name and email are required.", "warning")
            else:
                success = update_user_profile(user_id, name, email)
                if success:
                    session['user_name'] = name
                    flash("Profile updated successfully!", "success")
                else:
                    flash("Email is already in use by another account.", "danger")

        elif action == 'change_password':
            current_pw = request.form.get('current_password', '')
            new_pw = request.form.get('new_password', '')
            confirm_pw = request.form.get('confirm_password', '')

            if not check_password_hash(user['password_hash'], current_pw):
                flash("Current password incorrect.", "danger")
            elif len(new_pw) < 6:
                flash("New password must be at least 6 characters.", "warning")
            elif new_pw != confirm_pw:
                flash("New passwords do not match.", "warning")
            else:
                update_user_password(user_id, new_pw)
                flash("Password changed successfully!", "success")

        elif action == 'delete_account':
            confirm = request.form.get('confirm_delete')
            if confirm == 'DELETE':
                delete_user_account(user_id)
                session.clear()
                flash("Your account and all associated resumes have been permanently deleted.", "info")
                return redirect(url_for('index'))
            else:
                flash("Type DELETE to confirm account deletion.", "danger")

        return redirect(url_for('settings'))

    return render_template('settings.html', user=user)

# Run entry point
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
