from django.apps import apps
from django.db.models.signals import pre_save, pre_delete, post_init, post_save

from apps.signals.encryption.signals import encrypt_data, decrypt_data
from apps.signals.core.shared_pre_delete_m2m import shared_pre_delete

def register_signals():
    for model in apps.get_models():
        if getattr(model, 'track_with_signal', False):
            print(model)
            pre_delete.connect(shared_pre_delete, sender=model)
        pre_save.connect(encrypt_data, sender=model, weak=False)
        post_init.connect(decrypt_data, sender=model, weak=False)
        # post_save.connect(receiver=, sender=model, weak=False)

def run_register_signals(sender, **kwargs):
    register_signals()