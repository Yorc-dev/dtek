from django.apps import AppConfig, apps
from django.db.models.signals import post_migrate, pre_save, post_init, pre_delete

from apps.signals.core.register_signals import run_register_signals


class SignalCoreConfig(AppConfig):
    name = "signal"

    def ready(self):
        run_register_signals()
