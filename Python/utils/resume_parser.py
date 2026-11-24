import re
from pypdf import PdfReader

# Standard resume section keywords
SECTION_KEYWORDS = {
    "summary": ["summary", "profile", "objective", "professional summary", "about me", "executive summary"],
    "experience": ["experience", "employment", "work history", "work experience", "professional experience", "career"],
    "education": ["education", "academic", "qualifications", "degrees", "university", "college"],
    "skills": ["skills", "competencies", "technologies", "technical skills", "core competencies", "tools"],
    "projects": ["projects", "personal projects", "portfolio", "key initiatives"],
    "certifications": ["certifications", "certificates", "licenses", "credentials"],
    "languages": ["languages", "language proficiency"]
}

# Standard common technical and soft skill keywords for ATS detection
COMMON_KEYWORDS = [
    "python", "javascript", "typescript", "java", "c++", "c#", "html", "css", "sql", "nosql",
    "react", "angular", "vue", "node.js", "django", "flask", "fastapi", "spring boot", "express",
    "docker", "kubernetes", "aws", "azure", "gcp", "git", "ci/cd", "linux", "rest api", "graphql",
    "agile", "scrum", "leadership", "communication", "teamwork", "problem solving", "analytical",
    "project management", "testing", "unit test", "database", "mongodb", "postgresql", "mysql",
    "machine learning", "deep learning", "ai", "pandas", "numpy", "power bi", "tableau", "excel"
]

def extract_text_from_pdf(pdf_file_path):
    """
    Extracts raw text from a PDF file using pypdf.
    """
    try:
        reader = PdfReader(pdf_file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip(), None
    except Exception as e:
        return "", f"Error reading PDF: {str(e)}"

def analyze_resume_text(resume_text, job_description=""):
    """
    Analyzes resume text for ATS structure, section presence, keyword distribution, and readability.
    Compares against optional job description.
    """
    if not resume_text or len(resume_text.strip()) < 50:
        return {
            "error": "Resume text is too short or empty to analyze properly."
        }

    lower_text = resume_text.lower()
    words = re.findall(r'\b[a-z0-9+#.-]+\b', lower_text)
    total_words = len(words)

    # 1. Section presence analysis
    detected_sections = {}
    missing_sections = []
    section_score = 0
    
    # Priority sections
    essential_sections = ["summary", "experience", "education", "skills"]
    optional_sections = ["projects", "certifications", "languages"]

    for sec, aliases in SECTION_KEYWORDS.items():
        found = any(re.search(r'\b' + re.escape(alias) + r'\b', lower_text) for alias in aliases)
        detected_sections[sec] = found
        if not found and sec in essential_sections:
            missing_sections.append(sec.capitalize())

    # Points for essential sections (up to 40 pts)
    for sec in essential_sections:
        if detected_sections.get(sec):
            section_score += 10

    # Points for optional sections (up to 10 pts)
    for sec in optional_sections:
        if detected_sections.get(sec):
            section_score += 3.3
    section_score = min(50, round(section_score))

    # 2. Contact details check
    has_email = bool(re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text))
    has_phone = bool(re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', resume_text))
    has_links = bool(re.search(r'(linkedin\.com|github\.com|http[s]?://)', lower_text))
    contact_score = 0
    if has_email: contact_score += 5
    if has_phone: contact_score += 5
    if has_links: contact_score += 5

    # 3. Readability & Action Verbs
    action_verbs = [
        "managed", "led", "developed", "created", "designed", "implemented", "optimized",
        "engineered", "spearheaded", "accelerated", "resolved", "collaborated", "built", "delivered"
    ]
    found_verbs = [v for v in action_verbs if v in lower_text]
    verb_score = min(15, len(found_verbs) * 2)

    # 4. Length check (ideal resume: 300 to 1200 words)
    length_feedback = "Good length."
    length_score = 15
    if total_words < 150:
        length_feedback = "Resume is too short. Expand on your responsibilities and achievements."
        length_score = 5
    elif total_words < 300:
        length_feedback = "Resume could use more detail and quantified results."
        length_score = 10
    elif total_words > 1500:
        length_feedback = "Resume may be overly lengthy. Try condensing to 1-2 pages."
        length_score = 10

    # Base ATS Score calculation (out of 100)
    base_ats_score = section_score + contact_score + verb_score + length_score
    base_ats_score = max(20, min(95, base_ats_score)) # Keep realistic

    # Suggestions list
    suggestions = []
    if missing_sections:
        suggestions.append(f"Add missing standard sections: {', '.join(missing_sections)}.")
    if not has_email or not has_phone:
        suggestions.append("Ensure your direct contact information (Email and Phone) is prominently placed at the top.")
    if len(found_verbs) < 5:
        suggestions.append("Incorporate more active power verbs (e.g., 'Spearheaded', 'Optimized', 'Architected') in your bullet points.")
    if total_words < 300:
        suggestions.append("Add measurable outcomes (e.g., percentages, revenue, time saved) to substantiate accomplishments.")
    if not detected_sections.get("skills"):
        suggestions.append("Create a dedicated Skills section to optimize keyword parsing by applicant tracking systems.")

    # 5. Job Description comparison (if provided)
    job_analysis = None
    if job_description and len(job_description.strip()) > 20:
        jd_lower = job_description.lower()
        jd_words = set(re.findall(r'\b[a-z0-9+#.-]{3,}\b', jd_lower))
        
        # Stop words to filter out
        stopwords = {
            "and", "the", "for", "with", "that", "this", "from", "have", "will", "our", "you",
            "your", "are", "about", "all", "work", "team", "role", "must", "years", "skills",
            "ability", "strong", "experience", "candidate", "responsibilities", "requirements"
        }
        
        # Find candidate JD keywords (intersect with common skills or frequency)
        jd_keywords = [w for w in jd_words if w not in stopwords and (w in COMMON_KEYWORDS or len(w) > 4)]
        
        matching_keywords = []
        missing_keywords = []
        for kw in jd_keywords[:35]: # Check top candidate terms
            if kw in lower_text:
                matching_keywords.append(kw)
            else:
                missing_keywords.append(kw)
                
        match_rate = round((len(matching_keywords) / max(1, len(jd_keywords[:35]))) * 100)
        
        # Adjust score with JD matching
        ats_with_jd = round((base_ats_score * 0.5) + (match_rate * 0.5))
        
        job_analysis = {
            "match_rate": match_rate,
            "matching_keywords": matching_keywords[:15],
            "missing_keywords": missing_keywords[:15],
            "matched_score": ats_with_jd,
            "jd_suggestions": [
                f"Consider tailoring your resume to include relevant missing keywords like: {', '.join(missing_keywords[:5])}."
            ] if missing_keywords else ["Excellent keyword alignment with this job description!"]
        }

    return {
        "ats_score": job_analysis["matched_score"] if job_analysis else base_ats_score,
        "base_score": base_ats_score,
        "word_count": total_words,
        "detected_sections": detected_sections,
        "missing_sections": missing_sections,
        "contact_info_found": {
            "email": has_email,
            "phone": has_phone,
            "links": has_links
        },
        "action_verbs_found": found_verbs,
        "length_feedback": length_feedback,
        "suggestions": suggestions,
        "job_analysis": job_analysis,
        "disclaimer": "Note: This ATS score is an automated estimation based on standard resume formatting and keyword density practices. It does not guarantee recruiter or ATS acceptance."
    }
