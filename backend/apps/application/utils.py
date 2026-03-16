import base64
from io import BytesIO

from docxtpl import DocxTemplate

from core.settings import BASE_DIR



def render_application_to_docx(application):
    from django.conf import settings
    import os

    doc = DocxTemplate(f"{BASE_DIR}/apps/integration/Заявление на выдачу.docx")

    license_types = ", ".join(application.license_type.values_list('title', flat=True))
    MONTH_NAMES = [
        "января", "февраля", "марта", "апреля", "мая", "июня",
        "июля", "августа", "сентября", "октября", "ноября", "декабря"
    ]

    context = {
        "applicants_full_name": application.applicants_full_name,
        "phone_number": application.phone_number,
        "email": application.email,
        "organization_name": application.organization_name,
        "form_type": application.form_type,
        "ownership_form": application.ownership_form,
        "legal_address": application.legal_address,
        "actual_address": application.actual_address,
        "inn": application.inn,
        "okpo_code": application.okpo_code,
        "register_date": application.register_date.strftime("%d.%m.%Y") if application.register_date else "",
        "other_information": application.other_information or "",
        "day": application.created_at.strftime("%d"),
        "month": MONTH_NAMES[int(application.created_at.strftime("%m"))-1],
        "year": application.created_at.strftime("%Y"),
        "owner_full_name": application.owner_full_name,
        "license_types": license_types
    }

    doc.render(context)

    dir_path = os.path.join(settings.MEDIA_ROOT, "applications", "docs")
    os.makedirs(dir_path, exist_ok=True)

    file_name = f"{application.id}_заявление.docx"
    file_path = os.path.join(dir_path, file_name)
    doc.save(file_path)

    with open(file_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    return file_path, encoded
