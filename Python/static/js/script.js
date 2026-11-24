/**
 * ResumeAI - Interactive Resume Builder & Live Preview Engine
 */

let resumeData = {};
let currentStep = 1;
const totalSteps = 8;

document.addEventListener('DOMContentLoaded', () => {
  // Parse injected resume JSON
  const rawJsonEl = document.getElementById('initial-resume-data');
  if (rawJsonEl) {
    try {
      resumeData = JSON.parse(rawJsonEl.textContent);
    } catch (e) {
      console.error("Failed to parse resume JSON", e);
    }
  }

  // Ensure default structures
  resumeData.personal_info = resumeData.personal_info || {};
  resumeData.work_experience = resumeData.work_experience || [];
  resumeData.education = resumeData.education || [];
  resumeData.skills = resumeData.skills || [];
  resumeData.projects = resumeData.projects || [];
  resumeData.certifications = resumeData.certifications || [];
  resumeData.languages = resumeData.languages || [];

  // Initialize UI forms with existing data
  populateFormFields();
  renderDynamicLists();
  renderLivePreview();
  attachEventListeners();
});

// Switch wizard steps
function goToStep(step) {
  if (step < 1 || step > totalSteps) return;
  currentStep = step;

  // Update pill indicators
  document.querySelectorAll('.step-pill').forEach(pill => {
    const s = parseInt(pill.getAttribute('data-step'));
    pill.classList.remove('active');
    if (s === currentStep) {
      pill.classList.add('active');
    }
  });

  // Show corresponding section
  document.querySelectorAll('.wizard-section').forEach(sec => {
    sec.classList.add('d-none');
  });
  const activeSec = document.getElementById(`step-content-${currentStep}`);
  if (activeSec) {
    activeSec.classList.remove('d-none');
  }

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function nextStep() {
  saveCurrentState();
  goToStep(currentStep + 1);
}

function prevStep() {
  saveCurrentState();
  goToStep(currentStep - 1);
}

// Populate basic inputs from resumeData
function populateFormFields() {
  const p = resumeData.personal_info || {};
  const setVal = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.value = val || '';
  };

  setVal('input-title', resumeData.title);
  setVal('select-template', resumeData.template || 'modern');
  setVal('input-accent-color', resumeData.accent_color || '#6366f1');
  setVal('input-target-role', resumeData.target_role);

  // Personal Info
  setVal('pi-fullname', p.full_name);
  setVal('pi-title', p.professional_title);
  setVal('pi-email', p.email);
  setVal('pi-phone', p.phone);
  setVal('pi-location', p.location);
  setVal('pi-linkedin', p.linkedin_url);
  setVal('pi-github', p.github_url);
  setVal('pi-portfolio', p.portfolio_url);
  setVal('pi-summary', p.summary);

  if (p.photo_path) {
    const preview = document.getElementById('photo-preview-img');
    if (preview) {
      preview.src = p.photo_path;
      preview.classList.remove('d-none');
    }
  }
}

// Attach input listeners for live typing sync
function attachEventListeners() {
  // Sync text inputs
  const bindInput = (id, callback) => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener('input', (e) => {
        callback(e.target.value);
        renderLivePreview();
      });
    }
  };

  bindInput('input-title', v => resumeData.title = v);
  bindInput('input-target-role', v => resumeData.target_role = v);
  bindInput('input-accent-color', v => {
    resumeData.accent_color = v;
    document.documentElement.style.setProperty('--resume-accent', v);
  });
  bindInput('select-template', v => {
    resumeData.template = v;
    const paper = document.getElementById('resume-paper');
    if (paper) {
      paper.className = `resume-paper tpl-${v}`;
    }
  });

  // Personal info bindings
  const p = resumeData.personal_info;
  bindInput('pi-fullname', v => p.full_name = v);
  bindInput('pi-title', v => p.professional_title = v);
  bindInput('pi-email', v => p.email = v);
  bindInput('pi-phone', v => p.phone = v);
  bindInput('pi-location', v => p.location = v);
  bindInput('pi-linkedin', v => p.linkedin_url = v);
  bindInput('pi-github', v => p.github_url = v);
  bindInput('pi-portfolio', v => p.portfolio_url = v);
  bindInput('pi-summary', v => p.summary = v);

  // Photo upload handler
  const photoInput = document.getElementById('photo-file-input');
  if (photoInput) {
    photoInput.addEventListener('change', uploadPhotoHandler);
  }
}

// Save current inputs into resumeData before moving steps
function saveCurrentState() {
  const p = resumeData.personal_info;
  const getVal = id => {
    const el = document.getElementById(id);
    return el ? el.value.trim() : '';
  };

  resumeData.title = getVal('input-title') || 'Untitled Resume';
  resumeData.target_role = getVal('input-target-role');
  resumeData.template = getVal('select-template') || 'modern';
  resumeData.accent_color = getVal('input-accent-color') || '#6366f1';

  p.full_name = getVal('pi-fullname');
  p.professional_title = getVal('pi-title');
  p.email = getVal('pi-email');
  p.phone = getVal('pi-phone');
  p.location = getVal('pi-location');
  p.linkedin_url = getVal('pi-linkedin');
  p.github_url = getVal('pi-github');
  p.portfolio_url = getVal('pi-portfolio');
  p.summary = getVal('pi-summary');
}

// Dynamic List Rendering (Work Experience, Education, Skills, Projects, etc.)
function renderDynamicLists() {
  renderWorkExpList();
  renderEducationList();
  renderSkillsList();
  renderProjectsList();
  renderCertificationsList();
  renderLanguagesList();
}

// 1. Work Experience
function renderWorkExpList() {
  const container = document.getElementById('work-experience-list');
  if (!container) return;
  container.innerHTML = '';

  resumeData.work_experience.forEach((exp, idx) => {
    const card = document.createElement('div');
    card.className = 'card-saas p-3 mb-3 border';
    card.innerHTML = `
      <div class="d-flex justify-content-between align-items-center mb-2">
        <strong class="text-primary small">#${idx + 1} Work Experience</strong>
        <div class="d-flex gap-2">
          <button type="button" class="btn btn-outline-info btn-sm py-0" onclick="aiImproveExp(${idx})">
            <i class="fa-solid fa-wand-magic-sparkles"></i> AI Improve
          </button>
          <button type="button" class="btn btn-outline-danger btn-sm py-0" onclick="removeWorkExp(${idx})">
            <i class="fa-solid fa-trash"></i>
          </button>
        </div>
      </div>
      <div class="row g-2 mb-2">
        <div class="col-md-6">
          <label class="form-label small">Company Name *</label>
          <input type="text" class="form-control form-control-sm" value="${exp.company_name || ''}" oninput="updateWorkExpField(${idx}, 'company_name', this.value)">
        </div>
        <div class="col-md-6">
          <label class="form-label small">Job Title *</label>
          <input type="text" class="form-control form-control-sm" value="${exp.job_title || ''}" oninput="updateWorkExpField(${idx}, 'job_title', this.value)">
        </div>
      </div>
      <div class="row g-2 mb-2">
        <div class="col-md-4">
          <label class="form-label small">Employment Type</label>
          <select class="form-select form-select-sm" onchange="updateWorkExpField(${idx}, 'employment_type', this.value)">
            <option value="Full-time" ${exp.employment_type === 'Full-time' ? 'selected' : ''}>Full-time</option>
            <option value="Part-time" ${exp.employment_type === 'Part-time' ? 'selected' : ''}>Part-time</option>
            <option value="Contract" ${exp.employment_type === 'Contract' ? 'selected' : ''}>Contract</option>
            <option value="Internship" ${exp.employment_type === 'Internship' ? 'selected' : ''}>Internship</option>
          </select>
        </div>
        <div class="col-md-4">
          <label class="form-label small">Start Date</label>
          <input type="text" class="form-control form-control-sm" placeholder="e.g. Jun 2021" value="${exp.start_date || ''}" oninput="updateWorkExpField(${idx}, 'start_date', this.value)">
        </div>
        <div class="col-md-4">
          <label class="form-label small">End Date</label>
          <input type="text" class="form-control form-control-sm" placeholder="e.g. Present" value="${exp.end_date || ''}" oninput="updateWorkExpField(${idx}, 'end_date', this.value)">
        </div>
      </div>
      <div class="mb-2">
        <label class="form-label small">Job Responsibilities</label>
        <textarea class="form-control form-control-sm" rows="3" placeholder="Bullet points of key tasks..." oninput="updateWorkExpField(${idx}, 'responsibilities', this.value)">${exp.responsibilities || ''}</textarea>
      </div>
      <div class="mb-1">
        <label class="form-label small">Key Achievements</label>
        <textarea class="form-control form-control-sm" rows="2" placeholder="Measurable outcomes (e.g. Increased speed by 40%)..." oninput="updateWorkExpField(${idx}, 'achievements', this.value)">${exp.achievements || ''}</textarea>
      </div>
    `;
    container.appendChild(card);
  });
}

function addWorkExp() {
  resumeData.work_experience.push({
    company_name: '',
    job_title: '',
    employment_type: 'Full-time',
    start_date: '',
    end_date: '',
    responsibilities: '',
    achievements: ''
  });
  renderWorkExpList();
  renderLivePreview();
}

function updateWorkExpField(idx, field, val) {
  if (resumeData.work_experience[idx]) {
    resumeData.work_experience[idx][field] = val;
    renderLivePreview();
  }
}

function removeWorkExp(idx) {
  resumeData.work_experience.splice(idx, 1);
  renderWorkExpList();
  renderLivePreview();
}

// 2. Education
function renderEducationList() {
  const container = document.getElementById('education-list');
  if (!container) return;
  container.innerHTML = '';

  resumeData.education.forEach((edu, idx) => {
    const card = document.createElement('div');
    card.className = 'card-saas p-3 mb-3 border';
    card.innerHTML = `
      <div class="d-flex justify-content-between align-items-center mb-2">
        <strong class="text-primary small">#${idx + 1} Education</strong>
        <button type="button" class="btn btn-outline-danger btn-sm py-0" onclick="removeEducation(${idx})">
          <i class="fa-solid fa-trash"></i>
        </button>
      </div>
      <div class="row g-2 mb-2">
        <div class="col-md-6">
          <label class="form-label small">Institution Name *</label>
          <input type="text" class="form-control form-control-sm" value="${edu.institution_name || ''}" oninput="updateEduField(${idx}, 'institution_name', this.value)">
        </div>
        <div class="col-md-6">
          <label class="form-label small">Degree *</label>
          <input type="text" class="form-control form-control-sm" placeholder="e.g. Bachelor of Science" value="${edu.degree || ''}" oninput="updateEduField(${idx}, 'degree', this.value)">
        </div>
      </div>
      <div class="row g-2 mb-2">
        <div class="col-md-4">
          <label class="form-label small">Field of Study</label>
          <input type="text" class="form-control form-control-sm" placeholder="e.g. Computer Science" value="${edu.field_of_study || ''}" oninput="updateEduField(${idx}, 'field_of_study', this.value)">
        </div>
        <div class="col-md-3">
          <label class="form-label small">Start Year</label>
          <input type="text" class="form-control form-control-sm" placeholder="2018" value="${edu.start_year || ''}" oninput="updateEduField(${idx}, 'start_year', this.value)">
        </div>
        <div class="col-md-3">
          <label class="form-label small">Graduation Year</label>
          <input type="text" class="form-control form-control-sm" placeholder="2022" value="${edu.graduation_year || ''}" oninput="updateEduField(${idx}, 'graduation_year', this.value)">
        </div>
        <div class="col-md-2">
          <label class="form-label small">Grade / CGPA</label>
          <input type="text" class="form-control form-control-sm" placeholder="3.8 / 4.0" value="${edu.grade || ''}" oninput="updateEduField(${idx}, 'grade', this.value)">
        </div>
      </div>
    `;
    container.appendChild(card);
  });
}

function addEducation() {
  resumeData.education.push({
    institution_name: '',
    degree: '',
    field_of_study: '',
    start_year: '',
    graduation_year: '',
    grade: ''
  });
  renderEducationList();
  renderLivePreview();
}

function updateEduField(idx, field, val) {
  if (resumeData.education[idx]) {
    resumeData.education[idx][field] = val;
    renderLivePreview();
  }
}

function removeEducation(idx) {
  resumeData.education.splice(idx, 1);
  renderEducationList();
  renderLivePreview();
}

// 3. Skills
function renderSkillsList() {
  const container = document.getElementById('skills-chips-container');
  if (!container) return;
  container.innerHTML = '';

  resumeData.skills.forEach((skill, idx) => {
    const chip = document.createElement('span');
    chip.className = 'badge bg-primary-subtle text-primary border border-primary-subtle p-2 d-inline-flex align-items-center gap-2 m-1';
    chip.innerHTML = `
      <span>${skill.name}</span>
      <span class="text-muted" style="font-size: 10px;">(${skill.category || 'tech'})</span>
      <i class="fa-solid fa-xmark cursor-pointer" onclick="removeSkill(${idx})" title="Remove skill"></i>
    `;
    container.appendChild(chip);
  });
}

function addSkillFromInput() {
  const input = document.getElementById('new-skill-input');
  const catSelect = document.getElementById('new-skill-cat');
  if (!input || !input.value.trim()) return;

  const skillName = input.value.trim();
  const cat = catSelect ? catSelect.value : 'technical';

  resumeData.skills.push({ name: skillName, category: cat });
  input.value = '';
  renderSkillsList();
  renderLivePreview();
}

function removeSkill(idx) {
  resumeData.skills.splice(idx, 1);
  renderSkillsList();
  renderLivePreview();
}

// 4. Projects
function renderProjectsList() {
  const container = document.getElementById('projects-list');
  if (!container) return;
  container.innerHTML = '';

  resumeData.projects.forEach((proj, idx) => {
    const card = document.createElement('div');
    card.className = 'card-saas p-3 mb-3 border';
    card.innerHTML = `
      <div class="d-flex justify-content-between align-items-center mb-2">
        <strong class="text-primary small">#${idx + 1} Project</strong>
        <button type="button" class="btn btn-outline-danger btn-sm py-0" onclick="removeProject(${idx})">
          <i class="fa-solid fa-trash"></i>
        </button>
      </div>
      <div class="row g-2 mb-2">
        <div class="col-md-6">
          <label class="form-label small">Project Name *</label>
          <input type="text" class="form-control form-control-sm" value="${proj.project_name || ''}" oninput="updateProjField(${idx}, 'project_name', this.value)">
        </div>
        <div class="col-md-6">
          <label class="form-label small">Project URL / GitHub</label>
          <input type="text" class="form-control form-control-sm" placeholder="https://..." value="${proj.project_url || ''}" oninput="updateProjField(${idx}, 'project_url', this.value)">
        </div>
      </div>
      <div class="mb-2">
        <label class="form-label small">Technologies Used</label>
        <input type="text" class="form-control form-control-sm" placeholder="e.g. Python, Flask, SQLite" value="${proj.technologies || ''}" oninput="updateProjField(${idx}, 'technologies', this.value)">
      </div>
      <div class="mb-1">
        <label class="form-label small">Description</label>
        <textarea class="form-control form-control-sm" rows="2" placeholder="Key highlights and purpose..." oninput="updateProjField(${idx}, 'description', this.value)">${proj.description || ''}</textarea>
      </div>
    `;
    container.appendChild(card);
  });
}

function addProject() {
  resumeData.projects.push({
    project_name: '',
    project_url: '',
    technologies: '',
    description: ''
  });
  renderProjectsList();
  renderLivePreview();
}

function updateProjField(idx, field, val) {
  if (resumeData.projects[idx]) {
    resumeData.projects[idx][field] = val;
    renderLivePreview();
  }
}

function removeProject(idx) {
  resumeData.projects.splice(idx, 1);
  renderProjectsList();
  renderLivePreview();
}

// 5. Certifications
function renderCertificationsList() {
  const container = document.getElementById('certifications-list');
  if (!container) return;
  container.innerHTML = '';

  resumeData.certifications.forEach((cert, idx) => {
    const card = document.createElement('div');
    card.className = 'card-saas p-3 mb-3 border';
    card.innerHTML = `
      <div class="d-flex justify-content-between align-items-center mb-2">
        <strong class="text-primary small">#${idx + 1} Certification</strong>
        <button type="button" class="btn btn-outline-danger btn-sm py-0" onclick="removeCert(${idx})">
          <i class="fa-solid fa-trash"></i>
        </button>
      </div>
      <div class="row g-2 mb-2">
        <div class="col-md-6">
          <label class="form-label small">Certification Name *</label>
          <input type="text" class="form-control form-control-sm" value="${cert.certification_name || ''}" oninput="updateCertField(${idx}, 'certification_name', this.value)">
        </div>
        <div class="col-md-6">
          <label class="form-label small">Issuing Organization</label>
          <input type="text" class="form-control form-control-sm" placeholder="e.g. AWS, Cisco" value="${cert.issuing_org || ''}" oninput="updateCertField(${idx}, 'issuing_org', this.value)">
        </div>
      </div>
      <div class="row g-2">
        <div class="col-md-6">
          <label class="form-label small">Issue Date</label>
          <input type="text" class="form-control form-control-sm" placeholder="e.g. 2023" value="${cert.issue_date || ''}" oninput="updateCertField(${idx}, 'issue_date', this.value)">
        </div>
        <div class="col-md-6">
          <label class="form-label small">Certificate URL</label>
          <input type="text" class="form-control form-control-sm" placeholder="https://..." value="${cert.certificate_url || ''}" oninput="updateCertField(${idx}, 'certificate_url', this.value)">
        </div>
      </div>
    `;
    container.appendChild(card);
  });
}

function addCertification() {
  resumeData.certifications.push({
    certification_name: '',
    issuing_org: '',
    issue_date: '',
    certificate_url: ''
  });
  renderCertificationsList();
  renderLivePreview();
}

function updateCertField(idx, field, val) {
  if (resumeData.certifications[idx]) {
    resumeData.certifications[idx][field] = val;
    renderLivePreview();
  }
}

function removeCert(idx) {
  resumeData.certifications.splice(idx, 1);
  renderCertificationsList();
  renderLivePreview();
}

// 6. Languages
function renderLanguagesList() {
  const container = document.getElementById('languages-list');
  if (!container) return;
  container.innerHTML = '';

  resumeData.languages.forEach((lang, idx) => {
    const card = document.createElement('div');
    card.className = 'd-flex align-items-center gap-2 mb-2';
    card.innerHTML = `
      <input type="text" class="form-control form-control-sm" placeholder="Language (e.g. Spanish)" value="${lang.language_name || ''}" oninput="updateLangField(${idx}, 'language_name', this.value)">
      <select class="form-select form-select-sm" onchange="updateLangField(${idx}, 'proficiency_level', this.value)">
        <option value="Native" ${lang.proficiency_level === 'Native' ? 'selected' : ''}>Native</option>
        <option value="Fluent" ${lang.proficiency_level === 'Fluent' ? 'selected' : ''}>Fluent</option>
        <option value="Professional Working" ${lang.proficiency_level === 'Professional Working' ? 'selected' : ''}>Professional Working</option>
        <option value="Elementary" ${lang.proficiency_level === 'Elementary' ? 'selected' : ''}>Elementary</option>
      </select>
      <button type="button" class="btn btn-outline-danger btn-sm py-1" onclick="removeLanguage(${idx})">
        <i class="fa-solid fa-trash"></i>
      </button>
    `;
    container.appendChild(card);
  });
}

function addLanguage() {
  resumeData.languages.push({
    language_name: '',
    proficiency_level: 'Professional Working'
  });
  renderLanguagesList();
  renderLivePreview();
}

function updateLangField(idx, field, val) {
  if (resumeData.languages[idx]) {
    resumeData.languages[idx][field] = val;
    renderLivePreview();
  }
}

function removeLanguage(idx) {
  resumeData.languages.splice(idx, 1);
  renderLanguagesList();
  renderLivePreview();
}

// Photo upload API call
async function uploadPhotoHandler(e) {
  const file = e.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append('photo', file);

  const spinner = document.getElementById('photo-spinner');
  if (spinner) spinner.classList.remove('d-none');

  try {
    const res = await fetch(`/resume/upload-photo/${resumeData.id}`, {
      method: 'POST',
      body: formData
    });
    const result = await res.json();
    if (result.success) {
      resumeData.personal_info.photo_path = result.photo_url;
      const preview = document.getElementById('photo-preview-img');
      if (preview) {
        preview.src = result.photo_url;
        preview.classList.remove('d-none');
      }
      renderLivePreview();
    } else {
      alert(result.message || 'Photo upload failed');
    }
  } catch (err) {
    console.error(err);
    alert('Error uploading photo');
  } finally {
    if (spinner) spinner.classList.add('d-none');
  }
}

// Render Real-Time Live Preview inside A4 Canvas
function renderLivePreview() {
  const preview = document.getElementById('resume-live-preview');
  if (!preview) return;

  const p = resumeData.personal_info || {};
  const tpl = resumeData.template || 'modern';
  const accent = resumeData.accent_color || '#6366f1';

  // Apply accent color to css property
  document.documentElement.style.setProperty('--resume-accent', accent);

  let contacts = [];
  if (p.email) contacts.push(`<i class="fa-solid fa-envelope me-1"></i> ${p.email}`);
  if (p.phone) contacts.push(`<i class="fa-solid fa-phone me-1"></i> ${p.phone}`);
  if (p.location) contacts.push(`<i class="fa-solid fa-location-dot me-1"></i> ${p.location}`);
  if (p.linkedin_url) contacts.push(`<i class="fa-brands fa-linkedin me-1"></i> LinkedIn`);
  if (p.github_url) contacts.push(`<i class="fa-brands fa-github me-1"></i> GitHub`);
  if (p.portfolio_url) contacts.push(`<i class="fa-solid fa-globe me-1"></i> Portfolio`);

  let html = `
    <!-- Resume Header -->
    <div class="d-flex align-items-center justify-content-between mb-3 border-bottom pb-3">
      <div>
        <h2 class="fw-bold mb-1" style="color: ${tpl === 'modern' || tpl === 'creative' ? accent : '#0f172a'};">${p.full_name || 'Your Full Name'}</h2>
        <div class="fw-semibold text-muted mb-2">${p.professional_title || resumeData.target_role || 'Professional Title'}</div>
        <div class="small text-muted d-flex flex-wrap gap-2">
          ${contacts.join(' • ')}
        </div>
      </div>
      ${p.photo_path ? `<img src="${p.photo_path}" class="rounded-circle shadow-sm border" style="width: 70px; height: 70px; object-fit: cover;">` : ''}
    </div>
  `;

  // Professional Summary
  if (p.summary && p.summary.trim()) {
    html += `
      <div class="mb-3">
        <h6 class="fw-bold text-uppercase pb-1 mb-2 border-bottom" style="color: ${accent};">Professional Summary</h6>
        <p class="small text-dark mb-0">${p.summary.replace(/\n/g, '<br>')}</p>
      </div>
    `;
  }

  // Work Experience
  if (resumeData.work_experience && resumeData.work_experience.length > 0) {
    html += `
      <div class="mb-3">
        <h6 class="fw-bold text-uppercase pb-1 mb-2 border-bottom" style="color: ${accent};">Work Experience</h6>
    `;
    resumeData.work_experience.forEach(exp => {
      if (exp.company_name || exp.job_title) {
        const dates = `${exp.start_date || ''} – ${exp.end_date || 'Present'}`;
        html += `
          <div class="mb-2">
            <div class="d-flex justify-content-between align-items-baseline">
              <strong class="text-dark small">${exp.job_title || 'Role'} <span class="fw-normal text-muted">— ${exp.company_name || 'Company'}</span></strong>
              <span class="small text-muted">${dates}</span>
            </div>
            ${exp.responsibilities ? `<div class="small text-dark mt-1">${exp.responsibilities.replace(/\n/g, '<br>')}</div>` : ''}
            ${exp.achievements ? `<div class="small text-muted mt-1 fst-italic">Key Achievement: ${exp.achievements.replace(/\n/g, '<br>')}</div>` : ''}
          </div>
        `;
      }
    });
    html += `</div>`;
  }

  // Education
  if (resumeData.education && resumeData.education.length > 0) {
    html += `
      <div class="mb-3">
        <h6 class="fw-bold text-uppercase pb-1 mb-2 border-bottom" style="color: ${accent};">Education</h6>
    `;
    resumeData.education.forEach(edu => {
      if (edu.institution_name || edu.degree) {
        const dates = `${edu.start_year || ''} – ${edu.graduation_year || ''}`;
        html += `
          <div class="mb-2 d-flex justify-content-between align-items-baseline">
            <div>
              <strong class="text-dark small">${edu.degree || 'Degree'}${edu.field_of_study ? ` in ${edu.field_of_study}` : ''}</strong>
              <div class="small text-muted">${edu.institution_name || 'Institution'}${edu.grade ? ` | CGPA: ${edu.grade}` : ''}</div>
            </div>
            <span class="small text-muted">${dates}</span>
          </div>
        `;
      }
    });
    html += `</div>`;
  }

  // Skills
  if (resumeData.skills && resumeData.skills.length > 0) {
    html += `
      <div class="mb-3">
        <h6 class="fw-bold text-uppercase pb-1 mb-2 border-bottom" style="color: ${accent};">Skills & Competencies</h6>
        <div class="d-flex flex-wrap gap-1">
    `;
    resumeData.skills.forEach(s => {
      html += `<span class="badge bg-light text-dark border small">${s.name}</span>`;
    });
    html += `</div></div>`;
  }

  // Projects
  if (resumeData.projects && resumeData.projects.length > 0) {
    html += `
      <div class="mb-3">
        <h6 class="fw-bold text-uppercase pb-1 mb-2 border-bottom" style="color: ${accent};">Key Projects</h6>
    `;
    resumeData.projects.forEach(proj => {
      if (proj.project_name) {
        html += `
          <div class="mb-2">
            <div class="d-flex justify-content-between align-items-baseline">
              <strong class="text-dark small">${proj.project_name}</strong>
              ${proj.project_url ? `<span class="small" style="color: ${accent};">${proj.project_url}</span>` : ''}
            </div>
            ${proj.technologies ? `<div class="small text-muted">Technologies: ${proj.technologies}</div>` : ''}
            ${proj.description ? `<div class="small text-dark">${proj.description}</div>` : ''}
          </div>
        `;
      }
    });
    html += `</div>`;
  }

  // Certifications & Languages
  if ((resumeData.certifications && resumeData.certifications.length > 0) || (resumeData.languages && resumeData.languages.length > 0)) {
    html += `<div class="row g-3">`;
    if (resumeData.certifications.length > 0) {
      html += `
        <div class="col-md-6">
          <h6 class="fw-bold text-uppercase pb-1 mb-2 border-bottom" style="color: ${accent};">Certifications</h6>
      `;
      resumeData.certifications.forEach(c => {
        if (c.certification_name) {
          html += `<div class="small text-dark mb-1">• <strong>${c.certification_name}</strong> (${c.issuing_org || 'Issuer'})</div>`;
        }
      });
      html += `</div>`;
    }
    if (resumeData.languages.length > 0) {
      html += `
        <div class="col-md-6">
          <h6 class="fw-bold text-uppercase pb-1 mb-2 border-bottom" style="color: ${accent};">Languages</h6>
      `;
      resumeData.languages.forEach(l => {
        if (l.language_name) {
          html += `<div class="small text-dark mb-1">• <strong>${l.language_name}</strong>: ${l.proficiency_level || 'Proficient'}</div>`;
        }
      });
      html += `</div>`;
    }
    html += `</div>`;
  }

  preview.innerHTML = html;
}

// Save Full Resume to Server via JSON API
async function saveResumeToServer(silent = false) {
  saveCurrentState();
  const saveBtn = document.getElementById('btn-save-resume');
  if (saveBtn) {
    saveBtn.innerHTML = '<i class="fa-solid fa-spinner ai-spin me-1"></i> Saving...';
    saveBtn.disabled = true;
  }

  try {
    const res = await fetch(`/resume/save/${resumeData.id}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(resumeData)
    });
    const result = await res.json();
    if (result.success) {
      if (!silent) {
        showToast("Resume saved successfully!", "success");
      }
    } else {
      if (!silent) {
        showToast(result.message || "Could not save resume", "danger");
      }
    }
  } catch (err) {
    console.error(err);
    if (!silent) showToast("Network error saving resume", "danger");
  } finally {
    if (saveBtn) {
      saveBtn.innerHTML = '<i class="fa-solid fa-floppy-disk me-1"></i> Save Changes';
      saveBtn.disabled = false;
    }
  }
}

// ----------------- AI Assistant Functions -----------------

// 1. Generate Summary with AI
async function aiGenerateSummary() {
  saveCurrentState();
  const btn = document.getElementById('btn-ai-summary');
  if (btn) {
    btn.innerHTML = '<i class="fa-solid fa-spinner ai-spin me-1"></i> AI Generating...';
    btn.disabled = true;
  }

  try {
    const p = resumeData.personal_info;
    const skillsList = resumeData.skills.map(s => s.name).join(', ');
    const res = await fetch('/api/ai/generate-summary', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        full_name: p.full_name,
        title: p.professional_title,
        target_role: resumeData.target_role,
        skills: skillsList,
        existing_summary: p.summary
      })
    });
    const result = await res.json();
    if (result.success) {
      const summaryBox = document.getElementById('pi-summary');
      if (summaryBox) {
        summaryBox.value = result.content;
        p.summary = result.content;
      }
      renderLivePreview();
      showToast(result.is_demo ? "Summary generated in Demo Mode" : "Summary generated by AI!", "info");
    } else {
      showToast(result.content || "AI generation failed", "danger");
    }
  } catch (e) {
    console.error(e);
    showToast("Error communicating with AI assistant", "danger");
  } finally {
    if (btn) {
      btn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles me-1"></i> Generate with AI';
      btn.disabled = false;
    }
  }
}

// 2. Improve Bullet Points with AI
async function aiImproveExp(idx) {
  const exp = resumeData.work_experience[idx];
  if (!exp) return;

  const textToImprove = exp.responsibilities || exp.achievements;
  if (!textToImprove || !textToImprove.trim()) {
    showToast("Please enter some responsibilities or achievements first to improve.", "warning");
    return;
  }

  try {
    const res = await fetch('/api/ai/improve-text', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: textToImprove,
        context_type: `${exp.job_title} at ${exp.company_name}`
      })
    });
    const result = await res.json();
    if (result.success) {
      exp.responsibilities = result.content;
      renderWorkExpList();
      renderLivePreview();
      showToast("Experience bullet points improved with action verbs!", "success");
    }
  } catch (err) {
    console.error(err);
    showToast("Failed to improve text with AI", "danger");
  }
}

// 3. AI Skills Suggestions
async function aiSuggestSkills() {
  const role = resumeData.target_role || (resumeData.personal_info && resumeData.personal_info.professional_title);
  if (!role) {
    showToast("Please specify a target role or title first.", "warning");
    return;
  }

  const btn = document.getElementById('btn-ai-skills');
  if (btn) {
    btn.innerHTML = '<i class="fa-solid fa-spinner ai-spin me-1"></i> Suggesting...';
    btn.disabled = true;
  }

  try {
    const current = resumeData.skills.map(s => s.name).join(', ');
    const res = await fetch('/api/ai/suggest-skills', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ role: role, current_skills: current })
    });
    const result = await res.json();
    if (result.success) {
      let suggestions = [];
      try {
        const parsed = typeof result.content === 'string' ? JSON.parse(result.content) : result.content;
        suggestions = [...(parsed.technical || []), ...(parsed.soft || []), ...(parsed.tools || [])];
      } catch (err) {
        // Fallback split by lines or commas
        suggestions = result.content.split(/[,\n]/).map(s => s.replace(/[•\-\*]/g, '').trim()).filter(Boolean);
      }

      // Add unique suggestions
      const existing = new Set(resumeData.skills.map(s => s.name.toLowerCase()));
      let added = 0;
      suggestions.forEach(item => {
        if (!existing.has(item.toLowerCase()) && added < 8) {
          resumeData.skills.push({ name: item, category: 'technical' });
          existing.add(item.toLowerCase());
          added++;
        }
      });

      renderSkillsList();
      renderLivePreview();
      showToast(`Added ${added} suggested skills for ${role}!`, "success");
    }
  } catch (err) {
    console.error(err);
    showToast("Could not load AI skills", "danger");
  } finally {
    if (btn) {
      btn.innerHTML = '<i class="fa-solid fa-lightbulb me-1"></i> AI Skills Suggestions';
      btn.disabled = false;
    }
  }
}

// 4. AI Resume Review Modal
async function aiReviewResume() {
  saveCurrentState();
  const modalEl = document.getElementById('aiReviewModal');
  const contentEl = document.getElementById('ai-review-content');
  if (!modalEl || !contentEl) return;

  const bsModal = new bootstrap.Modal(modalEl);
  contentEl.innerHTML = '<div class="text-center py-4"><i class="fa-solid fa-spinner fa-2x ai-spin text-primary"></i><p class="mt-2 text-muted small">Senior AI Recruiter analyzing your resume metrics and structure...</p></div>';
  bsModal.show();

  try {
    const res = await fetch('/api/ai/review-resume', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resume_data: resumeData })
    });
    const result = await res.json();
    if (result.success) {
      contentEl.innerHTML = `<div class="p-2" style="white-space: pre-wrap; line-height: 1.6;">${result.content}</div>`;
    } else {
      contentEl.innerHTML = `<div class="alert alert-danger">${result.content || 'Failed to review resume'}</div>`;
    }
  } catch (err) {
    console.error(err);
    contentEl.innerHTML = '<div class="alert alert-danger">Error retrieving AI review.</div>';
  }
}

// Helper: Notification toast
function showToast(message, type = 'info') {
  const toastContainer = document.createElement('div');
  toastContainer.className = `alert alert-${type} alert-dismissible fade show position-fixed bottom-0 end-0 m-3 shadow-lg card-saas`;
  toastContainer.style.zIndex = '1090';
  toastContainer.innerHTML = `
    <div class="d-flex align-items-center gap-2">
      <i class="fa-solid fa-circle-info"></i>
      <div>${message}</div>
    </div>
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  `;
  document.body.appendChild(toastContainer);
  setTimeout(() => {
    toastContainer.remove();
  }, 4000);
}
