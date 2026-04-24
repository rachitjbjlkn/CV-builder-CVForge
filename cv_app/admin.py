from django.contrib import admin
from django.contrib.auth.models import User
from .models import CVProfile, ATSScore, UserProfile

class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'date_joined', 'is_staff']
    search_fields = ['username', 'email']
    list_filter = ['is_staff', 'is_superuser', 'date_joined']

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

class CVProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'template', 'created_at', 'user']
    list_filter = ['template', 'created_at']
    search_fields = ['full_name', 'email']
    readonly_fields = ['created_at', 'updated_at']

admin.site.register(CVProfile, CVProfileAdmin)
admin.site.register(ATSScore)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_email', 'plan', 'cv_count', 'daily_ats_checks', 'last_ats_check_date', 'created_at']
    list_filter = ['plan']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at']
    
    def user_email(self, obj):
        return obj.user.email if obj.user else '-'
    user_email.short_description = 'Email'