from django.urls import path

from .views import DocumentUploadView, ApplicationDocumentTemplateCreate, ApplicationDocumentTemplateUpdate, \
    ApplicationDocumentTemplateDelete

urlpatterns = [
    path(
        'upload/',
        DocumentUploadView.as_view(),
        name='document-upload'
    ),
    path(
        'document-template-create/',
        ApplicationDocumentTemplateCreate.as_view(),
        name='document-template-create'
    ),
    path(
        'document-template-update/<int:pk>/',
        ApplicationDocumentTemplateUpdate.as_view(),
        name='document-template-update'
    ),
    path(
        'document-template-delete/<int:pk>/',
        ApplicationDocumentTemplateDelete.as_view(),
        name='document-template-delete'
    )
]