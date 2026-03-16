from rest_framework import serializers

from django.contrib.auth import get_user_model

from .models import Application, ApplicationEmployee, PaymentReceipt, ApprovedRejected

from apps.license_template.serializers import LicenseTemplateFieldValueSerializer, LicenceTypeForApplicationEmployeeSerializer, LicenseTypeShortSerializer
# from ..account.serializers import UserSerializer

User = get_user_model()

# class ReRegistrationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ReRegistration
#         fields = '__all__'



class PaymentReceiptGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentReceipt
        fields = ['id', 'document']


class PaymentReceiptPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentReceipt
        fields = '__all__'

class ApprovedRejectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovedRejected
        fields = '__all__'

class ApplicationListSerializer(serializers.ModelSerializer):
    license_type = LicenseTypeShortSerializer(many=True)
    approved_rejection = ApprovedRejectionSerializer(many=True, read_only=True)
    application_type_display = serializers.CharField(source='get_application_type_display', read_only=True)


    class Meta:
        model = Application
        fields = [
            'id',
            'inn',
            'organization_name',
            'applicants_full_name',
            'created_at',
            'review_period',
            'license_type',
            'status',
            'organization',
            "approved_rejection",
            'application_type_display',
            'application_type',
            'sedo_code',
            'cause'
        ]

class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'role', 'email']



class ApplicationSerializer(serializers.ModelSerializer):
    field_values = LicenseTemplateFieldValueSerializer(many=True, read_only=True)
    payment_receipts = PaymentReceiptGetSerializer(many=True, read_only=True)

    class Meta:
        model = Application
        fields = [
            'id',
            'license_type',
            'organization_name',
            'applicants_status',
            'email',
            'phone_number',
            'other_information',
            'applicants_full_name',
            'form_type',
            'ownership_form',
            'legal_address',
            'actual_address',
            'inn',
            'okpo_code',
            'register_date',
            'created_at',
            'owner_full_name',
            'date_of_signing',
            'review_period',
            'finish_date',
            'status',
            'field_values',
            'payment_receipts',
            'organization',
            'application_type',
            'cause',
            'author_id',
            ]
        read_only_fields = ['author_id']
        
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request.user, 'inn'):
            validated_data['organization'] = request.user

        if request and getattr(request.user, 'is_staff', False):
            validated_data['author'] = request.user
        else:
            validated_data.pop('author', None)

        return super().create(validated_data)
        
class ApplicationDetailSerializer(serializers.ModelSerializer):
    field_values = LicenseTemplateFieldValueSerializer(many=True, read_only=True)
    payment_receipts = PaymentReceiptGetSerializer(many=True, read_only=True)
    licenses = serializers.SerializerMethodField()
    assigned_employees = serializers.SerializerMethodField()


    class Meta:
        model = Application
        fields = [
            'id',
            'license_type',
            'organization_name',
            'applicants_status',
            'email',
            'phone_number',
            'other_information',
            'applicants_full_name',
            'form_type',
            'ownership_form',
            'legal_address',
            'actual_address',
            'inn',
            'okpo_code',
            'register_date',
            'created_at',
            'owner_full_name',
            'date_of_signing',
            'review_period',
            'finish_date',
            'status',
            'field_values',
            'payment_receipts',
            'assigned_employees',
            'application_type',
            'sedo_code',
            'cause',
            'licenses',
            'author_id',
            ]
        
    def get_licenses(self, obj):
        from apps.license_template.models import LicenseAction, License
        from apps.license_template.serializers import LicenseSerializer
        # Находим все LicenseAction, связанные с этой заявкой
        actions = LicenseAction.objects.filter(application=obj)
        print(actions)
        # Собираем все лицензии из них
        licenses = License.objects.filter(actions__in=actions).distinct()
        print(licenses)
        return LicenseSerializer(licenses, many=True).data
    
    def get_assigned_employees(self, obj):
        try:
            applicatione_employee = ApplicationEmployee.objects.get(application=obj.id)
            application_approved_rejected = ApprovedRejected.objects.filter(application=obj.id)
            ae = obj.employees.first()
            return {"id":applicatione_employee.id, "employees":UserShortSerializer(ae.employees.all(), many=True).data, "approved_or_rejected":ApprovedRejectionSerializer(application_approved_rejected, many=True).data}
        except:
            return {}


class ApplicationEmployeeSerializer(serializers.ModelSerializer):
    employees = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True
    )

    class Meta:
        model = ApplicationEmployee
        fields = '__all__'


class ApplicationsAssignedToEmployeeSerializer(serializers.ModelSerializer):
    license_type = LicenceTypeForApplicationEmployeeSerializer(many=True, read_only=True)

    class Meta:
        model = Application
        fields = '__all__'

# class RejectionReasonsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = RejectionReasons
#         fields = '__all__'
