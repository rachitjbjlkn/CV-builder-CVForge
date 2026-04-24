from django.db import models
from django.contrib.auth.models import User
import json
from datetime import date, timedelta

class UserProfile(models.Model):
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('pro', 'Pro'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    daily_ats_checks = models.IntegerField(default=0)
    last_ats_check_date = models.DateField(null=True, blank=True)
    cv_limit = models.IntegerField(default=5)
    cv_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def can_create_cv(self):
        if self.plan == 'pro':
            return True
        return self.cv_count < self.cv_limit
    
    def can_check_ats(self):
        today = date.today()
        if self.last_ats_check_date != today:
            self.daily_ats_checks = 0
            self.last_ats_check_date = today
            self.save()
        
        if self.plan == 'pro':
            return True
        return self.daily_ats_checks < 5
    
    def increment_ats_check(self):
        today = date.today()
        if self.last_ats_check_date != today:
            self.daily_ats_checks = 0
            self.last_ats_check_date = today
        self.daily_ats_checks += 1
        self.save()
    
    def increment_cv(self):
        self.cv_count += 1
        self.save()
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class CVProfile(models.Model):
    TEMPLATE_CHOICES = [
        ('modern', 'Modern Minimal'),
        ('atspro', 'ATS Pro'),
        ('clean', 'Clean Simple'),
        ('executive', 'Executive Pro'),
        ('tech', 'Tech Developer'),
        ('creative', 'Creative Vivid'),
        ('elegant', 'Elegant Classic'),
        ('bold', 'Bold Impact'),
    ]

    # User ownership
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='cvs')
    
    # Personal Info
    full_name = models.CharField(max_length=200, default='Rachit')
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    location = models.CharField(max_length=200)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    website = models.URLField(blank=True)
    profile_photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    professional_summary = models.TextField(blank=True)
    template = models.CharField(max_length=20, choices=TEMPLATE_CHOICES, default='modern')

    # JSON fields for dynamic sections
    experience_json = models.TextField(default='[]')
    education_json = models.TextField(default='[]')
    skills_json = models.TextField(default='[]')
    projects_json = models.TextField(default='[]')
    certifications_json = models.TextField(default='[]')
    languages_json = models.TextField(default='[]')
    achievements_json = models.TextField(default='[]')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def experience(self):
        return json.loads(self.experience_json or '[]')

    @property
    def education(self):
        return json.loads(self.education_json or '[]')

    @property
    def skills(self):
        return json.loads(self.skills_json or '[]')

    @property
    def projects(self):
        return json.loads(self.projects_json or '[]')

    @property
    def certifications(self):
        return json.loads(self.certifications_json or '[]')

    @property
    def languages(self):
        return json.loads(self.languages_json or '[]')

    @property
    def achievements(self):
        return json.loads(self.achievements_json or '[]')

    def __str__(self):
        return f"{self.full_name}'s CV"

    class Meta:
        verbose_name = "CV Profile"
        verbose_name_plural = "CV Profiles"


class ATSScore(models.Model):
    cv_profile = models.ForeignKey(CVProfile, on_delete=models.CASCADE, related_name='ats_scores')
    job_description = models.TextField()
    overall_score = models.IntegerField(default=0)
    keyword_score = models.IntegerField(default=0)
    format_score = models.IntegerField(default=0)
    content_score = models.IntegerField(default=0)
    skills_match_score = models.IntegerField(default=0)
    matched_keywords = models.TextField(default='[]')
    missing_keywords = models.TextField(default='[]')
    suggestions = models.TextField(default='[]')
    detailed_analysis = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def matched_kw_list(self):
        return json.loads(self.matched_keywords or '[]')

    @property
    def missing_kw_list(self):
        return json.loads(self.missing_keywords or '[]')

    @property
    def suggestions_list(self):
        return json.loads(self.suggestions or '[]')

    def __str__(self):
        return f"ATS Score {self.overall_score}% for {self.cv_profile.full_name}"

    class Meta:
        verbose_name = "ATS Score"
        verbose_name_plural = "ATS Scores"
        ordering = ['-created_at']
