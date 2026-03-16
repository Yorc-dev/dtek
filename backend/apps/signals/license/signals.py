from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.license_template.models import License
from apps.license_template.utils import save_license_docx  


@receiver(post_save, sender=License)
def generate_license_doc(sender, instance: License, created, **kwargs):
    """
    После создания лицензии автоматически генерируем и сохраняем docx.
    Если документ уже есть — не перезаписываем.
    """
    if created and not instance.document:
        try:
            save_license_docx(instance, instance.application)
        except Exception as e:
            # Можно заменить на нормальный логгер
            print(f"Ошибка генерации docx для лицензии {instance.pk}: {e}")
