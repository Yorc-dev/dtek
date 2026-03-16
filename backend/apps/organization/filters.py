import django_filters
from apps.license_template.models import License

class LicenseFilter(django_filters.FilterSet):
    # фильтры
    status = django_filters.BooleanFilter(field_name="status")  # активная/неактивная
    suspension = django_filters.BooleanFilter(field_name="suspension")  # приостановлена
    expired = django_filters.BooleanFilter(field_name="expired")  # аннулирована

    registration_number = django_filters.CharFilter(lookup_expr='icontains')
    inn = django_filters.CharFilter(lookup_expr='icontains')
    licensee_address = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = License
        fields = [
            'registration_number',
            'inn',
            'status',
            'suspension',
            'expired',
        ]