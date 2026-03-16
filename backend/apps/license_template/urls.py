from django.urls import path

from .views import LicenseTypeListView, LicenseTemplateFieldsCreateView, LicenseTemplateFieldValueUpdateView, LicenseCreateAPIView, ActivityListAPIView, LicenseListAPIView, LicenseBulkCreateView, LicenseTypeShortListAPIView, LicenseDownloadView, LicenseUpdateAPIView, LicenseRetrieveAPIView, SendPINCode, CheckPINCode

urlpatterns = [
    path('license/', LicenseCreateAPIView.as_view(), name='license'),
    path('create-license/', LicenseBulkCreateView.as_view()),
    path('licenses/', LicenseListAPIView.as_view(), name='licenses'),
    path('activities/', ActivityListAPIView.as_view(), name='activities'),
    path('license-type/', LicenseTypeListView.as_view(), name='license-type'),
    path('fill-license-fields/', LicenseTemplateFieldsCreateView.as_view(), name='fill-license-template-fields'),
    path('update-field-values/', LicenseTemplateFieldValueUpdateView.as_view(), name='update-fields'),
    path('license-type-short/', LicenseTypeShortListAPIView.as_view(), name='license-type-short'),
    path('<int:pk>/download/', LicenseDownloadView.as_view(), name='license-download'),
    path('license-update/<int:pk>/', LicenseUpdateAPIView.as_view(), name='license-update'),
    path('<int:pk>/', LicenseRetrieveAPIView.as_view(), name='license-detail'),
    path('send-code/', SendPINCode.as_view(), name='send-code'),
    path('check-pincode/', CheckPINCode.as_view(), name='check-pincode')
]
