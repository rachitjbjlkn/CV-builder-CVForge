from django.apps import AppConfig
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

class CvAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cv_app'
    verbose_name = "CV Builder"

    def ready(self):
        from . import signals
