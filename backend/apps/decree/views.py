from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404

from apps.application.models import Application
from .models import Decree
from .serializers import DecreeSerializer, DocumentUploadSerializer

class DecreeViewSet(viewsets.ModelViewSet):
    queryset = Decree.objects.all()
    serializer_class = DecreeSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_fields = ('aplication_id', )


class SendDocumentView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = DocumentUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data["file"]
            application_id = serializer.validated_data["application_id"]

            # достаем заявку
            application = get_object_or_404(Application, id=application_id)
            recipient_email = application.email

            # создаём письмо
            email = EmailMessage(
                subject="Документ по вашей заявке",
                body=f"Документ для заявки №{application_id}",
                from_email=None,  # возьмет DEFAULT_FROM_EMAIL
                to=[recipient_email]
            )
            email.attach(file.name, file.read(), file.content_type)
            email.send()

            return Response({"message": f"Документ отправлен на {recipient_email}"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)