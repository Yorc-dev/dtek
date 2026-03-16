import jwt
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework import views
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from decouple import config
from django.db.models import Prefetch
from django.db import models
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from .filters import LicenseFilter
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.db.models import Q

from rest_framework import status

from apps.license_template.models import License
from apps.application.models import Application
from apps.integration.gns import get_data_from_gns
from apps.integration.minust import get_data_from_minust
from apps.integration.encp import get_auth_methods, send_pin_code, get_user_token

from .models import Organization
from .serializers import OrganizationSerializer

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"

def generate_org_tokens(org):
    payload_access = {
        "org_id": org.id,
        "iin": org.inn,
        "type": "access",
        "exp": datetime.utcnow() + timedelta(minutes=20),
    }
    payload_refresh = {
        "org_id": org.id,
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=7),
    }
    access = jwt.encode(payload_access, SECRET_KEY, algorithm=ALGORITHM)
    refresh = jwt.encode(payload_refresh, SECRET_KEY, algorithm=ALGORITHM)
    return {"access": access, "refresh": refresh}


class GNSInnView(views.APIView):
    def get(self, request):
        bearer_token = config('BEARER_TOKEN')
        org_inn = request.query_params.get('org_inn')

        if not org_inn:
            return Response(
                {
                    "msg": "inn parameter is required"
                }
            )
        try:
            try:
                print(222)
                data = get_data_from_gns(org_inn)
                print(111)
            except Exception as e:
                return Response({'msg':str(e)}, status=404)
            
            auth_methods = get_auth_methods(token=bearer_token,  person_idnp=org_inn)
            
            try:
                chosen_method = auth_methods["userAuthMethodList"][0]["authType"]
            except:
                return Response({'msg':auth_methods['errorMessage']}, status=auth_methods['errorCode'])
            
            send_pin_code(bearer_token, person_idnp=org_inn, method=chosen_method)
            
            return Response(data, status=200)
        except Exception as e:
            return Response({
                "msg": f"{e}"
            })
        
class CheckPINCodeView(views.APIView):
    def get(self, request):
        bearer_token = config('BEARER_TOKEN')
        org_inn = request.query_params.get('org_inn') or None
        person_inn = request.query_params.get('person_inn') or None
        pincode = request.query_params.get('code')

        if not org_inn:
            return Response(
                {
                    "msg": "inn parameter is required"
                }
            )
        try:
            if person_inn:
                print(1)
                data = get_data_from_minust(org_inn)
                user_token_response = get_user_token(token=bearer_token, person_idnp=person_inn, org_inn=org_inn, pin_code=pincode)
                organization_name = data['subject']['shortNameOl']
                kwargs = {"name":organization_name, "representative":person_inn}
                data['subject'].update({"opf":organization_name.split()[0]})
            else:
                print(1)
                data = get_data_from_gns(org_inn)
                print(data)
                user_token_response = get_user_token(token=bearer_token, person_idnp=org_inn, pin_code=pincode)
                print(user_token_response)
                organization_name = f'{data['lastName']} {data['firstName']} {data['middleName']}' 
                print(organization_name)
                kwargs = {"name":organization_name, "representative":org_inn}
            try:
                return Response({'msg':user_token_response['errorMessage']}, status=user_token_response['errorCode'])
            except:
                org, _ = Organization.objects.get_or_create(inn=org_inn, defaults=kwargs)
                tokens = generate_org_tokens(org)
                tokens.update(data)
                return Response(tokens)
                
        except Exception as e:
            return Response({
                "msg": f"{e}"
            })

class MinustInnView(views.APIView):
    def get(self, request):
        bearer_token = config('BEARER_TOKEN')
        org_inn = request.query_params.get('org_inn')
        person_inn = request.query_params.get('person_inn')
        if not org_inn:
            return Response(
                {
                    "msg": "inn parameter is required"
                }
            )
        try:
            data = {}
            try:
                data = get_data_from_minust(org_inn)
            except Exception as e:
                data = {'msg':f'Такой организации не существует. {e}'}
                return Response(data, status=404)

            auth_methods = get_auth_methods(token=bearer_token,  org_inn=org_inn, person_idnp=person_inn)
            
            try:
                chosen_method = auth_methods["userAuthMethodList"][0]["authType"]
            except:
                return Response({'msg':auth_methods['errorMessage']}, status=auth_methods['errorCode'])
            
            send_pin_code(bearer_token, person_idnp=person_inn, org_inn=org_inn, method=chosen_method)

            return Response(data, status=200)
        except Exception as e:
            return Response({
                "msg": f"{e}"
            })
 

# class OrganizationListAPIView(ListAPIView):
#     queryset = Organization.objects.all()
#     serializer_class = OrganizationSerializer
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter]
#     # filterset_class = LicenseFilter
#     search_fields = [
#         'licenses__registration_number',  # регистрационный номер
#         'name',                           # организация
#         'licenses__inn',                  # ИНН
#     ]


#     def get_queryset(self):
#         queryset = Organization.objects.all()

#         application_id = self.request.query_params.get("application_id")
#         if application_id:
#             queryset = queryset.filter(
#                 inn__in=License.objects.filter(application__id=application_id)
#                 .values_list("inn", flat=True)
#             ).distinct()

#         # если пришли параметры фильтра — фильтруем по связанным лицензиям
#         filters_applied = {}
#         for key in ['registration_number', 'inn', 'status', 'suspension', 'expired']:
#             value = self.request.query_params.get(key)
#             if value is not None:
#                 filters_applied[f"licenses__{key}"] = value

#         if filters_applied:
#             queryset = queryset.filter(**filters_applied).distinct()

#         # поддержка поиска по поисковым полям DRF (рег. номер, организация, ИНН)
#         search = self.request.query_params.get('search')
#         if search:
#             queryset = queryset.filter(
#                 models.Q(licenses__registration_number__icontains=search)
#                 | models.Q(name__icontains=search)
#                 | models.Q(licenses__inn__icontains=search)
#             ).distinct()

#         return queryset

def _parse_date(s: str):
    if not s:
        return None
    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None

class OrganizationListAPIView(ListAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = [
        'licenses__registration_number',  # регистрационный номер
        'name',                           # организация
        'licenses__inn',                  # ИНН
    ]

    def get_queryset(self):
        queryset = Organization.objects.all()

        application_id = self.request.query_params.get("application_id")
        if application_id:
            queryset = queryset.filter(
                inn__in=License.objects.filter(application__id=application_id)
                .values_list("inn", flat=True)
            ).distinct()

        # Базовые фильтры по связанным лицензиям
        FILTER_KEY_MAP = {
            'registration_number': 'licenses__registration_number',
            'inn': 'licenses__inn',
            'status': 'licenses__status',
            'suspension': 'licenses__suspension',
            'expired': 'licenses__expired',
        }
        for param, filter_key in FILTER_KEY_MAP.items():
            value = self.request.query_params.get(param)
            if value is not None and value != "":
                queryset = queryset.filter(**{filter_key: value}).distinct()

        # Фильтр по группе типа лицензии
        license_group = self.request.query_params.get("license_group")
        if license_group:
            values = [v.strip() for v in license_group.split(",") if v.strip() != ""]
            groups = []
            for v in values:
                try:
                    groups.append(int(v))
                except ValueError:
                    continue
            if len(groups) == 1:
                queryset = queryset.filter(
                    licenses__license_type__license_group=groups[0]
                ).distinct()
            elif groups:
                queryset = queryset.filter(
                    licenses__license_type__license_group__in=groups
                ).distinct()

        # Фильтр по периоду
        date_from = _parse_date(self.request.query_params.get("date_from"))
        date_to = _parse_date(self.request.query_params.get("date_to"))
        active_period = str(self.request.query_params.get("active_period", "")).lower() in ("1", "true", "yes")

        # Если задан хотя бы один край диапазона — применяем фильтр
        if date_from or date_to:
            if active_period:
                # Пересечение активного периода лицензии с диапазоном:
                # issued_date <= date_to (если задан) AND (expiration_date >= date_from OR expiration_date is null, если задан date_from)
                conds = Q()
                if date_to:
                    conds &= Q(licenses__issued_date__lte=date_to)
                if date_from:
                    conds &= (Q(licenses__expiration_date__gte=date_from) | Q(licenses__expiration_date__isnull=True))
                queryset = queryset.filter(conds).distinct()
            else:
                # Фильтрация по дате выдачи
                if date_from and date_to:
                    queryset = queryset.filter(
                        licenses__issued_date__range=(date_from, date_to)
                    ).distinct()
                elif date_from:
                    queryset = queryset.filter(
                        licenses__issued_date__gte=date_from
                    ).distinct()
                elif date_to:
                    queryset = queryset.filter(
                        licenses__issued_date__lte=date_to
                    ).distinct()

        # Поиск (рег. номер, организация, ИНН)
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(licenses__registration_number__icontains=search)
                | Q(name__icontains=search)
                | Q(licenses__inn__icontains=search)
            ).distinct()

        return queryset
# class OrganizationListAPIView(ListAPIView):
#     queryset = Organization.objects.all()
#     serializer_class = OrganizationSerializer



SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"

class OrganizationTokenRefreshView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response({"detail": "Требуется refresh токен"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            return Response({"detail": "Refresh токен истёк"}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({"detail": "Неверный refresh токен"}, status=status.HTTP_401_UNAUTHORIZED)

        if payload.get("type") != "refresh":
            return Response({"detail": "Нужен refresh токен"}, status=status.HTTP_400_BAD_REQUEST)

        org_id = payload.get("org_id")
        try:
            org = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            return Response({"detail": "Организация не найдена"}, status=status.HTTP_404_NOT_FOUND)

        # Генерим новый access
        new_access_payload = {
            "org_id": org.id,
            "type": "access",
            "exp": datetime.utcnow() + timedelta(minutes=30),
        }
        new_access_token = jwt.encode(new_access_payload, SECRET_KEY, algorithm=ALGORITHM)

        return Response({
            "access": new_access_token
        })
    


class RevokeOrganizationLicensesView(APIView):
    """
    POST /api/revoke-organization-licenses/
    {
        "application_id": 123
    }

    Деактивирует все лицензии организации, связанной с этой заявкой.
    """

    def post(self, request):
        application_id = request.data.get("application_id")
        if not application_id:
            return Response(
                {"detail": "Поле 'application_id' обязательно."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # достаём заявку
        application = get_object_or_404(Application, id=application_id)

        # достаём организацию
        organization = application.organization
        if not organization:
            return Response(
                {"detail": "У этой заявки нет связанной организации."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # находим все лицензии этой организации (по ИНН)
        licenses = License.objects.filter(inn=organization.inn)

        if not licenses.exists():
            return Response(
                {"detail": "У этой организации нет лицензий."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # аннулируем лицензии
        licenses.update(expired=True, status=False)

        return Response(
            {
                "detail": f"Анулировано {licenses.count()} лицензий организации '{organization.name}'."
            },
            status=status.HTTP_200_OK,
        )