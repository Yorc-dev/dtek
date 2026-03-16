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

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECURITY_SERVER_URL = settings.WSDL_FILE_PATH_MINUST
# SECURITY_SERVER_URL = '/home/katana/Desktop/work/yorc/last_repo_dtek/dtek_is-backend/backend/apps/integration/min.wsdl'


USERNAME = config("SOAP_USERNAME")
PASSWORD = config("SOAP_PASSWORD")
# CERTIFICATE_PATH = os.path.join(BASE_DIR, "integration/", config("CERTIFICATE_PATH"))
# CLIENT_CERT_PATH = os.path.join(BASE_DIR, "integration/", config("CLIENT_CERT_PATH"))
SERVER_URL = config("SERVER_URL")


def get_client():
    if not os.path.exists(SECURITY_SERVER_URL):
        raise FileNotFoundError(f"WSDL file not found: {SECURITY_SERVER_URL}")
    session = Session()
    session.auth = HTTPBasicAuth(USERNAME, PASSWORD)
    # session.verify = CLIENT_CERT_PATH
    session.verify = False
    # session.cert = (CERTIFICATE_PATH)

    class CustomTransport(Transport):
        def __init__(self, *args, **kwargs):
            kwargs['session'] = session
            super().__init__(*args, **kwargs)

    transport = CustomTransport()

    settings = Settings(strict=False, xml_huge_tree=True)
    history = HistoryPlugin()

    client = Client(wsdl=SECURITY_SERVER_URL, settings=settings, transport=transport, plugins=[history])
    return client


def convert_to_dict(obj):
    if isinstance(obj, dict):
        return {k: convert_to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_dict(v) for v in obj]
    elif isinstance(obj, etree._Element):
        return etree.tostring(obj, encoding='unicode')
    elif hasattr(obj, '__dict__'):
        return {k: convert_to_dict(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
    else:
        return obj


def get_data_from_minust(tin):
    header = {
        'client': {
            'xRoadInstance': 'central-server',
            'memberClass': 'GOV',
            'memberCode': '70000088',
            'subsystemCode': 'dfekt-service',
            'objectType': 'SUBSYSTEM'
        },
        'service': {
            'xRoadInstance': 'central-server',
            'memberClass': 'GOV',
            'memberCode': '70000024',
            'subsystemCode': 'minjust-service',
            'serviceCode': 'getSubjectByTin',
            'objectType': 'SERVICE'
        },
        'userId': 'asdasd',
        'id': str(uuid.uuid4()),
        'protocolVersion': '4.0'
    }

    body = {
        'tin': tin,
    }

    client = get_client()

    response = client.service.getSubjectByTin(_soapheaders=header, **body)
    serialized_response = serialize_object(response)
    dict_response = convert_to_dict(serialized_response).get('body')
    return dict_response




# get_data_from_minust('0123456789')