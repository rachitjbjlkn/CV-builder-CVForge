from django.contrib import admin
from .models import CVProfile, ATSScore, UserProfile

@admin.register(CVProfile)
class CVProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'template', 'created_at']
    list_filter = ['template', 'created_at']
    search_fields = ['full_name', 'email']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ATSScore)
class ATSScoreAdmin(admin.ModelAdmin):
    list_display = ['cv_profile', 'overall_score', 'created_at']
    list_filter = ['created_at', 'overall_score']
    search_fields = ['cv_profile__full_name', 'cv_profile__email']
    readonly_fields = ['created_at']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'cv_count', 'created_at']
    list_filter = ['plan']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at']

admin.site.site_header = "CVForge Admin"
admin.site.site_title = "CVForge"
admin.site.index_title = "Dashboard"