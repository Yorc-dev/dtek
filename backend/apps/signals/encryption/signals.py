from django.db.models.signals import pre_save, post_init
from django.dispatch import receiver

from encryption.aes_cipher import AESCipher

cipher = AESCipher()

# signal
@receiver(pre_save)
def encrypt_data(sender, instance, **kwargs):
    if hasattr(sender, 'encrypted_fields'):
        for field in sender.encrypted_fields:
            value = getattr(instance, field, None)
            if value:
                setattr(instance, field, cipher.encrypt_value(value))

@receiver(post_init)
def decrypt_data(sender, instance, **kwargs):
    if hasattr(instance, 'encrypted_fields'):
        for field in sender.encrypted_fields:
            value = getattr(instance, field, None)
            if value:
                setattr(instance, field, cipher.decrypt_value(value))
