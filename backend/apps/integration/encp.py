import requests
import time
from decouple import config
API_BASE = config('API_BASE')
HEADERS_TEMPLATE = {
    "Content-Type": "application/json;charset=utf-8",
    "User-Agent":"Postman"
}

def get_auth_methods(token, person_idnp=None, org_inn=None):
    url = f"{API_BASE}/api/user-auth-methods"
    headers = HEADERS_TEMPLATE.copy()
    headers["Authorization"] = f"Bearer {token}"
    data = {}
    if person_idnp and org_inn:
        data = {"organizationInn": org_inn, "personIdnp":person_idnp}
    elif person_idnp:
        data = {"personIdnp": person_idnp}
    data = requests.post(url=url, headers=headers, json=data).json()
    return data

def send_pin_code(token, person_idnp=None, org_inn=None, method="sms"):
    url = f"{API_BASE}/api/get-pin-code"
    headers = HEADERS_TEMPLATE.copy()
    headers["Authorization"] = f"Bearer {token}"

    data = {"method": method}
    if person_idnp and org_inn:
        data.update({"personIdnp": person_idnp, "organizationInn": org_inn})
    elif org_inn:
        data.update({"organizationInn": org_inn})
    elif person_idnp:
        data.update({"personIdnp": person_idnp})
    return requests.post(url, headers=headers, json=data).json()

def get_user_token(token, pin_code, person_idnp=None, org_inn=None):
    url = f"{API_BASE}/api/account/auth"
    headers = HEADERS_TEMPLATE.copy()
    headers["Authorization"] = f"Bearer {token}"

    data = {"byPin": pin_code}
    if person_idnp and org_inn:
        data.update({"personIdnp": person_idnp, "organizationInn": org_inn})
    elif person_idnp:
        data.update({"personIdnp": person_idnp})
    return requests.post(url, headers=headers, json=data).json()

def get_cert_info(user_token, bearer_token):
    url = f"{API_BASE}/api/get-cert-info"
    headers = HEADERS_TEMPLATE.copy()
    headers["Authorization"] = f"Bearer {bearer_token}"
    data = {"userToken": user_token}
    return requests.post(url, headers=headers, json=data).json()

def sign_hash(hash_value, user_token, bearer_token):
    url = f"{API_BASE}/api/get-sign/for-hash"
    headers = HEADERS_TEMPLATE.copy()
    headers["Authorization"] = f"Bearer {bearer_token}"
    data = {"hash": hash_value, "userToken": user_token}
    return requests.post(url, headers=headers, json=data).json()

def verify_signature(signature_base64, hash_value, bearer_token):
    url = f"{API_BASE}/api/check-sign/for-hash"
    headers = HEADERS_TEMPLATE.copy()
    headers["Authorization"] = f"Bearer {bearer_token}"
    data = {"signBase64": signature_base64, "hash": hash_value}
    return requests.post(url, headers=headers, json=data).json()

def main():
    # 🔧 Настройки
    bearer_token = "Jr6b8gqhOV-JZf2cjwQB3_bQq21BiyWh3VsAaql0i_g"  # выданный ГП Инфоком
    person_idnp = "20101200100111"
    organization_inn = "01234567891234"
    hash_to_sign = "3FBCE39F6274CBE69D9A843C8CB04C0B9E43776E2D6A6C17C9948C81017B92F0"

    # 1. Получение доступных методов авторизации
    auth_methods = get_auth_methods(bearer_token, person_idnp, organization_inn)
    print("Доступные методы авторизации:", auth_methods)

    # 2. Отправка PIN-кода
    chosen_method = auth_methods["userAuthMethodList"][0]["authType"]
    pin_send_result = send_pin_code(bearer_token, person_idnp, organization_inn, chosen_method)
    print("Результат отправки PIN-кода:", pin_send_result)

    # 3. Ввод PIN-кода вручную
    pin_code = input("Введите полученный PIN-код: ")

    # 4. Получение userToken
    user_token_response = get_user_token(bearer_token, person_idnp, organization_inn, pin_code)
    print("Токен пользователя:", user_token_response)
    user_token = user_token_response["token"]

    # 5. Получение информации о сертификате
    cert_info = get_cert_info(user_token, bearer_token)
    print("Информация о сертификате:", cert_info)

    # 6. Подписание хэша
    sign_response = sign_hash(hash_to_sign, user_token, bearer_token)
    print("Результат подписи:", sign_response)

    # 7. Проверка подписи (опционально)
    verify = verify_signature(sign_response["sign"], hash_to_sign, bearer_token)
    print("Результат проверки подписи:", verify)

if __name__ == "__main__":
    main()