from django.urls import path

from .views import ApplicationCreateView, ApplicationListView, ApplicationUpdateView, ApplicationDetailView, \
    ApplicationEmployeeCreate, AssignedApplicationsToEmployeeView, PaymentReceiptsCreateAPIView, ApplicationEmployeeUpdate, ApprovedRejectionView, ApprovedRejectionUpdateView, SignatureAPIView, ApprovedRejectionDetailView, ApplicationStatsView, ApplicationDocumentsDownloadAPIView, PaymentReceiptsDeleteAPIView


urlpatterns = [
    path('create-application/', ApplicationCreateView.as_view(), name='application'),
    path('list/', ApplicationListView.as_view(), name='list-applications'),
    path('detail/<int:pk>/', ApplicationDetailView.as_view(), name='detail-application'),
    path('update/<int:pk>/', ApplicationUpdateView.as_view(), name='update-application'),
    path(
        'set-employees/',
        ApplicationEmployeeCreate.as_view(),
        name='set-employees-to-application'
    ),
    path('update-employees/<int:pk>/', ApplicationEmployeeUpdate.as_view(), name='update-employees-to-application'),
    path('assigned-to-me/', AssignedApplicationsToEmployeeView.as_view()),
    path('upload-payment-receipts/', PaymentReceiptsCreateAPIView.as_view()),
    path('delete-payment-receipts/<int:pk>/', PaymentReceiptsDeleteAPIView.as_view()),
    path('approved-rejection/', ApprovedRejectionView.as_view()),
    path('update-approved-rejection/<int:pk>/', ApprovedRejectionUpdateView.as_view()),
    path('signature/', SignatureAPIView.as_view(), name="signature"),
    path('approved-rejection-detail/<int:pk>/', ApprovedRejectionDetailView.as_view()),
    path("stats/", ApplicationStatsView.as_view(), name="application-stats"),
    path(
        "<int:application_id>/documents/download/",
        ApplicationDocumentsDownloadAPIView.as_view(),
        name="application-documents-download"
    ),

]
