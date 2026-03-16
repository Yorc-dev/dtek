from datetime import timedelta

from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.template.loader import render_to_string
from django.db.models.signals import m2m_changed

from core.tasks import send_application_docx_task


from apps.application.models import Application, ApplicationEmployee
from apps.integration.sedo import send_document, prepare_file_payload, build_document_payload
from apps.application.utils import render_application_to_docx

@receiver(post_save, sender=ApplicationEmployee)
def change_status_after_assignment(sender, instance, **kwargs):
    instance.application.status = 2
    instance.application.review_period = timezone.now() + timedelta(days=30)
    instance.application.save()



@receiver(m2m_changed, sender=Application.license_type.through)
def generate_docx_after_license_type(sender, instance, action, **kwargs):
    if action == "post_add":
        send_application_docx_task.delay(instance.id)




# @receiver(m2m_changed, sender=Application.license_type.through)
# def generate_docx_after_license_type(sender, instance, action, **kwargs):
#     if action == "post_add":
#         docs = render_application_to_docx(instance)
#         print(f"✅ DOCX создан для заявки {instance.id}")

#         main_file = prepare_file_payload(
#             docs=docs,
#             file_name="док-проверка",
#             signature="подпись_файла_в_ОЭЦП"
#         )
#         payload = build_document_payload(
#             sender_inn="00406200710110",
#             receiver_inn="00406200710110",
#             doc_number="11-333",
#             main_file=main_file,
#         )

        
#         # status_code = send_document(payload)
#         # if status_code == 200:
#         #     print('Документ успешно отправлен!')
#         #     instance.send_status=2
#         #     instance.save()
#         # else:

#         print('GOOOOOD')