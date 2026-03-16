# import django_filters
from rest_framework import filters, views, generics, permissions, status
from rest_framework.permissions import IsAuthenticated
import io
import zipfile
import os
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView

from apps.application.models import Application
from apps.document.models import ApplicationDocumentTemplate

from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, OpenApiExample
from decouple import config
from django.contrib.postgres.search import TrigramSimilarity
from django_filters.rest_framework import DjangoFilterBackend


from apps.integration.gns import get_data_from_gns
from apps.integration.minust import get_data_from_minust
from apps.integration.encp import get_auth_methods, send_pin_code, get_user_token
from apps.organization.auth import OrganizationJWTAuthentication
from apps.account.choices import RoleChoices

from .filters import ApplicationFilter
from .models import Application, ApplicationEmployee, ApprovedRejected, PaymentReceipt
from .pagination import CombinedItemsPagination
from .serializer import ApplicationSerializer, ApplicationListSerializer, ApplicationEmployeeSerializer, \
    ApplicationsAssignedToEmployeeSerializer, PaymentReceiptPostSerializer, ApplicationDetailSerializer, ApprovedRejectionSerializer
from .choices import ApplicationStatusType

@extend_schema(
    tags=["Application"],
    description="Создание новой заявки. Позволяет пользователям подавать заявки на получение лицензий.",
    request=ApplicationSerializer,
    responses={201: ApplicationSerializer},
    examples=[
        OpenApiExample(
            "Пример запроса",
            value={
                "name": "Лицензия на торговлю",
                "application_type": 1,
                "license_type": 2
            },
            request_only=True
        ),
        OpenApiExample(
            "Пример ответа",
            value={
                "id": 1,
                "name": "Лицензия на торговлю",
                "application_type": "Торговая лицензия",
                "license_type": "Основная лицензия"
            },
            response_only=True
        ),
    ],
)
class ApplicationCreateView(generics.CreateAPIView):
    authentication_classes = [OrganizationJWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ApplicationSerializer
    queryset = Application.objects.prefetch_related('license_type')

    def create(self, request, *args, **kwargs):
        from apps.license_template.models import License, LicenseAction

        # Создаём сам объект Application
        response = super().create(request, *args, **kwargs)
        application_id = response.data.get("id")

        # Извлекаем параметры
        license_ids = request.query_params.get("license_id")
        license_numbers = request.query_params.get("license_number")

        # Проверяем наличие параметров
        if not license_ids and not license_numbers:
            return response

        # Пытаемся найти лицензию
        try:
            if license_ids:
                license_ids = license_ids.split(',') 
                print(license_ids)
            elif license_numbers:
                license_numbers = license_numbers.split(',')
                print(license_numbers)

            licenses = []

            if license_ids:
                licenses += list(License.objects.filter(id__in=license_ids))
            if license_numbers:
                licenses += list(License.objects.filter(registration_number__in=license_numbers))
        except License.DoesNotExist:
            return Response(
                {"detail": "Лицензия не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        application = Application.objects.get(id=application_id)
        license_action = LicenseAction.objects.create(
            application=application,
        )
        print(licenses)
        license_action.licenses.add(*licenses)

        return response

@extend_schema(
    tags=["Application"],
    description="Получение списка заявок с их текущим статусом и привязанной лицензией.",
    responses={200: ApplicationSerializer(many=True)},
    examples=[
        OpenApiExample(
            "Пример ответа",
            value=[
                {
                    "id": 1,
                    "name": "Лицензия на торговлю",
                    "status": "approved",
                    "license_type": "Основная лицензия"
                },
                {
                    "id": 2,
                    "name": "Лицензия на транспорт",
                    "status": "pending",
                    "license_type": "Дополнительная лицензия"
                }
            ],
            response_only=True
        ),
    ],
)
class ApplicationListView(generics.ListAPIView):
    serializer_class = ApplicationListSerializer
    queryset = Application.objects.all()
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = [
        'organization_name',
        'applicants_full_name',
        'created_at',
        'review_period',
    ]
    ordering = ['review_period']
    filterset_class = ApplicationFilter
    permission_classes = [IsAuthenticated]
    pagination_class = CombinedItemsPagination

    def get_queryset(self):
        queryset = super().get_queryset().filter(signature__isnull=False)
        search_query = self.request.GET.get('search', '')
        user = self.request.user 
        if hasattr(user, 'is_staff') and user.is_staff:
            if user.role == RoleChoices.DIRECTOR:
                queryset = super().get_queryset().filter(signature__isnull=False)
            else:
                # Остальные сотрудники видят только свои назначенные заявки
                assigned_app_ids = ApplicationEmployee.objects.filter(
                    employees=user
                ).values_list('application_id', flat=True)
                queryset = queryset.filter(id__in=assigned_app_ids)
        elif hasattr(user, "inn"):
            queryset = Application.objects.filter(organization=user)

        if search_query:
            return queryset.annotate(
                similarity=(
                    TrigramSimilarity('organization_name', search_query) +
                    TrigramSimilarity('applicants_full_name', search_query) +
                    TrigramSimilarity('inn', search_query)
                )
            ).filter(similarity__gt=0.3).order_by('-similarity')
        return queryset


@extend_schema(
    tags=["Application"],
    description="Обновление данных по заявке. Позволяет изменить информацию в уже поданной заявке.",
    request=ApplicationSerializer,
    responses={200: ApplicationSerializer},
    examples=[
        OpenApiExample(
            "Пример запроса",
            value={
                "name": "Лицензия на транспорт",
                "status": "approved"
            },
            request_only=True
        ),
        OpenApiExample(
            "Пример ответа",
            value={
                "id": 2,
                "name": "Лицензия на транспорт",
                "status": "approved",
                "license_type": "Дополнительная лицензия"
            },
            response_only=True
        ),
    ],
)
class ApplicationUpdateView(generics.UpdateAPIView):
    serializer_class = ApplicationSerializer
    queryset = Application.objects.all()


class ApplicationDetailView(generics.RetrieveAPIView):
    serializer_class = ApplicationDetailSerializer
    queryset = Application.objects.prefetch_related(
        'license_type',
        'field_values__field'
    )


class ApplicationEmployeeCreate(generics.CreateAPIView):
    serializer_class = ApplicationEmployeeSerializer


class ApplicationEmployeeUpdate(generics.UpdateAPIView):
    queryset = ApplicationEmployee.objects.all()
    serializer_class = ApplicationEmployeeSerializer


class AssignedApplicationsToEmployeeView(generics.ListAPIView):
    serializer_class = ApplicationsAssignedToEmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Application.objects.filter(
            employees__employees=user
        ).prefetch_related('license_type', 'field_values__field').distinct()



# class RejectionReasonsListView(generics.ListAPIView):
#     queryset = RejectionReasons.objects.all()
#     serializer_class = RejectionReasonsSerializer
#     permission_classes = [permissions.IsAuthenticated]

class PaymentReceiptsCreateAPIView(generics.CreateAPIView):
    serializer_class = PaymentReceiptPostSerializer
    permission_classes = [permissions.IsAuthenticated]


class PaymentReceiptsDeleteAPIView(generics.DestroyAPIView):
    queryset = PaymentReceipt.objects.all()
    serializer_class = PaymentReceiptPostSerializer
    permission_classes = [permissions.IsAuthenticated]

class ApprovedRejectionView(generics.CreateAPIView):
    serializer_class = ApprovedRejectionSerializer

class ApprovedRejectionDetailView(generics.RetrieveAPIView):
    queryset = ApprovedRejected.objects.all()
    serializer_class = ApprovedRejectionSerializer

class ApprovedRejectionUpdateView(generics.UpdateAPIView):
    queryset = ApprovedRejected.objects.all()
    serializer_class = ApprovedRejectionSerializer

class SignatureAPIView(views.APIView):
    def post(request, data):
        return Response("Вы подписали заявку")
    

# class Re_registrationAPIView(generics.CreateAPIView):
#     serializer_class = ReRegistrationSerializer
#     def create(self, request, *args, **kwargs):
#         from apps.license_template.models import License
#         license_id = request.query_params.get("license_id")
#         license_number = request.query_params.get("license_number")
#         if license_id:
#             license = License.objects.get(id=license_id)
#         elif license_number:
#             license = License.objects.get(license_number=license_number)
#         license.status = False 
#         return 


class ApplicationStatsView(views.APIView):
    permission_classes = [IsAuthenticated]  # если нужно ограничить доступ

    def get(self, request, *args, **kwargs):
        approved_count = Application.objects.filter(status=ApplicationStatusType.APPROVED).count()
        review_count = Application.objects.filter(status=ApplicationStatusType.REVIEW).count()

        return Response({
            "approved": approved_count,
            "review": review_count
        })
    



class ApplicationDocumentsDownloadAPIView(APIView):
    """
    Эндпоинт для скачивания всех документов, связанных с заявкой, в виде архива (.zip)
    """
    # permission_classes = [IsAuthenticated]

    def get(self, request, application_id):
        # Проверяем, что заявка существует
        application = get_object_or_404(Application, id=application_id)

        # Достаём все связанные шаблоны документов
        app_docs = ApplicationDocumentTemplate.objects.filter(application=application).select_related('document', 'field')

        # Если документов нет — возвращаем 404
        if not app_docs.exists():
            return HttpResponse("Нет документов, связанных с этой заявкой.", status=404)

        # Создаём архив в памяти
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for app_doc in app_docs:
                if app_doc.document and app_doc.document.document:
                    file_path = app_doc.document.document.path
                    if os.path.exists(file_path):
                        # красивое имя файла: поле_документ.pdf
                        field_name = app_doc.field.field_name if app_doc.field else "Без_поля"
                        base_name = os.path.basename(app_doc.document.document.name)
                        arc_name = f"{field_name}/{base_name}"
                        zip_file.write(file_path, arcname=arc_name)

        buffer.seek(0)

        # Создаём HTTP-ответ
        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/zip"
        )
        response['Content-Disposition'] = f'attachment; filename="application_{application_id}_documents.zip"'

        return response