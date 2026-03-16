from django.db import models
from django.utils.translation import gettext_lazy as _

from django_prometheus.models import ExportModelOperationsMixin

from apps.license_template.models import LicenseTemplateField, LicenseTemplate
from apps.application.models import Application


class DocumentExample(ExportModelOperationsMixin('document-example'), models.Model):
    field_id = models.ForeignKey(
        LicenseTemplateField,
        on_delete=models.CASCADE,
        related_name='document_examples',
        verbose_name=_('Поле к которому нужно прикрепить пример документа')
    )
    document = models.FileField(_('Пример документа'), upload_to='document-examples/')

    def __str__(self) -> str:
        return f'{self.field_id.field_name}'

    class Meta:
        verbose_name = _('Пример документа')
        verbose_name_plural = _('Примеры документов')


class Document(ExportModelOperationsMixin('document'), models.Model):
    document = models.FileField(_('Документ'), upload_to='documents/')

    class Meta:
        verbose_name = _('Документ')
        verbose_name_plural = _('Документы')


class ApplicationDocumentTemplate(ExportModelOperationsMixin('application-document-template'), models.Model):  # ToDo Продумать удаление документа при удалении его шаблона
    field = models.ForeignKey(
        LicenseTemplateField,
        on_delete=models.SET_NULL,
        null=True,
        related_name='document_templates',
        verbose_name=_('Поле')
    )
    template = models.ForeignKey(
        LicenseTemplate,
        on_delete=models.SET_NULL,
        null=True,
        related_name='document_templates',
        verbose_name=_('Шаблон')
    )
    application = models.ForeignKey(
        Application,
        on_delete=models.SET_NULL,
        null=True,
        related_name='document_templates',
        verbose_name=_('Заявка')
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        related_name='document_templates',
        verbose_name=_('Документ')
    )

    class Meta:
        verbose_name = _('Шаблон документа')
        verbose_name_plural = _('Шаблоны документов')
