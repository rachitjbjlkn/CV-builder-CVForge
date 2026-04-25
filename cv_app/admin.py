from django.contrib import admin
from django.contrib.auth.models import User
from .models import CVProfile, ATSScore, UserProfile

class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'date_joined', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_filter = ['is_staff', 'is_superuser', 'date_joined', 'is_active']
    ordering = ['-date_joined']
    readonly_fields = ['date_joined', 'last_login']
    fieldsets = (
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

class CVProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'template', 'created_at', 'user', 'get_ats_count']
    list_filter = ['template', 'created_at', 'user__is_active']
    search_fields = ['full_name', 'email', 'phone', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'experience_json', 'education_json', 'skills_json', 'projects_json', 'certifications_json', 'languages_json', 'achievements_json']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    show_full_result_count = True
    
    fieldsets = (
        ('Personal Info', {
            'fields': ('user', 'full_name', 'email', 'phone', 'location')
        }),
        ('Professional', {
            'fields': ('professional_summary', 'linkedin', 'github', 'portfolio')
        }),
        ('Content', {
            'fields': ('experience_json', 'education_json', 'skills_json', 'projects_json', 'certifications_json', 'languages_json', 'achievements_json')
        }),
        ('Settings', {
            'fields': ('template', 'created_at', 'updated_at')
        }),
    )
    
    def get_ats_count(self, obj):
        return obj.ats_scores.count()
    get_ats_count.short_description = 'ATS Checks'

admin.site.register(CVProfile, CVProfileAdmin)

class ATSScoreAdmin(admin.ModelAdmin):
    list_display = ['cv', 'overall_score', 'keyword_score', 'formatting_score', 'created_at']
    list_filter = ['created_at', 'overall_score']
    search_fields = ['cv__full_name', 'cv__email']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    def get_keyword_score(self, obj):
        return f"{obj.keyword_score}%"
    get_keyword_score.short_description = 'Keyword Score'
    
    def get_formatting_score(self, obj):
        return f"{obj.formatting_score}%"
    get_formatting_score.short_description = 'Format Score'

admin.site.register(ATSScore, ATSScoreAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_email', 'plan', 'cv_count', 'daily_ats_checks', 'last_ats_check_date', 'is_active']
    list_filter = ['plan', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name']
    readonly_fields = ['created_at', 'daily_ats_checks', 'last_ats_check_date']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Plan & Limits', {'fields': ('plan', 'cv_limit', 'cv_count')}),
        ('ATS Limits', {'fields': ('daily_ats_checks', 'last_ats_check_date')}),
        ('Dates', {'fields': ('created_at',)}),
    )
    
    def user_email(self, obj):
        return obj.user.email if obj.user else '-'
    user_email.short_description = 'Email'
    
    def is_active(self, obj):
        return obj.user.is_active
    is_active.boolean = True
    is_active.short_description = 'Active'

admin.site.site_header = "CVForge Admin"
admin.site.site_title = "CVForge"
admin.site.index_title = "Dashboard"