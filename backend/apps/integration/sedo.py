import requests
import base64
import json
from typing import List, Dict
from decouple import config
# Константы (лучше хранить во внешнем конфиге или .env)
ACCESS_KEY = config('ACCESS_KEY')
SECRET_KEY = config('SECRET_KEY')
API_URL = config('API_URL')


def prepare_file_payload(docs, file_name: str, signature: str) -> Dict:
    """
    Готовит словарь для основного или вложенного файла
    :param file_path: путь к файлу
    :param file_name: имя файла без расширения
    :param signature: подпись ОЭЦП файла
    :return: словарь для поля 'doc_file' или элемента в 'doc_attach_files'
    """
    return {
        "fileName": file_name,
        "fileExt": 'docs',
        "fileBody": docs,
        "fileSignature": signature
    }


def build_document_payload(
    sender_inn: str,
    receiver_inn: str,
    doc_number: str,
    main_file: Dict,
) -> Dict:
    """
    Формирует полный JSON payload документа
    :param sender_inn: ИНН отправителя
    :param receiver_inn: ИНН получателя
    :param doc_number: номер документа
    :param main_file: основной файл (dict)
    :param attachments: список вложений (list of dict)
    :return: JSON-словарь запроса
    """
    return {
        "org_sender_inn": sender_inn,
        "org_receiver_inn": receiver_inn,
        "doc_number": doc_number,
        "doc_lang_ky": "ky",
        "doc_lang_ru": "ru",
        "doc_lang_fl": "en",
        "doc_type": "LETTER",
        "doc_registered": "2022-05-10 13:30:00",
        "doc_deadline": "2022-05-20 12:30:00",
        "doc_signature": "строка_подписи_ОЭЦП",
        "signature_algorithm": "gost3411",
        "doc_extra_fields": json.dumps({"some-field": 123}),
        "doc_creater_name": "Фамилия Имя Отчество",
        "doc_signer_name": "Фамилия Имя Отчество",
        "doc_description": "описание документа",
        "doc_fyi": "true",
        "doc_uuid_related": "4ca69ad9-c409-4e5c-b3b7-2f2bd8b34f94",
        "doc_number_related": "333-11",
        "doc_registered_related": "2022-05-30 10:30:00",
        "doc_file": main_file,
        "doc_attach_files": []
    }


def send_document(payload: Dict) -> None:
    """
    Отправляет документ через REST API
    :param payload: сформированный JSON payload
    """
    headers = {
        'x-access-key': ACCESS_KEY,
        'x-secret-key': SECRET_KEY,
        'Content-Type': 'application/json;charset=utf-8'
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    print(response.status_code)
    if response.status_code != 200:
        print(f"ОШИБКА SEDO: {response.status_code}")
        print(f"ОТВЕТ СЕРВЕРА: {response.text}")
    return response.status_code


def main():
    """
    Главная функция: подготовка и отправка документа
    """
    # Подготовка основного файла
    main_file = prepare_file_payload(
        file_path="test.docx",
        file_name="док-проверка",
        signature="подпись_файла_в_ОЭЦП"
    )


    # Сборка тела запроса
    payload = build_document_payload(
        sender_inn="00406200710110",
        receiver_inn="00406200710110",
        doc_number="11-333",
        main_file=main_file,
        # attachments=attachments
    )

    # Отправка документа
    send_document(payload)


# Запуск
if __name__ == "__main__":
    main()