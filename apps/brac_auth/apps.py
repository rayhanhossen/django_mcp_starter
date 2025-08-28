from django.apps import AppConfig


class BracAuthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "brac_auth"

    def ready(self):
        import brac_auth.signals


