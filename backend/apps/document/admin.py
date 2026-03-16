from django.contrib import admin
from django import forms

from .models import Document, DocumentExample, ApplicationDocumentTemplate
from apps.license_template.choices import FieldType
from apps.license_template.models import LicenseTemplateField


class DocumentExampleForm(forms.ModelForm):
    class Meta:
        model = DocumentExample
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['field_id'].queryset = LicenseTemplateField.objects.filter(field_type=FieldType.DOCUMENT)


@admin.register(DocumentExample)
class DocumentExampleAdmin(admin.ModelAdmin):
    form = DocumentExampleForm
    list_display = ('pk', 'field_id')


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'document')


@admin.register(ApplicationDocumentTemplate)
class ApplicationDocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ('pk', 'field', 'template', 'application', 'document')
