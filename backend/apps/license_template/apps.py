from django.apps import AppConfig


class LicenceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.license_template"
    verbose_name = 'Лицензии'

    def ready(self):
        import apps.signals.license.signals