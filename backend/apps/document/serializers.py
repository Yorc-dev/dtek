from urllib.parse import urlparse

from rest_framework import serializers

from .models import Document, ApplicationDocumentTemplate


class DocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        fields = ['id', 'document']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        parsed_url = urlparse(data['document'])
        data['document'] = parsed_url.path.lstrip('/')
        return data


class ApplicationDocumentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationDocumentTemplate
        fields = '__all__'

    def validate_field(self, value):
        if value and value.field_type != 'document':
            raise serializers.ValidationError(
                {
                    'field_type': f'field type for field: {value} must be document'
                }
            )
        return value
