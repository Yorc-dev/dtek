from rest_framework import generics

from .models import Document, ApplicationDocumentTemplate
from .serializers import DocumentSerializer, ApplicationDocumentTemplateSerializer


class DocumentUploadView(generics.CreateAPIView):
    serializer_class = DocumentSerializer


class ApplicationDocumentTemplateCreate(generics.CreateAPIView):
    serializer_class = ApplicationDocumentTemplateSerializer


class ApplicationDocumentTemplateUpdate(generics.UpdateAPIView):
    serializer_class = ApplicationDocumentTemplateSerializer
    queryset = ApplicationDocumentTemplate.objects.all()


class ApplicationDocumentTemplateDelete(generics.DestroyAPIView):
    queryset = ApplicationDocumentTemplate.objects.all()


