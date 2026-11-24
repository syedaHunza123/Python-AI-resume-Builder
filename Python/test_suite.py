import os
import unittest
import tempfile
import json
from app import app
from database.db import init_db, create_user, get_user_by_email, create_resume, get_full_resume, save_full_resume_data, duplicate_resume, delete_resume
from utils.ai_helper import generate_summary, improve_text, suggest_skills
from utils.resume_parser import analyze_resume_text
from utils.pdf_generator import generate_resume_pdf

class ResumeAITestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        init_db()

    def test_user_creation_and_auth(self):
        # Register user
        email = f"test_{int(os.times().user * 1000)}@example.com"
        user_id = create_user("Test User", email, "secret123")
        self.assertIsNotNone(user_id)

        user = get_user_by_email(email)
        self.assertIsNotNone(user)
        self.assertEqual(user['name'], "Test User")

    def test_resume_crud(self):
        user_id = create_user("Resume Owner", "owner@example.com", "pass1234")
        if not user_id:
            user = get_user_by_email("owner@example.com")
            user_id = user['id']

        # Create
        res_id = create_resume(user_id, "DevOps Engineer", "modern")
        self.assertIsNotNone(res_id)

        # Update data
        payload = {
            'title': 'Senior DevOps Lead',
            'template': 'technical',
            'accent_color': '#10b981',
            'target_role': 'DevOps Lead',
            'personal_info': {
                'full_name': 'Jane Doe',
                'professional_title': 'DevOps Lead',
                'email': 'jane@devops.com',
                'summary': 'Passionate cloud engineer with extensive Kubernetes and CI/CD mastery.'
            },
            'skills': [{'name': 'Kubernetes', 'category': 'technical'}],
            'work_experience': [{
                'company_name': 'CloudOps Ltd',
                'job_title': 'Lead Cloud Engineer',
                'employment_type': 'Full-time',
                'start_date': '2020',
                'end_date': 'Present',
                'responsibilities': 'Managed cloud infrastructure.'
            }]
        }
        success, msg = save_full_resume_data(res_id, user_id, payload)
        self.assertTrue(success)

        # Retrieve and verify
        res_data = get_full_resume(res_id, user_id)
        self.assertEqual(res_data['title'], 'Senior DevOps Lead')
        self.assertEqual(res_data['personal_info']['full_name'], 'Jane Doe')
        self.assertEqual(len(res_data['skills']), 1)
        self.assertEqual(len(res_data['work_experience']), 1)

        # Duplicate
        dup_id = duplicate_resume(res_id, user_id)
        self.assertIsNotNone(dup_id)
        dup_data = get_full_resume(dup_id, user_id)
        self.assertIn('(Copy)', dup_data['title'])

        # PDF generation test
        pdf_stream = generate_resume_pdf(res_data, template='technical')
        self.assertGreater(pdf_stream.getbuffer().nbytes, 1000)

        # Delete
        self.assertTrue(delete_resume(dup_id, user_id))

    def test_ai_demo_mode_fallbacks(self):
        # Even without an API key, demo mode must return coherent answers
        success, content, is_demo = generate_summary("John Smith", "Software Architect", "Python, AWS", 8)
        self.assertTrue(success)
        self.assertTrue(len(content) > 30)

        success2, content2, _ = improve_text("Wrote some code and handled database fixes.")
        self.assertTrue(success2)
        self.assertIn("Spearheaded", content2)

    def test_ats_scanner(self):
        sample_text = """
        John Doe
        john@example.com | 555-0199 | linkedin.com/in/johndoe
        Professional Summary:
        Experienced Python developer with expertise in Flask and PostgreSQL.
        Work Experience:
        Acme Corp - Senior Software Engineer
        Spearheaded API migration and optimized database queries.
        Education:
        B.S. in Computer Science from Stanford University
        Skills:
        Python, Flask, PostgreSQL, Docker, Git, Agile
        """
        analysis = analyze_resume_text(sample_text, job_description="Looking for senior Python and Flask engineer with Docker experience.")
        self.assertIn("ats_score", analysis)
        self.assertGreaterEqual(analysis["ats_score"], 60)
        self.assertTrue(analysis["detected_sections"]["summary"])
        self.assertTrue(analysis["detected_sections"]["experience"])

if __name__ == '__main__':
    unittest.main()
