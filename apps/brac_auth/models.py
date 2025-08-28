from django.db import models
from django.utils import timezone

# Create your models here.
class CustomPermittedSSOUsers(models.Model):
    sso_username = models.BigIntegerField(unique=True)
    override_project_permission = models.BooleanField(default=False)
    override_office_permission = models.BooleanField(default=False)
    domain_status = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)