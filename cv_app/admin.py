from django.contrib import admin
from .models import CVProfile, ATSScore

@admin.register(CVProfile)
class CVProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'template', 'created_at']
    list_filter = ['template']
    search_fields = ['full_name', 'email']

@admin.register(ATSScore)
class ATSScoreAdmin(admin.ModelAdmin):
    list_display = ['id', 'overall_score', 'created_at']
    list_filter = ['created_at']

admin.site.site_header = "CVForge Admin"
admin.site.site_title = "CVForge"
admin.site.index_title = "Dashboard"