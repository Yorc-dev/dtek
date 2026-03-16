from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import FileResponse, Http404
from django.views import View
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated

import os
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch
from django.core.exceptions import MultipleObjectsReturned
from rest_framework import status
from django.db import IntegrityError, transaction
from drf_spectacular.utils import extend_schema, OpenApiExample
from apps.integration.encp import get_auth_methods, send_pin_code, get_user_token
from decouple import config

from apps.integration.encp import send_pin_code, sign_hash
from apps.license_template.models import LicenseType, LicenseTemplateFieldValue, LicenseTemplateFieldOrder, LicenseTemplate, Activity, License
from apps.license_template.serializers import LicenseTypeSerializer, LicenseTemplateFieldValueSerializer, LicenseSerializer, ActivitySerializer, LicenseListSerializer, LicenseTypeShortSerializer

from .utils import render_license_to_docx

class LicenseTypeShortListAPIView(generics.ListAPIView):
    queryset = LicenseType.objects.all()
    serializer_class = LicenseTypeShortSerializer

@extend_schema(
    tags=["License"],
    description="Получение списка типов лицензий с их шаблонами и полями.",
    responses={200: LicenseTypeSerializer}
)
class LicenseTypeListView(generics.ListAPIView):
    queryset = (
        LicenseType.objects.prefetch_related(
            Prefetch(
                "templates",
                queryset=LicenseTemplate.objects.select_related("license_type").prefetch_related(
                    Prefetch(
                        "field_order",
                        queryset=LicenseTemplateFieldOrder.objects.select_related("field").order_by("order"),
                        to_attr="ordered_fields"
                    )
                ),
                to_attr="templates_list"
            )
        )
    )
    serializer_class = LicenseTypeSerializer


@extend_schema(
    tags=["License"],
    description="Создание значений полей шаблона лицензии.",
    request=LicenseTemplateFieldValueSerializer,
    responses={201: LicenseTemplateFieldValueSerializer},
    examples=[
        OpenApiExample(
            "Пример запроса",
            summary="Создание значения поля шаблона",
            value={
                "field": 1,
                "value": "Примерное значение",
                "template": 2
            },
            request_only=True,
        ),
        OpenApiExample(
            "Пример ответа",
            summary="Успешное создание значения",
            value={
                "id": 5,
                "field": 1,
                "value": "Примерное значение",
                "template": 2
            },
            response_only=True,
        ),
    ],
)
class LicenseTemplateFieldsCreateView(generics.CreateAPIView):
    serializer_class = LicenseTemplateFieldValueSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        created_or_updated_objects = []
        try:
            for instance in serializer.validated_data:

                field_value_obj, _ = LicenseTemplateFieldValue.objects.update_or_create(
                    application=instance.get('application'),
                    field=instance.get('field'),
                    license_type=instance.get('license_type'),
                    defaults=instance
                )
                created_or_updated_objects.append(field_value_obj)
        except MultipleObjectsReturned:
            return Response(
                {
                    'msg': 'The field duplicated in db, you must first delete it'
                }
            )
        return Response(
            {'message': 'Success'},
            status=201
        )    # ToDo отдавать созданные объекты


@extend_schema(
    tags=["License"],
    description="Обновление значений полей шаблона лицензии.",
    request=LicenseTemplateFieldValueSerializer,
    responses={200: LicenseTemplateFieldValueSerializer},
    examples=[
        OpenApiExample(
            "Пример запроса",
            summary="Обновление значения поля шаблона",
            value={
                "value": "Новое значение"
            },
            request_only=True,
        ),
        OpenApiExample(
            "Пример ответа",
            summary="Успешное обновление",
            value={
                "id": 5,
                "field": 1,
                "value": "Новое значение",
                "template": 2
            },
            response_only=True,
        ),
    ],
)
class LicenseTemplateFieldValueUpdateView(generics.UpdateAPIView):
    serializer_class = LicenseTemplateFieldValueSerializer
    queryset = LicenseTemplateFieldValue.objects.all()

    # def patch(self, request, *args, **kwargs):
    #     template_fields = request.data
    #     print(template_fields, '!!!!!!!!!')
    #     for inst in template_fields:
    #         instances = LicenseTemplateFieldValue.objects.filter(application=)
    #         serializer = self.serializer_class(data=inst)
    #         serializer.is_valid(raise_exception=True)
    #         serializer.update(serializer.instance, serializer.validated_data)
    #     return Response('good')

class LicenseCreateAPIView(generics.CreateAPIView):
    serializer_class = LicenseSerializer

class LicenseListAPIView(generics.ListAPIView):
    queryset = License.objects.all().order_by('-issued_date')
    serializer_class = LicenseListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['expired', 'suspension', 'registration_number']
    
    def get_queryset(self):
        organization = self.request.user  
        return License.objects.filter(
            application__organization=organization
        ).order_by('-issued_date')
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        active_count = queryset.filter(status=True, expired=False, suspension=False).count()

        inactive_count = queryset.filter(
            Q(status=False) | Q(expired=True) | Q(suspension=True)
        ).count()

        serializer = self.get_serializer(queryset, many=True)

        return Response({
            "active_count": active_count,
            "inactive_count": inactive_count,
            "results": serializer.data
        })

class LicenseRetrieveAPIView(generics.RetrieveAPIView):
    queryset = License.objects.all()
    serializer_class = LicenseListSerializer

class LicenseUpdateAPIView(generics.UpdateAPIView):
    queryset = License.objects.filter(status=True)
    serializer_class = LicenseListSerializer


class ActivityListAPIView(generics.ListAPIView):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction, IntegrityError

from .models import License
from .serializers import LicenseSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction, IntegrityError

from .models import License
from .serializers import LicenseSerializer


class LicenseBulkCreateView(APIView):
    def post(self, request):
        data = request.data

        if not isinstance(data, list):
            return Response(
                {"error": "Ожидается массив объектов"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = LicenseSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)

        
        licenses = [LicenseSerializer().create(item) for item in serializer.validated_data]

 
        return Response(
            {"created": len(licenses)},
            status=status.HTTP_201_CREATED
        )


class LicenseDownloadView(View):
    def get(self, request, pk):
        try:
            lic = License.objects.get(pk=pk)
        except License.DoesNotExist:
            raise Http404("Лицензия не найдена")

        if not lic.document:
            raise Http404("Документ еще не сгенерирован")

        return FileResponse(
            lic.document.open("rb"),
            as_attachment=True,
            filename=os.path.basename(lic.document.name)
        )
    


class SendPINCode(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        org_inn = request.user.tin
        bearer_token = config('BEARER_TOKEN')

        try:
            auth_methods = get_auth_methods(token=bearer_token, person_idnp=org_inn)
            
            try:
                chosen_method = auth_methods["userAuthMethodList"][0]["authType"]
            except:
                return Response({'msg': auth_methods['errorMessage']}, status=auth_methods['errorCode'])
            
            send_pin_code(bearer_token, person_idnp=org_inn, method=chosen_method)
            
            return Response(status=200)
        except Exception as e:
            return Response({"msg": f"{e}"})
    

class CheckPINCode(APIView):
    def get(self, request):
        from apps.application.models import Application
        pincode = request.query_params.get('code')
        application_id = request.query_params.get('application_id')
        licenses = Application.objects.get(id=application_id).licenses.all()

        person_inn = request.user.tin
        bearer_token = config('BEARER_TOKEN')       
        hash = config('HASH') 
        user_token_response = get_user_token(token=bearer_token, person_idnp=person_inn, pin_code=pincode)
        
        try:
            return Response({'msg':user_token_response['errorMessage']}, status=user_token_response['errorCode'])
        except:    
            user_token = user_token_response["token"]
            sign_response = sign_hash(hash, user_token, bearer_token)
            licenses.update(signature=sign_response["sign"])

            return Response(sign_response)