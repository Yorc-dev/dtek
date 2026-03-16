import base64
from io import BytesIO
import qrcode
from docx.shared import Mm
import os
from django.conf import settings


from docxtpl import DocxTemplate, InlineImage
from django.core.files.base import ContentFile
from decouple import config

from apps.integration.minust import get_data_from_minust
from apps.integration.gns import get_data_from_gns

from core.settings import BASE_DIR


def render_license_to_docx(license, application_obj):
    doc = DocxTemplate(f"{BASE_DIR}/apps/integration/license_templare_ru.docx")

    # license_types = ", ".join(license.license_type.values_list('title', flat=True))
    MONTH_NAMES = [
    "января", "февраля", "марта", "апреля", "мая", "июня",
    "июля", "августа", "сентября", "октября", "ноября", "декабря"
    ]
    DOMAIN = config('DOMAIN')
    download_url = license.document.url if license.document else f"/licenses/{license.pk}/download/"
    download_url = DOMAIN + download_url
    qr_io = BytesIO()
    img = qrcode.make(download_url)
    img.save(qr_io, format="PNG")
    qr_io.seek(0)
    organization = application_obj.organization
    if application_obj.applicants_status == 1: 
        minust_data = get_data_from_minust(organization.inn)
        register = {
            "registration_certificate":minust_data.get("subject").get('registrCode'), 
            "issued_by_whom_and_when": 'Министерство юстиции Кыргызской республики ' + minust_data.get("subject").get('firstOrderDate')
        }
    else:
        minust_data = get_data_from_gns(organization.inn)
        register = {
            "registration_certificate":minust_data.get("certificateNumber"), 
            "issued_by_whom_and_when": 'Министерство юстиции Кыргызской республики ' + minust_data.get('registrationDate').split('T')[0]
        }
    print(minust_data)
    qr_image = InlineImage(doc, qr_io, width=Mm(30))
    licenses = license.license_type
    activities = ', '.join([activite.text for activite in licenses.activities.all()])
    context = {
        "register_number": license.registration_number,
        "recipient_name": organization.name,
        "recipient_address": license.licensee_address,
        "registration_certificate": register.get( "registration_certificate"),
        "issued_by_whom_and_when": register.get("issued_by_whom_and_when"),
        "recipient_pin": license.inn,
        "allowed_activities": activities,
        "validity_period": license.expiration_date.strftime("%d.%m.%Y") if license.expiration_date else "",
        "license_type": license.get_registrable_type_display(),
        "license_terms": license.license_terms_ky,
        "day": license.issued_date.strftime("%d"),
        "month": MONTH_NAMES[int(license.issued_date.strftime("%m")) - 1],
        "year": license.issued_date.strftime("%Y"),
        "qr_code": qr_image,
        "link":download_url
    }
    doc.render(context)

    output = BytesIO()
    doc.save(output)
    output.seek(0)
    return output
    

import subprocess
import uuid
import os
from io import BytesIO


def convert_docx_bytes_to_pdf_bytes(docx_bytes: BytesIO) -> BytesIO:
    input_path = f"/tmp/{uuid.uuid4()}.docx"
    output_path = f"/tmp/{uuid.uuid4()}.pdf"

    # Save DOCX to tmp
    with open(input_path, "wb") as f:
        f.write(docx_bytes.read())

    # Convert via LibreOffice
    subprocess.run([
        "libreoffice",
        "--headless",
        "--convert-to", "pdf",
        "--outdir", "/tmp",
        input_path
    ], check=True)

    # libreoffice produces a pdf with same name but .pdf
    produced_pdf = input_path.replace(".docx", ".pdf")

    pdf_bytes = BytesIO()
    with open(produced_pdf, "rb") as f:
        pdf_bytes.write(f.read())

    pdf_bytes.seek(0)

    # cleanup
    os.remove(input_path)
    os.remove(produced_pdf)

    return pdf_bytes



from django.core.files.base import ContentFile


def save_license_docx(license_obj, application_obj):
    # 1. Генерация DOCX в памяти
    output_docx = render_license_to_docx(license_obj, application_obj)

    # 2. Конвертация DOCX → PDF
    output_docx.seek(0)
    output_pdf = convert_docx_bytes_to_pdf_bytes(output_docx)

    # 3. Сохраняем PDF в поле `document`
    filename_pdf = f"license_{license_obj.registration_number or license_obj.pk}.pdf"
    license_obj.document.save(filename_pdf, ContentFile(output_pdf.read()), save=True)
