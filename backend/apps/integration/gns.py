import uuid
from zeep import Client, Settings
from zeep.transports import Transport
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep.plugins import HistoryPlugin
from lxml import etree
import os
from decouple import config
from django.conf import settings
from zeep.helpers import serialize_object
import logging
import requests

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY_SERVER_URL = settings.WSDL_FILE_PATH_GNS

TUNDUK_URL = config('TUNDUK_URL')
ENDPOINT_PATH = config('ENDPOINT_PATH')
X_ROAD_CLIENT = config('X_ROAD_CLIENT')

USERNAME = config("USERNAME")
PASSWORD = config("PASSWORD")

def get_data_from_gns(inn):
    url = f"{TUNDUK_URL}{ENDPOINT_PATH}"
    headers = {
        "X-Road-Client": X_ROAD_CLIENT
    }

    # try:
    print(url+inn)
    response = requests.get(
        url=url+inn,
        headers=headers,
        verify=False,
        timeout=10
    )
    print(response)
    if response.status_code==404:
        raise Exception('Такой организации не найдено')

    logger.info(f'requesting url: {url}?inn={inn}')
    return response.json()
    # except requests.exceptions.RequestException as e:
    #     logger.error(f'Error while requesting GNS: {e}', exc_info=True)
    #     return {
    #         "msg": "Error from GNS"
    #     }


# def get_client():
#     if not os.path.exists(SECURITY_SERVER_URL):
#         raise FileNotFoundError(f"WSDL file not found: {SECURITY_SERVER_URL}")
#     session = Session()
#     session.auth = HTTPBasicAuth(USERNAME, PASSWORD)
#     # session.verify = CLIENT_CERT_PATH
#     session.verify = False
#     # session.cert = (CERTIFICATE_PATH)

#     class CustomTransport(Transport):
#         def __init__(self, *args, **kwargs):
#             kwargs['session'] = session
#             super().__init__(*args, **kwargs)

#     transport = CustomTransport()

#     settings = Settings(strict=False, xml_huge_tree=True)
#     history = HistoryPlugin()

#     client = Client(wsdl=SECURITY_SERVER_URL, settings=settings, transport=transport, plugins=[history])
#     return client


# def convert_to_dict(obj):
#     if isinstance(obj, dict):
#         return {k: convert_to_dict(v) for k, v in obj.items()}
#     elif isinstance(obj, list):
#         return [convert_to_dict(v) for v in obj]
#     elif isinstance(obj, etree._Element):
#         return etree.tostring(obj, encoding='unicode')
#     elif hasattr(obj, '__dict__'):
#         return {k: convert_to_dict(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
#     else:
#         return obj


# def get_data_from_gns(tin):
#     header = {
#         'client': {
#             'xRoadInstance': 'central-server',
#             'memberClass': 'GOV',
#             'memberCode': '70000088',
#             'subsystemCode': 'dfekt-service',
#             'objectType': 'SUBSYSTEM'
#         },
#         'service': {
#             'xRoadInstance': 'central-server',
#             'memberClass': 'GOV',
#             'memberCode': '70000002',
#             'subsystemCode': 'gns-service',
#             'serviceCode': 'tpDataByINN',
#             'objectType': 'SERVICE'
#         },
#         'userId': 'katana',
#         'id': str(uuid.uuid4()),
#         'protocolVersion': '4.0'
#     }

#     body = {
#         'inn': tin,
#     }

#     client = get_client()
#     print(client,11111111111111)

#     try:
#         print(client.service.__dict__)
#         response = client.service.tpDataByINN(_soapheaders=header, request=body)
#         print(1)
#         serialized_response = serialize_object(response)
#         print(2)
#         dict_response = convert_to_dict(serialized_response).get('body')
#         print(3)
#         return dict_response

#     except Exception as e:
#         logger.error(f"Ошибка при вызове SOAP-сервиса: {e}", exc_info=True)
#         return {"message": "Произошла ошибка при обработке запроса"}



# get_data_from_minust('0123456789')