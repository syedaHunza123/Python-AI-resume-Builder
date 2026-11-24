import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database.db')

def get_db_connection():
    """Returns a SQLite connection configured with Row factory and foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Initializes the database schema with all required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Resumes table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL DEFAULT 'Untitled Resume',
        template TEXT NOT NULL DEFAULT 'modern',
        accent_color TEXT DEFAULT '#6366f1',
        font_family TEXT DEFAULT 'Inter',
        target_role TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')

    # Personal Information table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS personal_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER UNIQUE NOT NULL,
        full_name TEXT,
        professional_title TEXT,
        email TEXT,
        phone TEXT,
        location TEXT,
        linkedin_url TEXT,
        github_url TEXT,
        portfolio_url TEXT,
        photo_path TEXT,
        summary TEXT,
        FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
    )
    ''')

    # Work Experience table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS work_experience (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER NOT NULL,
        company_name TEXT NOT NULL,
        job_title TEXT NOT NULL,
        employment_type TEXT,
        start_date TEXT,
        end_date TEXT,
        is_current INTEGER DEFAULT 0,
        responsibilities TEXT,
        achievements TEXT,
        order_index INTEGER DEFAULT 0,
        FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
    )
    ''')

    # Education table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS education (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER NOT NULL,
        institution_name TEXT NOT NULL,
        degree TEXT NOT NULL,
        field_of_study TEXT,
        start_year TEXT,
        graduation_year TEXT,
        grade TEXT,
        order_index INTEGER DEFAULT 0,
        FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
    )
    ''')

    # Skills table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER NOT NULL,
        category TEXT NOT NULL DEFAULT 'technical', -- 'technical', 'soft', 'programming', 'tools'
        name TEXT NOT NULL,
        proficiency TEXT DEFAULT 'Intermediate',
        order_index INTEGER DEFAULT 0,
        FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
    )
    ''')

    # Projects table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER NOT NULL,
        project_name TEXT NOT NULL,
        description TEXT,
        technologies TEXT,
        project_url TEXT,
        order_index INTEGER DEFAULT 0,
        FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
    )
    ''')

    # Certifications table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS certifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER NOT NULL,
        certification_name TEXT NOT NULL,
        issuing_org TEXT,
        issue_date TEXT,
        certificate_url TEXT,
        order_index INTEGER DEFAULT 0,
        FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
    )
    ''')

    # Languages table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS languages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER NOT NULL,
        language_name TEXT NOT NULL,
        proficiency_level TEXT DEFAULT 'Professional Working',
        order_index INTEGER DEFAULT 0,
        FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
    )
    ''')

    # Cover Letters table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cover_letters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        resume_id INTEGER,
        title TEXT NOT NULL,
        job_title TEXT,
        company_name TEXT,
        recipient_name TEXT,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE SET NULL
    )
    ''')

    conn.commit()
    conn.close()

# User Management Helpers
def create_user(name, email, password):
    """Creates a new user with hashed password."""
    conn = get_db_connection()
    cursor = conn.cursor()
    password_hash = generate_password_hash(password)
    try:
        cursor.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email.lower().strip(), password_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return user_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_user_by_email(email):
    """Retrieves user row by email."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email.lower().strip(),))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    """Retrieves user row by id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def update_user_password(user_id, new_password):
    """Updates password for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    password_hash = generate_password_hash(new_password)
    cursor.execute(
        "UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (password_hash, user_id)
    )
    conn.commit()
    conn.close()
    return True

def update_user_profile(user_id, name, email):
    """Updates user profile name and email."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE users SET name = ?, email = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (name.strip(), email.lower().strip(), user_id)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def delete_user_account(user_id):
    """Deletes user account and cascades to all resumes."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True

# Resume CRUD Helpers
def get_user_resumes(user_id):
    """Gets all resumes belonging to a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM resumes WHERE user_id = ? ORDER BY updated_at DESC",
        (user_id,)
    )
    resumes = cursor.fetchall()
    conn.close()
    return resumes

def create_resume(user_id, title="Untitled Resume", template="modern"):
    """Creates a new empty resume for user with default personal_info entry."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO resumes (user_id, title, template) VALUES (?, ?, ?)",
        (user_id, title, template)
    )
    resume_id = cursor.lastrowid
    
    # Initialize blank personal info row
    cursor.execute(
        "INSERT INTO personal_info (resume_id, full_name) VALUES (?, ?)",
        (resume_id, "")
    )
    
    conn.commit()
    conn.close()
    return resume_id

def get_full_resume(resume_id, user_id):
    """Retrieves complete resume data including all related child records if user owns it."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM resumes WHERE id = ? AND user_id = ?", (resume_id, user_id))
    resume = cursor.fetchone()
    if not resume:
        conn.close()
        return None
        
    resume_dict = dict(resume)
    
    # Personal Info
    cursor.execute("SELECT * FROM personal_info WHERE resume_id = ?", (resume_id,))
    p_info = cursor.fetchone()
    resume_dict['personal_info'] = dict(p_info) if p_info else {}
    
    # Work Experience
    cursor.execute("SELECT * FROM work_experience WHERE resume_id = ? ORDER BY order_index ASC, id ASC", (resume_id,))
    resume_dict['work_experience'] = [dict(row) for row in cursor.fetchall()]
    
    # Education
    cursor.execute("SELECT * FROM education WHERE resume_id = ? ORDER BY order_index ASC, id ASC", (resume_id,))
    resume_dict['education'] = [dict(row) for row in cursor.fetchall()]
    
    # Skills
    cursor.execute("SELECT * FROM skills WHERE resume_id = ? ORDER BY order_index ASC, id ASC", (resume_id,))
    resume_dict['skills'] = [dict(row) for row in cursor.fetchall()]
    
    # Projects
    cursor.execute("SELECT * FROM projects WHERE resume_id = ? ORDER BY order_index ASC, id ASC", (resume_id,))
    resume_dict['projects'] = [dict(row) for row in cursor.fetchall()]
    
    # Certifications
    cursor.execute("SELECT * FROM certifications WHERE resume_id = ? ORDER BY order_index ASC, id ASC", (resume_id,))
    resume_dict['certifications'] = [dict(row) for row in cursor.fetchall()]
    
    # Languages
    cursor.execute("SELECT * FROM languages WHERE resume_id = ? ORDER BY order_index ASC, id ASC", (resume_id,))
    resume_dict['languages'] = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return resume_dict

def update_resume_metadata(resume_id, user_id, title=None, template=None, accent_color=None, font_family=None, target_role=None):
    """Updates high-level settings of a resume."""
    conn = get_db_connection()
    cursor = conn.cursor()
    updates = []
    params = []
    
    if title is not None:
        updates.append("title = ?")
        params.append(title)
    if template is not None:
        updates.append("template = ?")
        params.append(template)
    if accent_color is not None:
        updates.append("accent_color = ?")
        params.append(accent_color)
    if font_family is not None:
        updates.append("font_family = ?")
        params.append(font_family)
    if target_role is not None:
        updates.append("target_role = ?")
        params.append(target_role)
        
    if not updates:
        conn.close()
        return True
        
    updates.append("updated_at = CURRENT_TIMESTAMP")
    params.extend([resume_id, user_id])
    
    query = f"UPDATE resumes SET {', '.join(updates)} WHERE id = ? AND user_id = ?"
    cursor.execute(query, params)
    conn.commit()
    conn.close()
    return True

def duplicate_resume(resume_id, user_id):
    """Clones a resume and all its child components for the user."""
    full_data = get_full_resume(resume_id, user_id)
    if not full_data:
        return None
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    new_title = f"{full_data['title']} (Copy)"
    cursor.execute(
        "INSERT INTO resumes (user_id, title, template, accent_color, font_family, target_role) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, new_title, full_data.get('template', 'modern'), full_data.get('accent_color', '#6366f1'), full_data.get('font_family', 'Inter'), full_data.get('target_role', ''))
    )
    new_resume_id = cursor.lastrowid
    
    # Copy Personal Info
    p = full_data.get('personal_info', {})
    cursor.execute('''
        INSERT INTO personal_info (resume_id, full_name, professional_title, email, phone, location, linkedin_url, github_url, portfolio_url, photo_path, summary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (new_resume_id, p.get('full_name'), p.get('professional_title'), p.get('email'), p.get('phone'), p.get('location'), p.get('linkedin_url'), p.get('github_url'), p.get('portfolio_url'), p.get('photo_path'), p.get('summary')))
    
    # Copy Work Experience
    for exp in full_data.get('work_experience', []):
        cursor.execute('''
            INSERT INTO work_experience (resume_id, company_name, job_title, employment_type, start_date, end_date, is_current, responsibilities, achievements, order_index)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (new_resume_id, exp.get('company_name'), exp.get('job_title'), exp.get('employment_type'), exp.get('start_date'), exp.get('end_date'), exp.get('is_current', 0), exp.get('responsibilities'), exp.get('achievements'), exp.get('order_index', 0)))
        
    # Copy Education
    for edu in full_data.get('education', []):
        cursor.execute('''
            INSERT INTO education (resume_id, institution_name, degree, field_of_study, start_year, graduation_year, grade, order_index)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (new_resume_id, edu.get('institution_name'), edu.get('degree'), edu.get('field_of_study'), edu.get('start_year'), edu.get('graduation_year'), edu.get('grade'), edu.get('order_index', 0)))
        
    # Copy Skills
    for skill in full_data.get('skills', []):
        cursor.execute('''
            INSERT INTO skills (resume_id, category, name, proficiency, order_index)
            VALUES (?, ?, ?, ?, ?)
        ''', (new_resume_id, skill.get('category', 'technical'), skill.get('name'), skill.get('proficiency'), skill.get('order_index', 0)))
        
    # Copy Projects
    for proj in full_data.get('projects', []):
        cursor.execute('''
            INSERT INTO projects (resume_id, project_name, description, technologies, project_url, order_index)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (new_resume_id, proj.get('project_name'), proj.get('description'), proj.get('technologies'), proj.get('project_url'), proj.get('order_index', 0)))
        
    # Copy Certifications
    for cert in full_data.get('certifications', []):
        cursor.execute('''
            INSERT INTO certifications (resume_id, certification_name, issuing_org, issue_date, certificate_url, order_index)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (new_resume_id, cert.get('certification_name'), cert.get('issuing_org'), cert.get('issue_date'), cert.get('certificate_url'), cert.get('order_index', 0)))
        
    # Copy Languages
    for lang in full_data.get('languages', []):
        cursor.execute('''
            INSERT INTO languages (resume_id, language_name, proficiency_level, order_index)
            VALUES (?, ?, ?, ?)
        ''', (new_resume_id, lang.get('language_name'), lang.get('proficiency_level'), lang.get('order_index', 0)))
        
    conn.commit()
    conn.close()
    return new_resume_id

def delete_resume(resume_id, user_id):
    """Deletes a resume if the user owns it."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM resumes WHERE id = ? AND user_id = ?", (resume_id, user_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def save_full_resume_data(resume_id, user_id, data):
    """Saves complete resume state from the resume builder JSON payload."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verify ownership
    cursor.execute("SELECT id FROM resumes WHERE id = ? AND user_id = ?", (resume_id, user_id))
    if not cursor.fetchone():
        conn.close()
        return False, "Unauthorized or Resume not found"
        
    # 1. Update resume metadata
    cursor.execute('''
        UPDATE resumes 
        SET title = ?, template = ?, accent_color = ?, font_family = ?, target_role = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (
        data.get('title', 'Untitled Resume'),
        data.get('template', 'modern'),
        data.get('accent_color', '#6366f1'),
        data.get('font_family', 'Inter'),
        data.get('target_role', ''),
        resume_id
    ))
    
    # 2. Update Personal Info
    p = data.get('personal_info', {})
    cursor.execute("SELECT id FROM personal_info WHERE resume_id = ?", (resume_id,))
    exists_p = cursor.fetchone()
    if exists_p:
        cursor.execute('''
            UPDATE personal_info
            SET full_name = ?, professional_title = ?, email = ?, phone = ?, location = ?,
                linkedin_url = ?, github_url = ?, portfolio_url = ?, photo_path = ?, summary = ?
            WHERE resume_id = ?
        ''', (
            p.get('full_name', ''), p.get('professional_title', ''), p.get('email', ''),
            p.get('phone', ''), p.get('location', ''), p.get('linkedin_url', ''),
            p.get('github_url', ''), p.get('portfolio_url', ''), p.get('photo_path', ''),
            p.get('summary', ''), resume_id
        ))
    else:
        cursor.execute('''
            INSERT INTO personal_info (resume_id, full_name, professional_title, email, phone, location, linkedin_url, github_url, portfolio_url, photo_path, summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            resume_id, p.get('full_name', ''), p.get('professional_title', ''), p.get('email', ''),
            p.get('phone', ''), p.get('location', ''), p.get('linkedin_url', ''),
            p.get('github_url', ''), p.get('portfolio_url', ''), p.get('photo_path', ''),
            p.get('summary', '')
        ))
        
    # 3. Work Experience - replace records
    cursor.execute("DELETE FROM work_experience WHERE resume_id = ?", (resume_id,))
    for idx, exp in enumerate(data.get('work_experience', [])):
        if exp.get('company_name') or exp.get('job_title'):
            cursor.execute('''
                INSERT INTO work_experience (resume_id, company_name, job_title, employment_type, start_date, end_date, is_current, responsibilities, achievements, order_index)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                resume_id,
                exp.get('company_name', ''),
                exp.get('job_title', ''),
                exp.get('employment_type', 'Full-time'),
                exp.get('start_date', ''),
                exp.get('end_date', ''),
                1 if exp.get('is_current') else 0,
                exp.get('responsibilities', ''),
                exp.get('achievements', ''),
                idx
            ))
            
    # 4. Education - replace records
    cursor.execute("DELETE FROM education WHERE resume_id = ?", (resume_id,))
    for idx, edu in enumerate(data.get('education', [])):
        if edu.get('institution_name') or edu.get('degree'):
            cursor.execute('''
                INSERT INTO education (resume_id, institution_name, degree, field_of_study, start_year, graduation_year, grade, order_index)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                resume_id,
                edu.get('institution_name', ''),
                edu.get('degree', ''),
                edu.get('field_of_study', ''),
                edu.get('start_year', ''),
                edu.get('graduation_year', ''),
                edu.get('grade', ''),
                idx
            ))
            
    # 5. Skills - replace records
    cursor.execute("DELETE FROM skills WHERE resume_id = ?", (resume_id,))
    for idx, skill in enumerate(data.get('skills', [])):
        if skill.get('name'):
            cursor.execute('''
                INSERT INTO skills (resume_id, category, name, proficiency, order_index)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                resume_id,
                skill.get('category', 'technical'),
                skill.get('name', ''),
                skill.get('proficiency', 'Intermediate'),
                idx
            ))
            
    # 6. Projects - replace records
    cursor.execute("DELETE FROM projects WHERE resume_id = ?", (resume_id,))
    for idx, proj in enumerate(data.get('projects', [])):
        if proj.get('project_name'):
            cursor.execute('''
                INSERT INTO projects (resume_id, project_name, description, technologies, project_url, order_index)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                resume_id,
                proj.get('project_name', ''),
                proj.get('description', ''),
                proj.get('technologies', ''),
                proj.get('project_url', ''),
                idx
            ))
            
    # 7. Certifications - replace records
    cursor.execute("DELETE FROM certifications WHERE resume_id = ?", (resume_id,))
    for idx, cert in enumerate(data.get('certifications', [])):
        if cert.get('certification_name'):
            cursor.execute('''
                INSERT INTO certifications (resume_id, certification_name, issuing_org, issue_date, certificate_url, order_index)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                resume_id,
                cert.get('certification_name', ''),
                cert.get('issuing_org', ''),
                cert.get('issue_date', ''),
                cert.get('certificate_url', ''),
                idx
            ))
            
    # 8. Languages - replace records
    cursor.execute("DELETE FROM languages WHERE resume_id = ?", (resume_id,))
    for idx, lang in enumerate(data.get('languages', [])):
        if lang.get('language_name'):
            cursor.execute('''
                INSERT INTO languages (resume_id, language_name, proficiency_level, order_index)
                VALUES (?, ?, ?, ?)
            ''', (
                resume_id,
                lang.get('language_name', ''),
                lang.get('proficiency_level', 'Professional Working'),
                idx
            ))
            
    conn.commit()
    conn.close()
    return True, "Resume saved successfully"

# Cover letter CRUD
def save_cover_letter(user_id, title, job_title, company_name, recipient_name, content, resume_id=None):
    """Saves or updates a cover letter."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO cover_letters (user_id, resume_id, title, job_title, company_name, recipient_name, content)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, resume_id, title, job_title, company_name, recipient_name, content))
    letter_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return letter_id

def get_user_cover_letters(user_id):
    """Gets all cover letters for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cover_letters WHERE user_id = ? ORDER BY updated_at DESC", (user_id,))
    letters = cursor.fetchall()
    conn.close()
    return letters

def get_cover_letter(letter_id, user_id):
    """Gets a specific cover letter."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cover_letters WHERE id = ? AND user_id = ?", (letter_id, user_id))
    letter = cursor.fetchone()
    conn.close()
    return dict(letter) if letter else None
