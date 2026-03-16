# import pandas as pd

# from apps.organization.models import Organization
# from apps.application.models import Application
# from apps.application.choices import ApplicationType, ApplicationStatusType
# from apps.license_template.models import License, LicenseType

# def normalize_inn(val):
#     if pd.isna(val):
#         return None
#     return str(val).split('.')[0]


# def parse_excel_and_create_models(file):
#     # Читаем файл
#     df = pd.read_excel(file)

#     # Предположим, что у тебя есть колонки:
#     # customer_name, customer_email, product_title, product_price, quantity, order_date

#     for _, row in df.iterrows():
#         print(f"Processing row: {row.to_dict()}")
#         try:
#             inn_org = normalize_inn(row['ИНН организации'])
#             inn_rep = normalize_inn(row['ИНН поручителя'])
#             organization, _ = Organization.objects.get_or_create(
#                 name=row['Название организации'],
#                 inn=inn_org,
#                 representative=inn_rep
#             )

#             license_type = LicenseType.objects.get(title=row['Тип лицензии'])
            

#             application, _ = Application.objects.get_or_create(
#                 applicants_full_name=row['ФИО заявителя'],
#                 applicants_status=row['Статус заявителя'],
#                 organization=organization,
#                 organization_name=row['Название организации'],
#                 email=row['Почта'],
#                 phone_number=row['Номер телефона'],
#                 other_information=row.get('Другие сведения', ''),
#                 ownership_form=row['Форма собственности'],
#                 legal_address=row['Юридический адрес'],
#                 actual_address=row['Фактический адрес'],
#                 inn=inn_org,
#                 okpo_code=row['Код ОКПО'],
#                 owner_full_name=row['ФИО руководителя'],
#                 register_date=row.get('Дата регистрации юр.лица'),
#                 application_type=row.get('Тип заявки', ApplicationType.SUBMITTING),
#                 is_archived=True,
#                 status=ApplicationStatusType.APPROVED

#             )
#             if _ or not application.license_type.filter(pk=license_type.pk).exists():
#                 application.license_type.add(license_type)
            
            # def to_date_str(val):
            #     if pd.isna(val):
            #         return None
            #     if hasattr(val, 'date'):
            #         return val.date().isoformat()
            #     if hasattr(val, 'isoformat'):
            #         return val.isoformat()
            #     return str(val)
            # expiration_date=to_date_str(row.get('Срок действия лицензии'))
            
#             try:
#                 license, _ = License.objects.get_or_create(
#                     registration_number=row['Регистрационный номер по реестру лицензий'],
#                     issued_date=row['Дата выдачи'],
#                     issued_by=row['Выдана'],
#                     licensee_address=row['Адрес лицензиата'],
#                     state_registration_certificate=row['Свидетельство о государственной регистрации'],
#                     state_registration_issued_by=row['Кем выдана государственная регистрация'],
#                     inn=inn_org,
#                     license_type=license_type,
#                     expiration_date=expiration_date,
#                     expired=row.get('Анулировано', False),
#                     registrable_type=row.get('Лицензия является', 0),
#                     application=application,
#                     volume=row.get('Объем лицензии', ''),
#                     license_terms=row.get('Лицензионные условия', ''),
#                     direct_aproved=True
#                 )
#             except Exception as e:
#                 print(f"Error creating License for row {row.to_dict()}: {e}")
#                 continue
#             if _:
#                 print(f"Created License: {license.registration_number}")
#         except Exception as e:
#             print(f"Error processing row {row.to_dict()}: {e}")



import pandas as pd
from datetime import datetime, date

from apps.organization.models import Organization
from apps.application.models import Application
from apps.application.choices import ApplicationType, ApplicationStatusType
from apps.license_template.models import License, LicenseType
from core.tasks import parsing_row


# =========================
# Универсальные нормализаторы
# =========================

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
    if val is None or pd.isna(val):
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
            
            

# =========================
# Основной парсер
# =========================

def parse_excel_and_create_models(file):
    df = pd.read_excel(file, dtype=str)
    for _, row in df.iterrows():
        row_dict = row.where(pd.notna(row), None).to_dict()
        parsing_row.delay(_, row_dict)