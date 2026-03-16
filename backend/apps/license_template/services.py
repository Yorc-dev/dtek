# from django.db import transaction
# from django.db import IntegrityError
# import pandas as pd
# from datetime import datetime, date

# from apps.organization.models import Organization
# from apps.application.models import Application
# from apps.application.choices import ApplicationType, ApplicationStatusType
# from apps.license_template.models import License, LicenseType



# def clean_str(val):
#     """
#     Приводит любое значение к безопасной строке
#     """
#     if val is None or pd.isna(val):
#         return None
#     return str(val).strip()


# def clean_int(val, default=0):
#     """
#     Приводит float/int/str к int
#     """
#     try:
#         return int(float(val))
#     except Exception:
#         return default


# def clean_bool(val):
#     """
#     Приводит 0 / 1 / '0' / '1' / float к bool
#     """
#     try:
#         return bool(int(float(val)))
#     except Exception:
#         return False


# def normalize_inn(val):
#     """
#     ИНН и подобные идентификаторы:
#     2708202510191.0 -> '2708202510191'
#     """
#     if val is None or pd.isna(val):
#         return None
#     return str(val).split('.')[0]


# def clean_date(val):
#     if val is None or pd.isna(val):
#         return None

#     if isinstance(val, (datetime, date)):
#         return val.date() if isinstance(val, datetime) else val

#     if isinstance(val, str):
#         val = val.strip()
#         if not val:
#             return None

#         parsed = pd.to_datetime(val, errors='coerce')
#         if pd.isna(parsed):
#             return None
#         return parsed.date()

#     return None

# def to_date_str(val):
#         if pd.isna(val):
#             return None
#         if hasattr(val, 'date'):
#             return val.date().isoformat()
#         if hasattr(val, 'isoformat'):
#             return val.isoformat()
#         return str(val)
            
            



# def get_or_create_organization_safe(row):
#     try:
#         organization, created = Organization.objects.get_or_create(
#                 name=clean_str(row.get('Название организации')),
#                 inn=normalize_inn(row.get('ИНН организации')),
#                 representative=normalize_inn(row.get('ИНН поручителя')))
#         return organization, created
#     except IntegrityError:
#         return Organization.objects.get(
#                 name=clean_str(row.get('Название организации')),
#                 inn=normalize_inn(row.get('ИНН организации')),
#                 representative=normalize_inn(row.get('ИНН поручителя'))
#                 ), False


# class OrganizationService:
#     @staticmethod
#     @transaction.atomic
#     def create_data(row):
#         organization, created = get_or_create_organization_safe(row)
#         return organization, created
    


# def get_or_create_application_safe(row, org):
#     try:
#         application, created = Application.objects.get_or_create(
#                 applicants_full_name=clean_str(row.get('ФИО заявителя')),
#                 applicants_status=clean_int(row.get('Статус заявителя')),
#                 organization=org,
#                 organization_name=clean_str(row.get('Название организации')),
#                 email=clean_str(row.get('Почта')),
#                 phone_number=clean_str(row.get('Номер телефона')),
#                 other_information=clean_str(row.get('Другие сведения')),
#                 ownership_form=clean_str(row.get('Форма собственности')),
#                 legal_address=clean_str(row.get('Юридический адрес')),
#                 actual_address=clean_str(row.get('Фактический адрес')),
#                 inn=normalize_inn(row.get('ИНН организации')),
#                 okpo_code=normalize_inn(row.get('Код ОКПО')),
#                 owner_full_name=clean_str(row.get('ФИО руководителя')),
#                 register_date=clean_date(row.get('Дата регистрации юр.лица')),
#                 application_type=clean_int(
#                     row.get('Тип заявки', ApplicationType.SUBMITTING)
#                 ),
#                 is_archived=True,
#                 status=ApplicationStatusType.APPROVED
#             )
#         return application, created
#     except IntegrityError:
#         return Application.objects.get(
#                 applicants_full_name=clean_str(row.get('ФИО заявителя')),
#                 applicants_status=clean_int(row.get('Статус заявителя')),
#                 organization=org,
#                 organization_name=clean_str(row.get('Название организации')),
#                 email=clean_str(row.get('Почта')),
#                 phone_number=clean_str(row.get('Номер телефона')),
#                 other_information=clean_str(row.get('Другие сведения')),
#                 ownership_form=clean_str(row.get('Форма собственности')),
#                 legal_address=clean_str(row.get('Юридический адрес')),
#                 actual_address=clean_str(row.get('Фактический адрес')),
#                 inn=normalize_inn(row.get('ИНН организации')),
#                 okpo_code=normalize_inn(row.get('Код ОКПО')),
#                 owner_full_name=clean_str(row.get('ФИО руководителя')),
#                 register_date=clean_date(row.get('Дата регистрации юр.лица')),
#                 application_type=clean_int(
#                     row.get('Тип заявки', ApplicationType.SUBMITTING)
#                 ),
#                 is_archived=True,
#                 status=ApplicationStatusType.APPROVED
#                 ), False


# class ApplicationService:
#     @staticmethod
#     @transaction.atomic
#     def create_data(row, org):
#         application, created = get_or_create_application_safe(row, org)
#         return application, created
    


# def get_or_create_license_safe(row, lt, expd, application):
#     try:
#         license, created = License.objects.get_or_create(
#                 registration_number=clean_str(
#                     row.get('Регистрационный номер по реестру лицензий')
#                 ),
#                 issued_date=clean_date(row.get('Дата выдачи')),
#                 issued_by=clean_str(row.get('Выдана')),
#                 licensee_address=clean_str(row.get('Адрес лицензиата')),
#                 state_registration_certificate=clean_str(
#                     row.get('Свидетельство о государственной регистрации')
#                 ),
#                 state_registration_issued_by=clean_str(
#                     row.get('Кем выдана государственная регистрация')
#                 ),
#                 inn=normalize_inn(row.get('ИНН организации')),
#                 license_type=lt,
#                 expiration_date=expd,
#                 expired=clean_bool(row.get('Анулировано')),
#                 registrable_type=clean_int(
#                     row.get('Лицензия является')
#                 ),
#                 application=application,
#                 volume=clean_str(row.get('Объем лицензии')),
#                 license_terms=clean_str(row.get('Лицензионные условия')),
#                 direct_aproved=True
#                 )
#         return license, created
#     except IntegrityError:
#         return License.objects.get(
#                 registration_number=clean_str(
#                     row.get('Регистрационный номер по реестру лицензий')
#                 ),
#                 issued_date=clean_date(row.get('Дата выдачи')),
#                 issued_by=clean_str(row.get('Выдана')),
#                 licensee_address=clean_str(row.get('Адрес лицензиата')),
#                 state_registration_certificate=clean_str(
#                     row.get('Свидетельство о государственной регистрации')
#                 ),
#                 state_registration_issued_by=clean_str(
#                     row.get('Кем выдана государственная регистрация')
#                 ),
#                 inn=normalize_inn(row.get('ИНН организации')),
#                 license_type=lt,
#                 expiration_date=expd,
#                 expired=clean_bool(row.get('Анулировано')),
#                 registrable_type=clean_int(
#                     row.get('Лицензия является')
#                 ),
#                 application=application,
#                 volume=clean_str(row.get('Объем лицензии')),
#                 license_terms=clean_str(row.get('Лицензионные условия')),
#                 direct_aproved=True
#                 ), False


# class LicenseService:
#     @staticmethod
#     @transaction.atomic
#     def create_data(row, lt, expd, application):
#         license, created = get_or_create_license_safe(row, lt, expd, application)
#         return license, created
    