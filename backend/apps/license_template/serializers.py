from rest_framework import serializers
from django.db.models import IntegerField
from django.db.models.functions import Cast

from .models import LicenseTemplateField, LicenseTemplateFieldOrder, LicenseType, LicenseTemplate, \
    LicenseTemplateFieldValue, License, LicenseDefaults, Activity

from apps.application.models import Application
from .utils import render_license_to_docx

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__'

class LicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = License
        fields = (
            'id',
            'registration_number',
            'issued_date',
            'expiration_date',
            'license_type',
            'registrable_type',
            'application',
            'volume_ru',
            'volume_ky',
            'license_terms_ky',
            'license_terms_ru'
        )

    def create(self, validated_data):
        defaults = LicenseDefaults.objects.first()
        if defaults:
            last_license = (
                License.objects.annotate(
                    reg_num_int=Cast("registration_number", IntegerField())
                )
                .order_by("-reg_num_int")
                .first()
)
            # last_license = License.objects.order_by("-registration_number").first()
            default_license_number = defaults.license_number_start
            if last_license:
                last_license_number = int(last_license.registration_number)
                if last_license_number < default_license_number:
                    next_number = default_license_number + 1
                else:
                    next_number = last_license_number + 1
            else:
                next_number = defaults.license_number_start

            validated_data["registration_number"] = str(next_number)

        application = Application.objects.get(id=validated_data.get('application').id)
        validated_data['licensee_address'] = application.actual_address
        validated_data['inn'] = application.inn
        # validated_data['permitted_activity'] = application.
        return super().create(validated_data)

class LicenseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = License
        fields = '__all__'

    
class LicensePublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = License
        fields = 'registration_number', 'issued_date', 'expiration_date', 'volume', 'license_type', 'document', 'suspension'

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['license_type'] = LicenseTypeShortSerializer(instance.license_type).data['title']
        return repr

class LicenseTemplateFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenseTemplateField
        fields = (
            'id',
            'field_name',
            'field_type'
        )

    def to_representation(self, instance):
        repr = super().to_representation(instance)

        template = self.context.get('template')
        field_mapping = getattr(self, '_template_field_mapping', None)


        if field_mapping is None:
            field_mapping = {
                field.field_id: field
                for field in LicenseTemplateFieldOrder.objects.filter(template=template)
            }
            setattr(self, '_template_field_mapping', field_mapping)
        field = field_mapping.get(instance.id)

        if field:
            repr.update({
                'order': field.order,
                'is_required': field.is_required,
                'min_length': field.min_length,
                'max_length': field.max_length,
                'is_static': field.is_static,
                'description': field.description,
                'document_example': field.field.document_examples.first().document.url if
                field.field.document_examples.exists() else None
            })
        else:
            repr.update({
                'order': None,
                'is_required': None,
                'min_length': None,
                'max_length': None,
                'is_static': None,
                'description': None,
                'document_example': None
            })
        return repr

class LicenseTypeShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = LicenseType
        fields = ['id', 'title', 'detailed_description']

class LicenseTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = LicenseType
        fields = ['id', 'title', 'description','detailed_description',
            'license_terms','license_group']

    def to_representation(self, instance):
        repr_data = super().to_representation(instance)
        template = instance.templates.first()
        field_serializer = LicenseTemplateFieldSerializer(
            LicenseTemplateField.objects.filter(field_order__template=template),
            many=True,
            context={'template': template}
        )

        repr_data['fields'] = field_serializer.data
        return repr_data


class LicenseTemplateFieldValueSerializer(serializers.ModelSerializer):
    field_type = serializers.ReadOnlyField(source='field.field_type')

    class Meta:
        model = LicenseTemplateFieldValue
        fields = [
            'id',
            'application',
            'field',
            'field_type',
            'value',
            'license_type'
        ]


class LicenceTypeForApplicationEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenseType
        fields = (
            'id',
            'title'
        )