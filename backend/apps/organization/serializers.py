from rest_framework import serializers
from apps.integration.encp import get_auth_methods, send_pin_code, get_user_token, get_cert_info, sign_hash

from decouple import config

from .models import Organization
from apps.license_template.models import License
from apps.license_template.serializers import LicensePublicSerializer, LicenseListSerializer

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model=Organization
        fields="__all__"

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        request = self.context.get("request")
        user = getattr(request, "user", None)
        licenses = License.objects.filter(inn=instance.inn)
        if user and user.is_authenticated:
            license_serializer = LicenseListSerializer(licenses, many=True, context=self.context)
        else:
            license_serializer = LicensePublicSerializer(licenses, many=True, context=self.context)

        repr['licenses'] =license_serializer.data 
        return repr