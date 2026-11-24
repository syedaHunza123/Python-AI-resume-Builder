import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free").strip()
SITE_URL = os.getenv("SITE_URL", "http://localhost:5000")
SITE_NAME = os.getenv("SITE_NAME", "ResumeAI")

OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

def is_ai_configured():
    """Checks if a valid OpenRouter API key is configured."""
    return bool(OPENROUTER_API_KEY and len(OPENROUTER_API_KEY) > 10)

def call_openrouter(system_prompt, user_prompt, temperature=0.7, max_tokens=1000):
    """
    Calls OpenRouter chat completions API.
    Returns (status_boolean, response_text_or_error, is_demo_mode).
    """
    if not is_ai_configured():
        return False, "OpenRouter API Key is not configured. Falling back to Demo Mode.", True

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": SITE_URL,
        "X-Title": SITE_NAME,
        "Content-Type": "application/json"
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    try:
        response = requests.post(OPENROUTER_ENDPOINT, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()
            return True, content, False
        else:
            err_msg = f"API Error ({response.status_code}): {response.text}"
            return False, err_msg, False
    except requests.exceptions.Timeout:
        return False, "Request to OpenRouter timed out. Please try again.", False
    except Exception as e:
        return False, f"Exception during AI generation: {str(e)}", False

# AI Generators with Demo Mode fallbacks
def generate_summary(full_name, title, skills, experience_years=None, target_role=None, existing_summary=None):
    """
    Generates a high-impact, professional executive summary based on actual user info.
    """
    if not is_ai_configured():
        role = target_role or title or "Professional"
        return True, (
            f"[Demo Mode] Results-driven {role} with a proven track record of delivering scalable solutions and operational excellence. "
            f"Proficient in key core competencies including {skills or 'industry standard practices'}. "
            f"Recognized for strong problem-solving abilities, cross-functional collaboration, and consistently driving measurable business outcomes."
        ), True

    system_prompt = (
        "You are an expert executive resume writer. Your job is to write a compelling 3-4 sentence professional resume summary. "
        "CRITICAL RULES:\n"
        "1. Strictly use only the facts, skills, and titles provided by the user.\n"
        "2. NEVER invent fake companies, degrees, unmentioned years of experience, or unmentioned certifications.\n"
        "3. Emphasize impact, clarity, action verbs, and professionalism.\n"
        "4. Return ONLY the summary paragraph text with no introductory pleasantries or markdown quotes."
    )

    user_prompt = f"""
Candidate Name: {full_name or 'N/A'}
Current/Target Title: {title or target_role or 'Professional'}
Skills: {skills or 'N/A'}
Years of Experience: {experience_years or 'Not specified'}
Existing Draft (if any): {existing_summary or 'None provided'}

Please write or refine an impactful professional summary.
"""
    return call_openrouter(system_prompt, user_prompt, temperature=0.6, max_tokens=300)

def improve_text(text, context_type="Work Experience"):
    """
    Improves and refines existing text (bullet points, responsibilities, or summaries) with strong action verbs.
    """
    if not text or not text.strip():
        return False, "Please provide the text you would like to improve.", False

    if not is_ai_configured():
        return True, (
            f"[Demo Mode] • Spearheaded initiatives aligning with key deliverables: {text.strip()}\n"
            f"• Enhanced performance metrics by systematically streamlining workflows and eliminating operational bottlenecks.\n"
            f"• Partnered across cross-functional teams to ensure high reliability and on-time milestone delivery."
        ), True

    system_prompt = (
        f"You are a professional resume editor. Enhance the provided {context_type} text into concise, high-impact bullet points or sentences. "
        "CRITICAL RULES:\n"
        "1. Never invent fictional metrics, tools, or organizations that were not in the source text.\n"
        "2. Begin with powerful action verbs (e.g., Architected, Spearheaded, Accelerated, Optimized).\n"
        "3. Maintain standard professional business English.\n"
        "4. Return ONLY the improved content."
    )

    user_prompt = f"Original text to improve:\n\n{text}"
    return call_openrouter(system_prompt, user_prompt, temperature=0.5, max_tokens=400)

def generate_job_description(job_title, company_name=None, keywords=None):
    """
    Generates standard professional responsibilities and achievement templates for a given role title.
    """
    if not job_title or not job_title.strip():
        return False, "Please specify a job title.", False

    if not is_ai_configured():
        return True, (
            f"[Demo Mode] Responsibilities for {job_title}:\n"
            f"• Led end-to-end execution of projects from inception through production rollout.\n"
            f"• Collaborated with team members to establish quality benchmarks and best practices.\n"
            f"• Resolved complex operational challenges, improving turnaround efficiency by 20%.\n"
            f"• Maintained documentation and communicated technical updates to stakeholders."
        ), True

    system_prompt = (
        "You are an experienced HR and talent acquisition specialist. Generate 4-5 industry-standard, high-impact resume bullet points for the provided job title. "
        "Focus on responsibilities, leadership, and quantifiable achievements. Do not invent proprietary company names. Return bullet points starting with '•'."
    )

    user_prompt = f"Job Title: {job_title}\nCompany: {company_name or 'N/A'}\nKey Focus / Technologies: {keywords or 'General best practices'}"
    return call_openrouter(system_prompt, user_prompt, temperature=0.6, max_tokens=350)

def suggest_skills(job_title_or_role, current_skills=None):
    """
    Suggests in-demand technical and soft skills for a given job title.
    """
    if not job_title_or_role:
        return False, "Please provide a job title or target role.", False

    if not is_ai_configured():
        suggestions = {
            "technical": ["Problem Solving", "Data Analysis", "System Design", "Agile Methodology", "Process Optimization"],
            "soft": ["Communication", "Leadership", "Critical Thinking", "Adaptability", "Collaboration"],
            "tools": ["Git", "Jira", "VS Code", "Docker", "Slack"]
        }
        return True, json.dumps(suggestions), True

    system_prompt = (
        "You are a recruitment specialist. Suggest relevant, highly sought-after skills for a specified role. "
        "Return ONLY a valid JSON object in this exact schema without markdown backticks:\n"
        '{"technical": ["Skill 1", "Skill 2", ...], "soft": ["Skill 1", ...], "tools": ["Tool 1", ...]}'
    )

    user_prompt = f"Target Role: {job_title_or_role}\nCurrent Skills: {current_skills or 'None'}"
    success, res, is_demo = call_openrouter(system_prompt, user_prompt, temperature=0.4, max_tokens=400)
    if success:
        # Clean JSON if wrapped in markdown
        cleaned = res.replace("```json", "").replace("```", "").strip()
        try:
            json.loads(cleaned)
            return True, cleaned, is_demo
        except Exception:
            return True, res, is_demo
    return success, res, is_demo

def review_resume_feedback(resume_data):
    """
    Reviews complete resume JSON and provides constructive critique, strengths, weaknesses, and ATS readiness.
    """
    if not is_ai_configured():
        p_info = resume_data.get('personal_info', {})
        exp_count = len(resume_data.get('work_experience', []))
        edu_count = len(resume_data.get('education', []))
        skills_count = len(resume_data.get('skills', []))
        return True, (
            f"[Demo Mode] **Resume Review & Feedback**\n\n"
            f"**Strengths:**\n"
            f"• Clear structure with {exp_count} experience entries and {edu_count} education records.\n"
            f"• Contact details for {p_info.get('full_name') or 'Candidate'} are present.\n"
            f"• Cataloged {skills_count} verified skills.\n\n"
            f"**Actionable Improvements:**\n"
            f"• Enhance bullet points under work experiences with quantified business outcomes (e.g., % growth, hours saved).\n"
            f"• Ensure your summary highlights your unique value proposition in 3 focused sentences.\n"
            f"• Check that all project entries list concrete technologies used."
        ), True

    system_prompt = (
        "You are a senior executive recruiter and ATS specialist. Review the candidate's resume data thoroughly. "
        "Provide a structured assessment:\n"
        "1. Overall Score out of 100\n"
        "2. Key Strengths (what stands out)\n"
        "3. Areas for Improvement (formatting, clarity, quantification)\n"
        "4. Actionable Next Steps\n"
        "Keep the tone encouraging, direct, and professional."
    )

    user_prompt = f"Resume Data JSON:\n{json.dumps(resume_data, indent=2)}"
    return call_openrouter(system_prompt, user_prompt, temperature=0.5, max_tokens=800)

def generate_cover_letter_content(resume_data, job_title, company_name, job_description=None, recipient_name=None):
    """
    Generates a personalized, professional cover letter matching candidate experience with job specifications.
    """
    p_info = resume_data.get('personal_info', {})
    candidate_name = p_info.get('full_name', 'Applicant')
    
    if not is_ai_configured():
        return True, (
            f"[Demo Mode]\n\n"
            f"Dear {recipient_name or 'Hiring Manager'},\n\n"
            f"I am writing to express my enthusiastic interest in the {job_title} position at {company_name}. "
            f"With my background in {p_info.get('professional_title', 'my professional field')} and proven hands-on experience, "
            f"I am eager to contribute immediately to your team's objectives.\n\n"
            f"Throughout my career, I have honed skills in problem solving, cross-functional execution, and delivering impactful results. "
            f"I admire {company_name}'s dedication to innovation and believe my dedication to excellence makes me a strong fit for this opportunity.\n\n"
            f"Thank you for your time and consideration. I look forward to the opportunity to discuss how my qualifications align with your organizational goals.\n\n"
            f"Sincerely,\n{candidate_name}"
        ), True

    system_prompt = (
        "You are an executive career advisor. Write an engaging, authentic 3-4 paragraph cover letter. "
        "CRITICAL RULES:\n"
        "1. Only mention past experiences and skills that exist in the user's resume data.\n"
        "2. Avoid generic buzzwords; highlight specific tangible contributions.\n"
        "3. Keep formatting standard: Salutation, Opening hook, Relevant experience body, Fit for company, Professional sign-off."
    )

    user_prompt = f"""
Candidate Info:
Name: {candidate_name}
Title: {p_info.get('professional_title', '')}
Summary: {p_info.get('summary', '')}
Recent Work: {[exp.get('job_title') + ' at ' + exp.get('company_name') for exp in resume_data.get('work_experience', [])[:2]]}
Key Skills: {[s.get('name') for s in resume_data.get('skills', [])[:8]]}

Target Position:
Job Title: {job_title}
Company: {company_name}
Hiring Manager: {recipient_name or 'Hiring Manager'}
Job Description / Notes: {job_description or 'None provided'}
"""
    return call_openrouter(system_prompt, user_prompt, temperature=0.6, max_tokens=700)
