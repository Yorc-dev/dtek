from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import DecreeViewSet, SendDocumentView

router = DefaultRouter()
router.register('', DecreeViewSet)

urlpatterns = [
    path("send-document/", SendDocumentView.as_view(), name="send-document"),
    path('', include(router.urls)),

]