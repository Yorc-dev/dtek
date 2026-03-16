from apps.account.send_email import send_reset_password_email
from apps.application.models import Application
from apps.integration.sedo import send_document, prepare_file_payload, build_document_payload
from apps.application.utils import render_application_to_docx
from django.conf import settings
# from apps.license_template.services import OrganizationService, ApplicationService, LicenseService
from apps.license_template.models import LicenseType
import pandas as pd
from django.db import transaction

from datetime import datetime, date

from apps.organization.models import Organization
from apps.application.models import Application
from apps.application.choices import ApplicationType, ApplicationStatusType
from apps.license_template.models import License, LicenseType


from celery import shared_task


from .celery import app

@app.task
def send_reset_password_email_task(email, reset_token):
    send_reset_password_email(email, reset_token)

@shared_task(bind=True, max_retries=5,  rate_limit='2/m')
def send_application_docx_task(self, app_id):
    app = Application.objects.get(id=app_id)

    try:
        file_path, encoded_doc = render_application_to_docx(app)

        app.doc.name = file_path.replace(settings.MEDIA_ROOT + '/', '')
        app.save(update_fields=["doc"])

        main_file = prepare_file_payload(encoded_doc, file_name="заявление.docx", signature="подпись")

        payload = build_document_payload(
            sender_inn=app.inn,
            receiver_inn=app.inn,
            doc_number="11-333",
            main_file=main_file
        )

        status_code = send_document(payload)

        if status_code == 200:
            app.send_status = 2
        else:
            app.send_status = 1
            raise Exception(f"Не удалось отправить: {status_code}")

        app.save(update_fields=["send_status"])

    except Exception as e:
        self.retry(exc=e, countdown=60)

# @shared_task
# def parsing_row(_, row):
#     def clean_str(val):
#         if val is None or pd.isna(val):
#             return None
#         return str(val).strip()
#     print(4)
#     # print(f"Processing row: {row.to_dict()}")
#     def to_date_str(val):
#         if val is None or pd.isna(val):
#             return None
#         if val == 'без ограничения действия':
#             return None
#         if hasattr(val, 'date'):
#             return val.date()
#         return val
#     try:
        
#          with transaction.atomic():

#             # 1️⃣ Organization
#             organization, _ = OrganizationService.create_data(row)

#             # 2️⃣ LicenseType (обязательно ДО application/license)
#             license_type = LicenseType.objects.filter(
#                 title__iexact=clean_str(row.get('Тип лицензии'))
#             ).first()

#             if not license_type:
#                 raise ValueError(
#                     f"LicenseType not found: '{clean_str(row.get('Тип лицензии'))}'"
#                 )

#             # 3️⃣ Application
#             application, created = ApplicationService.create_data(row, organization)

#             # 4️⃣ M2M: application ↔ license_type
#             if not application.license_type.filter(pk=license_type.pk).exists():
#                 application.license_type.add(license_type)

#             # 5️⃣ Expiration date
#             expiration_date = to_date_str(row.get('Срок действия лицензии'))

#             # 6️⃣ License (FK application уже гарантированно существует)
#             license_obj, license_created = LicenseService.create_data(
#                 row=row,
#                 lt=license_type,
#                 expd=expiration_date,
#                 application=application
#             )

#             if license_created:
#                 print(f"Created License: {license_obj.registration_number}")

#     except Exception as e:
#         print(f"Error processing row {row}: {e}")
        




@shared_task
def parsing_row(_, row):
    
    def clean_str(val):
        """
        Приводит любое значение к безопасной строке
        """
        if val is None or pd.isna(val):
            return None
        return str(val).strip()


    def clean_int(val, default=0):
        """
        Приводит float/int/str к int
        """
        try:
            return int(float(val))
        except Exception:
            return default


    def clean_bool(val):
        """
        Приводит 0 / 1 / '0' / '1' / float к bool
        """
        try:
            return bool(int(float(val)))
        except Exception:
            return False


    def normalize_inn(val):
        """
        ИНН и подобные идентификаторы:
        2708202510191.0 -> '2708202510191'
        """
        if val is None or pd.isna(val):
            return None
        return str(val).split('.')[0]


    def clean_date(val):
        if val is None or pd.isna(val) or val == 'без ограничения действия':
            return None

        if isinstance(val, (datetime, date)):
            return val.date() if isinstance(val, datetime) else val

        if isinstance(val, str):
            val = val.strip()
            if not val:
                return None

            parsed = pd.to_datetime(val, errors='coerce')
            if pd.isna(parsed):
                return None
            return parsed.date()

        return None

    def to_date_str(val):
            if pd.isna(val):
                return None
            if hasattr(val, 'date'):
                return val.date().isoformat()
            if hasattr(val, 'isoformat'):
                return val.isoformat()
            return str(val)
            

    try:
        with transaction.atomic():
            # -------------------------
            # Организация
            # -------------------------
            inn_org = normalize_inn(row.get('ИНН организации'))
            inn_rep = normalize_inn(row.get('ИНН поручителя'))
            try:
                print(f'Создание организации {_}')
                organization, _ = Organization.objects.get_or_create(
                    name=clean_str(row.get('Название организации')),
                    inn=inn_org,
                    representative=inn_rep
                )
            except Exception as e:  
                print(row)
                raise ValueError(
                    f"LicenseType not found: '{e}'"
                )

            # -------------------------
            # Тип лицензии
            # -------------------------
            print(f'Получение типа лицензии {_}')

            license_type = LicenseType.objects.get(
                title__iexact=clean_str(row.get('Тип лицензии'))
            )
            if not license_type:
                raise ValueError(
                    f"LicenseType not found: '{clean_str(row.get('Тип лицензии'))}'"
                )
            

            # -------------------------
            # Заявка
            # -------------------------
            print(f'Создание заявки {_}')

            application, created = Application.objects.get_or_create(
                applicants_full_name=clean_str(row.get('ФИО заявителя')),
                applicants_status=clean_int(row.get('Статус заявителя')),
                organization=organization,
                organization_name=clean_str(row.get('Название организации')),
                email=clean_str(row.get('Почта')),
                phone_number=clean_str(row.get('Номер телефона')),
                other_information=clean_str(row.get('Другие сведения')),
                ownership_form=clean_str(row.get('Форма собственности')),
                legal_address=clean_str(row.get('Юридический адрес')),
                actual_address=clean_str(row.get('Фактический адрес')),
                inn=inn_org,
                okpo_code=normalize_inn(row.get('Код ОКПО')),
                owner_full_name=clean_str(row.get('ФИО руководителя')),
                register_date=clean_date(row.get('Дата регистрации юр.лица')),
                application_type=clean_int(
                    row.get('Тип заявки', ApplicationType.SUBMITTING)
                ),
                is_archived=True,
                status=ApplicationStatusType.APPROVED
            )
            print(f'Успешно создалась заявка {_}')


            if created or not application.license_type.filter(
                pk=license_type.pk
            ).exists():
                application.license_type.add(license_type)

            # -------------------------
            # Лицензия
            # -------------------------
            expiration_date = clean_date(row.get('Срок действия лицензии'))
            print(f'Создание лицензии {_}')

            license_obj, license_created = License.objects.get_or_create(
                registration_number=clean_str(
                    row.get('Регистрационный номер по реестру лицензий')
                ),
                defaults={
                    'issued_date': clean_date(row.get('Дата выдачи')),
                    'issued_by': clean_str(row.get('Выдана')),
                    'licensee_address': clean_str(row.get('Адрес лицензиата')),
                    'state_registration_certificate': clean_str(
                        row.get('Свидетельство о государственной регистрации')
                    ),
                    'state_registration_issued_by': clean_str(
                        row.get('Кем выдана государственная регистрация')
                    ),
                    'inn': inn_org,
                    'license_type': license_type,
                    'expiration_date': expiration_date,
                    'expired': clean_bool(row.get('Анулировано')),
                    'registrable_type': clean_int(
                        row.get('Лицензия является')
                    ),
                    'application': application,
                    'volume': clean_str(row.get('Объем лицензии')),
                    'license_terms': clean_str(row.get('Лицензионные условия')),
                    'direct_aproved': True,
                }
            )

            if license_created:
                print(
                    f"Created License: {license_obj.registration_number}"
                )

    except Exception as e:
            print(
                f"Error processing row {_ + 1}: {e}"
            )
