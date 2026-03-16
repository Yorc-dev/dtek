from django.contrib import admin
from .models import Application, ApplicationEmployee, ApprovedRejected
from apps.license_template.admin import LicenseTemplateFieldValueInline


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('pk', 'applicants_full_name', 'status', 'review_period')
    inlines = [LicenseTemplateFieldValueInline]


@admin.register(ApplicationEmployee)
class ApplicationEmployeeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'application')



# @admin.register(RejectionReasons)
# class RejectionReasonsAdmin(admin.ModelAdmin):
#     list_display = ('pk', 'text')
#     exclude = ('text',)


@admin.register(ApprovedRejected)
class ApprovedRejectedAdmin(admin.ModelAdmin):
    list_display = ('application','approved','rejected')
