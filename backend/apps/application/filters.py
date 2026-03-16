import django_filters

from apps.application.models import Application


class ApplicationFilter(django_filters.FilterSet):
    license_type = django_filters.BaseInFilter(field_name='license_type__id', lookup_expr='in')
    created_at = django_filters.NumberFilter(
        method='filter_by_created_year',
        label='Год создания'
    )
    class Meta:
        model = Application
        fields = ['id', 'status', 'license_type', 'application_type', 'created_at']

    def filter_by_created_year(self, queryset, name, value):
        return queryset.filter(created_at__year=value)
