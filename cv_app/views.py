from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import CVProfile, ATSScore, UserProfile
import json
import re
import urllib.request
import urllib.parse
import urllib.error
import io

def parse_cv_file(file):
    """Parse PDF, DOCX, or TXT file and return text content."""
    text = ""
    file_name = file.name.lower()
    file.seek(0)
    
    if file_name.endswith('.pdf'):
        try:
            from pypdf import PdfReader
            reader = PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        except Exception as e:
            print(f"PDF parse error: {e}")
            raise ValueError(f"Could not read PDF: {str(e)}")
    
    elif file_name.endswith('.docx'):
        try:
            from docx import Document
            doc = Document(file)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            print(f"DOCX parse error: {e}")
            raise ValueError(f"Could not read DOCX: {str(e)}")
    
    elif file_name.endswith('.txt'):
        text = file.read().decode('utf-8', errors='ignore')
    
    else:
        raise ValueError("Unsupported file type. Use PDF, DOCX, or TXT")
    
    return text

# ─── HOME ────────────────────────────────────────────────────────────────────

@login_required
def home(request):
    # Show only the logged-in user's CVs
    cvs = CVProfile.objects.filter(user=request.user).order_by('-updated_at')[:12]
    
    # Get user's first name or username
    user_name = request.user.first_name if request.user.first_name else request.user.username
    
    features = [
        {'icon': '✏️', 'name': 'CV Builder', 'desc': 'Create CVs with 8 ATS-optimized templates'},
        {'icon': '🎯', 'name': 'ATS Checker', 'desc': 'Analyze CV against any job description'},
        {'icon': '📄', 'name': 'External Files', 'desc': 'Upload PDF, DOCX & analyze any resume'},
        {'icon': '👁', 'name': 'Live Preview', 'desc': 'Preview before downloading'},
        {'icon': '🖨️', 'name': 'Print/PDF', 'desc': 'Export to PDF or print'},
        {'icon': '⚡', 'name': 'AI Summary', 'desc': 'Auto-generate professional summaries'},
    ]
    
    return render(request, 'cv_app/home.html', {
        'cvs': cvs, 
        'features': features,
        'user_name': user_name
    })


# ─── AUTH ─────────────────────────────────────────────────────────────────

def auth_view(request):
    return render(request, 'cv_app/auth.html')


def signup(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            
            if not username or not email or not password:
                return JsonResponse({'error': 'All fields are required'}, status=400)
            
            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists'}, status=400)
            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email already exists'}, status=400)
            
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            return JsonResponse({'status': 'ok', 'redirect': '/'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=400)


def signin(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return JsonResponse({'status': 'ok', 'redirect': '/'})
        return JsonResponse({'error': 'Invalid credentials'}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=400)


def signout(request):
    logout(request)
    return redirect('home')


# ─── UPGRADE ─────────────────────────────────────────────────────

@login_required
def upgrade(request):
    profile = request.user.profile
    profile.plan = 'pro'
    profile.save()
    return JsonResponse({'status': 'ok', 'plan': profile.plan})


# ─── CV BUILDER ──────────────────────────────────────────────────────────────

@login_required
def cv_builder(request, pk=None):
    cv = None
    if pk:
        cv = get_object_or_404(CVProfile, pk=pk, user=request.user)

    templates = [
        {'id': 'modern',    'name': 'Modern Minimal',   'icon': '⚡', 'desc': 'Clean, ATS-friendly format'},
        {'id': 'atspro',    'name': 'ATS Pro',        'icon': '🎯', 'desc': 'Optimized for ATS systems'},
        {'id': 'clean',     'name': 'Clean Simple',   'icon': '✨', 'desc': 'Simple, readable format'},
        {'id': 'executive', 'name': 'Executive Pro',    'icon': '💼', 'desc': 'Corporate, authoritative'},
        {'id': 'tech',     'name': 'Tech Developer',   'icon': '💻', 'desc': 'Code-inspired design'},
        {'id': 'creative', 'name': 'Creative Vivid',  'icon': '🎨', 'desc': 'Colorful, eye-catching'},
        {'id': 'elegant',  'name': 'Elegant Classic', 'icon': '📜', 'desc': 'Timeless, sophisticated'},
        {'id': 'bold',     'name': 'Bold Impact',   'icon': '🔥', 'desc': 'High contrast design'},
    ]
    cv_data = {
        'pk': cv.pk if cv else None,
        'full_name': cv.full_name if cv else 'Rachit',
        'email': cv.email if cv else '',
        'phone': cv.phone if cv else '',
        'location': cv.location if cv else '',
        'linkedin': cv.linkedin if cv else '',
        'github': cv.github if cv else '',
        'website': cv.website if cv else '',
        'professional_summary': cv.professional_summary if cv else '',
        'template': cv.template if cv else 'modern',
        'experience_json': cv.experience_json if cv else '[]',
        'education_json': cv.education_json if cv else '[]',
        'skills_json': cv.skills_json if cv else '[]',
        'projects_json': cv.projects_json if cv else '[]',
        'achievements_json': cv.achievements_json if cv else '[]',
        'certifications_json': cv.certifications_json if cv else '[]',
        'languages_json': cv.languages_json if cv else '[]',
    }
    quick_skills = [
        'Python', 'JavaScript', 'TypeScript', 'React', 'Next.js', 'Vue.js',
        'Node.js', 'Django', 'Flask', 'FastAPI', 'SQL', 'PostgreSQL',
        'MongoDB', 'Git', 'Docker', 'Kubernetes', 'AWS', 'GCP', 'Azure',
        'Machine Learning', 'TensorFlow', 'PyTorch', 'NLP', 'REST APIs',
        'GraphQL', 'HTML/CSS', 'Tailwind', 'Figma', 'CI/CD', 'Jira'
    ]
    return render(request, 'cv_app/builder.html', {'cv': cv, 'cv_data': cv_data, 'templates': templates, 'quick_skills': quick_skills})


@csrf_exempt
def save_cv(request, pk=None):
    print("SAVE CALLED, method:", request.method)
    print("Body:", request.body[:200] if request.body else "empty")
    
    if request.method == 'POST':
        try:
            body_str = request.body.decode('utf-8')
            print("Body str:", body_str[:100])
            data = json.loads(body_str)
        except Exception as e:
            print("JSON error:", e)
            return JsonResponse({'error': f'Invalid JSON: {e}'}, status=400)

        try:
            if pk:
                cv = get_object_or_404(CVProfile, pk=pk, user=request.user)
            else:
                cv = CVProfile()

            cv.full_name = data.get('full_name', 'Rachit')
            cv.email = data.get('email', '')
            cv.phone = data.get('phone', '')
            cv.location = data.get('location', '')
            cv.linkedin = data.get('linkedin', '')
            cv.github = data.get('github', '')
            cv.website = data.get('website', '')
            cv.professional_summary = data.get('professional_summary', '')
            cv.template = data.get('template', 'modern')
            cv.experience_json = json.dumps(data.get('experience', []))
            cv.education_json = json.dumps(data.get('education', []))
            cv.skills_json = json.dumps(data.get('skills', []))
            cv.projects_json = json.dumps(data.get('projects', []))
            cv.certifications_json = json.dumps(data.get('certifications', []))
            cv.languages_json = json.dumps(data.get('languages', []))
            cv.achievements_json = json.dumps(data.get('achievements', []))

            if request.user.is_authenticated:
                cv.user = request.user
            
            # Get or create user profile
            if request.user.is_authenticated:
                profile, _ = UserProfile.objects.get_or_create(user=request.user)
                profile.increment_cv()
            
            cv.save()
            print(f"Saved CV: {cv.pk}")
            return JsonResponse({'status': 'ok', 'id': cv.pk, 'redirect': f'/preview/{cv.pk}/'})
        except Exception as e:
            print(f"Save error: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Use POST method'}, status=405)


@login_required
def cv_preview(request, pk):
    cv = get_object_or_404(CVProfile, pk=pk, user=request.user)
    ats_scores = cv.ats_scores.order_by('-created_at')[:5]
    return render(request, 'cv_app/preview.html', {'cv': cv, 'ats_scores': ats_scores})


@login_required
def delete_cv(request, pk):
    cv = get_object_or_404(CVProfile, pk=pk, user=request.user)
    cv.delete()
    return redirect('home')


# ─── ATS CHECKER ─────────────────────────────────────────────────────────────

@login_required
def ats_checker(request, pk=None):
    cv = None
    if pk:
        cv = get_object_or_404(CVProfile, pk=pk, user=request.user)
    all_cvs = CVProfile.objects.filter(user=request.user).order_by('-updated_at')
    return render(request, 'cv_app/ats.html', {'cv': cv, 'all_cvs': all_cvs})


@csrf_exempt
def analyze_ats(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    data = json.loads(request.body)
    cv_id = data.get('cv_id')
    job_description = data.get('job_description', '')

    if not cv_id or not job_description:
        return JsonResponse({'error': 'CV and job description required'}, status=400)

    cv = get_object_or_404(CVProfile, pk=cv_id)

    # Build CV text for analysis
    cv_text = build_cv_text(cv)

    # Try Groq API first (free), fallback to local algorithm
    result = None
    if settings.GROQ_API_KEY:
        result = analyze_with_groq(cv_text, job_description)

    if not result:
        result = analyze_locally(cv_text, job_description, cv)

    # Save to DB
    ats = ATSScore(
        cv_profile=cv,
        job_description=job_description,
        overall_score=result['overall_score'],
        keyword_score=result['keyword_score'],
        format_score=result['format_score'],
        content_score=result['content_score'],
        skills_match_score=result['skills_match_score'],
        matched_keywords=json.dumps(result['matched_keywords']),
        missing_keywords=json.dumps(result['missing_keywords']),
        suggestions=json.dumps(result['suggestions']),
        detailed_analysis=result.get('detailed_analysis', ''),
    )
    ats.save()

    return JsonResponse({**result, 'ats_id': ats.pk})


def build_cv_text(cv):
    parts = [
        cv.full_name, cv.email, cv.phone, cv.location,
        cv.professional_summary or '',
    ]
    for exp in cv.experience:
        parts.append(f"{exp.get('title','')} at {exp.get('company','')} {exp.get('description','')}")
    for edu in cv.education:
        parts.append(f"{edu.get('degree','')} {edu.get('field','')} {edu.get('institution','')}")
    for skill in cv.skills:
        parts.append(skill.get('name', skill) if isinstance(skill, dict) else str(skill))
    for proj in cv.projects:
        parts.append(f"{proj.get('name','')} {proj.get('description','')} {proj.get('technologies','')}")
    for cert in cv.certifications:
        parts.append(str(cert.get('name', cert)))
    for ach in cv.achievements:
        parts.append(str(ach.get('title', ach)))
    return ' '.join(parts)


def analyze_with_groq(cv_text, job_description):
    """Use Groq's free LLaMA API for intelligent ATS analysis."""
    prompt = f"""Analyze this CV against the job description and return ONLY valid JSON.

CV:
{cv_text[:2000]}

Job Description:
{job_description[:1500]}

Return this exact JSON structure:
{{
  "overall_score": <0-100>,
  "keyword_score": <0-100>,
  "format_score": <0-100>,
  "content_score": <0-100>,
  "skills_match_score": <0-100>,
  "matched_keywords": ["keyword1", "keyword2", ...],
  "missing_keywords": ["keyword1", "keyword2", ...],
  "suggestions": ["suggestion1", "suggestion2", "suggestion3", ...],
  "detailed_analysis": "2-3 sentence professional analysis"
}}"""

    try:
        payload = json.dumps({
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 800,
            "temperature": 0.2,
        }).encode()

        req = urllib.request.Request(
            settings.GROQ_API_URL,
            data=payload,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {settings.GROQ_API_KEY}',
            }
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            text = result['choices'][0]['message']['content']
            # Extract JSON from response
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group())
    except Exception as e:
        print(f"Groq API error: {e}")
    return None


def analyze_locally(cv_text, job_description, cv):
    """Smart local ATS analysis algorithm."""
    cv_lower = cv_text.lower()
    jd_lower = job_description.lower()

    # Extract keywords from JD
    stop_words = {'the','a','an','and','or','but','in','on','at','to','for','of','with',
                  'is','are','be','was','were','will','have','has','can','should','must',
                  'this','that','these','those','we','you','our','your','their','about'}

    jd_words = re.findall(r'\b[a-zA-Z][a-zA-Z+#\.]{2,}\b', job_description)
    keywords = {}
    for w in jd_words:
        w_lower = w.lower()
        if w_lower not in stop_words and len(w_lower) > 2:
            keywords[w_lower] = keywords.get(w_lower, 0) + 1

    # Sort by frequency, take top keywords
    sorted_kw = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
    top_keywords = [k for k, v in sorted_kw[:40] if v >= 1]

    matched = [kw for kw in top_keywords if kw in cv_lower]
    missing = [kw for kw in top_keywords if kw not in cv_lower]

    # Score calculations
    keyword_score = min(100, int((len(matched) / max(len(top_keywords), 1)) * 100))

    # Format score (check for key sections)
    sections = ['experience', 'education', 'skills', 'summary', 'contact']
    format_hits = sum(1 for s in sections if s in cv_lower)
    format_score = min(100, format_hits * 20)

    # Add bonus for having profile photo, multiple experiences, etc.
    if len(cv.experience) >= 2: format_score = min(100, format_score + 10)
    if cv.professional_summary: format_score = min(100, format_score + 10)

    # Content score (length & richness)
    word_count = len(cv_text.split())
    content_score = min(100, max(40, word_count // 5))

    # Skills match
    skills_in_cv = [s.get('name','').lower() if isinstance(s, dict) else s.lower() for s in cv.skills]
    skill_hits = sum(1 for s in skills_in_cv if any(kw in s or s in kw for kw in top_keywords[:20]))
    skills_match_score = min(100, max(30, skill_hits * 15))

    overall_score = int(keyword_score * 0.35 + format_score * 0.20 +
                        content_score * 0.20 + skills_match_score * 0.25)

    # Generate smart suggestions
    suggestions = []
    if keyword_score < 70:
        suggestions.append(f"Add these missing keywords to your CV: {', '.join(missing[:5])}")
    if not cv.professional_summary:
        suggestions.append("Add a strong professional summary mentioning key skills from the JD")
    if len(cv.experience) == 0:
        suggestions.append("Add your work experience with quantifiable achievements")
    if len(cv.skills) < 8:
        suggestions.append("Expand your skills section with technical and soft skills")
    if not cv.linkedin:
        suggestions.append("Add your LinkedIn profile URL to increase credibility")
    if len(cv.projects) == 0:
        suggestions.append("Add relevant projects to demonstrate hands-on experience")
    if content_score < 60:
        suggestions.append("Add more detailed descriptions to your experience entries")
    suggestions.append("Use action verbs like 'Led', 'Built', 'Achieved', 'Improved' in your descriptions")
    suggestions.append("Quantify achievements with numbers, percentages, and metrics")

    detail = (f"Your CV matches {len(matched)} of {len(top_keywords)} key terms from the job description. "
              f"The overall ATS compatibility score is {overall_score}%. "
              f"Focus on incorporating missing keywords naturally into your experience descriptions.")

    return {
        'overall_score': overall_score,
        'keyword_score': keyword_score,
        'format_score': format_score,
        'content_score': content_score,
        'skills_match_score': skills_match_score,
        'matched_keywords': matched[:20],
        'missing_keywords': missing[:15],
        'suggestions': suggestions[:8],
        'detailed_analysis': detail,
    }


# ─── CV PRINT/EXPORT ─────────────────────────────────────────────────────────

def cv_print_demo(request):
    """Demo CV preview for template showcase."""
    template = request.GET.get('template', 'modern')
    
    demo_cv = type('obj', (object,), {
        'full_name': 'Alex Johnson',
        'email': 'alex.johnson@email.com',
        'phone': '+1 555-123-4567',
        'location': 'San Francisco, CA',
        'linkedin': 'linkedin.com/in/alexjohnson',
        'github': 'github.com/alexjohnson',
        'website': 'alexjohnson.dev',
        'professional_summary': 'Full-stack developer with 5+ years of experience building scalable web applications. Passionate about clean code, performance optimization, and user experience.',
        'template': template,
        'experience': [
            {'title': 'Senior Software Engineer', 'company': 'TechCorp Inc.', 'location': 'San Francisco, CA', 'start': '2021-01', 'end': '', 'current': True, 'description': '• Led development of microservices architecture\n• Improved system performance by 40%\n• Mentored junior developers'},
            {'title': 'Software Developer', 'company': 'StartupXYZ', 'location': 'Remote', 'start': '2019-03', 'end': '2020-12', 'current': False, 'description': '• Built RESTful APIs\n• Implemented authentication system'}
        ],
        'education': [
            {'degree': 'B.Tech', 'field': 'Computer Science', 'institution': 'MIT', 'location': 'Boston', 'start': '2015', 'end': '2019', 'grade': '9.2 CGPA'}
        ],
        'skills': [
            {'name': 'Python', 'level': 5}, {'name': 'JavaScript', 'level': 4}, {'name': 'React', 'level': 4},
            {'name': 'Django', 'level': 5}, {'name': 'Node.js', 'level': 3}, {'name': 'SQL', 'level': 4}
        ],
        'projects': [
            {'name': 'E-commerce Platform', 'description': 'Full-stack shopping platform', 'technologies': 'React, Node.js, MongoDB'},
            {'name': 'Task Manager', 'description': 'Productivity app with real-time updates', 'technologies': 'Vue.js, Firebase'}
        ],
        'certifications': [
            {'name': 'AWS Solutions Architect', 'issuer': 'Amazon', 'date': '2023-06'}
        ],
        'languages': [
            {'name': 'English', 'proficiency': 'Native'}, {'name': 'Spanish', 'proficiency': 'Professional'}
        ],
        'achievements': [
            {'title': 'Best Employee Award', 'description': 'Recognized for outstanding performance', 'date': '2022'}
        ]
    })()
    
    response = render(request, 'cv_app/print.html', {'cv': demo_cv})
    response['X-Frame-Options'] = 'ALLOW'
    return response


def cv_print(request, pk):
    cv = get_object_or_404(CVProfile, pk=pk, user=request.user)
    response = render(request, 'cv_app/print.html', {'cv': cv})
    return response


# ─── EXTERNAL CV ATS CHECK ───────────────────────────────────────────────────

@csrf_exempt
def analyze_external_cv(request):
    """Analyze an uploaded external CV file against a job description."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        if 'cv_file' not in request.FILES:
            return JsonResponse({'error': 'No CV file uploaded'}, status=400)
        
        cv_file = request.FILES['cv_file']
        job_description = request.POST.get('job_description', '')
        
        if not job_description:
            return JsonResponse({'error': 'Job description required'}, status=400)
        
        # Parse the CV file
        cv_text = parse_cv_file(cv_file)
        
        if not cv_text.strip():
            return JsonResponse({'error': 'Could not extract text from file'}, status=400)
        
        # Analyze using local algorithm (works without CVProfile)
        result = analyze_external_ats(cv_text, job_description)
        
        return JsonResponse(result)
    
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        print(f"External CV analysis error: {e}")
        return JsonResponse({'error': 'Failed to analyze CV'}, status=500)


def analyze_external_ats(cv_text, job_description):
    """ATS analysis for external CV text (without CVProfile)."""
    cv_lower = cv_text.lower()
    jd_lower = job_description.lower()
    
    stop_words = {'the','a','an','and','or','but','in','on','at','to','for','of','with',
               'is','are','be','was','were','will','have','has','can','should','must',
               'this','that','these','those','we','you','our','your','their','about'}
    
    jd_words = re.findall(r'\b[a-zA-Z][a-zA-Z+#\.]{2,}\b', job_description)
    keywords = {}
    for w in jd_words:
        w_lower = w.lower()
        if w_lower not in stop_words and len(w_lower) > 2:
            keywords[w_lower] = keywords.get(w_lower, 0) + 1
    
    sorted_kw = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
    top_keywords = [k for k, v in sorted_kw[:40] if v >= 1]
    
    matched = [kw for kw in top_keywords if kw in cv_lower]
    missing = [kw for kw in top_keywords if kw not in cv_lower]
    
    keyword_score = min(100, int((len(matched) / max(len(top_keywords), 1)) * 100))
    
    sections = ['experience', 'education', 'skills', 'summary', 'contact']
    format_hits = sum(1 for s in sections if s in cv_lower)
    format_score = min(100, format_hits * 20)
    if 'summary' in cv_lower: format_score = min(100, format_score + 10)
    
    word_count = len(cv_text.split())
    content_score = min(100, max(40, word_count // 5))
    
    skills_match_score = min(100, max(30, len(matched) * 8))
    
    overall_score = int(keyword_score * 0.35 + format_score * 0.20 +
                        content_score * 0.20 + skills_match_score * 0.25)
    
    suggestions = []
    if keyword_score < 70:
        suggestions.append(f"Add these missing keywords: {', '.join(missing[:5])}")
    if 'summary' not in cv_lower:
        suggestions.append("Add a professional summary section")
    if content_score < 60:
        suggestions.append("Add more detailed descriptions to your experience")
    suggestions.append("Use action verbs like 'Led', 'Built', 'Achieved' in descriptions")
    suggestions.append("Quantify achievements with numbers and percentages")
    
    detail = (f"Your CV matches {len(matched)} of {len(top_keywords)} key terms. "
             f"ATS compatibility: {overall_score}%. "
             f"Incorporate missing keywords naturally.")
    
    return {
        'overall_score': overall_score,
        'keyword_score': keyword_score,
        'format_score': format_score,
        'content_score': content_score,
        'skills_match_score': skills_match_score,
        'matched_keywords': matched[:20],
        'missing_keywords': missing[:15],
        'suggestions': suggestions[:8],
        'detailed_analysis': detail,
    }