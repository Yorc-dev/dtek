from django.urls import path

from .views import GNSInnView, MinustInnView, CheckPINCodeView, OrganizationListAPIView, OrganizationTokenRefreshView, RevokeOrganizationLicensesView


urlpatterns = [
    path('gns/', GNSInnView.as_view(), name='test_gns_integration'),
    path('minust/', MinustInnView.as_view(), name='test_minust_integration'),
    path('check-pin-code/', CheckPINCodeView.as_view()),
    path('organizations/', OrganizationListAPIView.as_view()),
    path("refresh/", OrganizationTokenRefreshView.as_view(), name="org_token_refresh"),
    path(
        "revoke-organization-licenses/",
        RevokeOrganizationLicensesView.as_view(),
        name="revoke-organization-licenses",
    ),
]