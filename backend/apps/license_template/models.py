from django.db import models
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField

from django_prometheus.models import ExportModelOperationsMixin

from apps.license_template.choices import FieldType
from apps.application.models import Application

class Activity(models.Model):
    text = models.CharField(max_length=100, verbose_name=_('Деятельность'))
    license_type = models.ForeignKey('LicenseType', on_delete=models.CASCADE, related_name="activities", blank=True, null=True)

    class Meta:
        verbose_name = _('Деятельностей')
        verbose_name_plural = _('Деятельности')


class LicenseDefaults(models.Model):
    license_number_start = models.PositiveIntegerField(
        default=1,
        verbose_name="Начальный номер лицензии (без нулей)"
    )

    def __str__(self):
        return "Дефолтные значения для лицензий"
    
    class Meta:
        verbose_name = "Значения по умолчанию для лицензии"
        verbose_name_plural = "Значения по умолчанию для лицензий"


class License(models.Model):
    REGISTRATION_NUMBER_LENGTH = 20
    INN_LENGTH = 14

    REGISTRABLE_TYPES = [
        (0, _("Отчуждаемая")),
        (1, _("Неотчуждаемая")),
    ]

    STATUS_CHOICES = [
        (0, _("Активна")),
        (1, _("Неактивна")),
    ]

    registration_number = models.CharField(
        max_length=REGISTRATION_NUMBER_LENGTH,
        verbose_name="Регистрационный номер по реестру лицензий",
        blank=True,
        null=True
    )
    issued_date = models.DateField(verbose_name="Дата выдачи")
    issued_by = models.CharField(max_length=255, verbose_name="Выдана")

    licensee_address = models.TextField(verbose_name="Адрес лицензиата")

    state_registration_certificate = models.CharField(
        max_length=255,
        verbose_name="Свидетельство о государственной регистрации"
    )
    state_registration_issued_by = models.CharField(
        max_length=255,
        verbose_name="Кем выдана государственная регистрация"
    )

    inn = models.CharField(
        max_length=INN_LENGTH,
        verbose_name="Идентификационный код (ИНН)"
    )

    license_type = models.ForeignKey(
        'LicenseType',
        on_delete=models.CASCADE,
        related_name='licenses',
        verbose_name=_('Тип лицензии')
    )
    expiration_date = models.DateField(
        verbose_name="Срок действия лицензии",
        blank=True,
        null=True,
        help_text="Если лицензия бессрочная — оставьте поле пустым"
    )
    expired = models.BooleanField(
        max_length=10,
        default=False,
        verbose_name="Анулировано"
    )
    registrable_type = models.IntegerField(
        choices=REGISTRABLE_TYPES,
        verbose_name="Лицензия является"
    )


    status = models.BooleanField(
        max_length=10,
        default=True,
        verbose_name="Статус"
    )
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='licenses',
        verbose_name='Заявка')
    
    volume = models.CharField(max_length=200, verbose_name='Объем', blank=True, null=True)
    license_terms = models.TextField(verbose_name="Лицензионные условия", blank=True, null=True)

    document = models.FileField(upload_to='licenses/docs/', null=True, blank=True)
    direct_aproved = models.BooleanField(default=False)
    suspension = models.BooleanField(default=False)
    suspension_date = models.DateField(blank=True, null=True)
    signature = models.CharField(_('Подпись'),max_length=6000, blank=True, null=True)
    class Meta:
        verbose_name = "Лицензия"
        verbose_name_plural = "Лицензии"


    def __str__(self):
        return f"Лицензия {self.registration_number} — {self.status}"

    


class LicenseType(
    ExportModelOperationsMixin('license-type'),
    models.Model
):
    LICENSE_GROUP = [
        (0, _("Тепловая энергия")),
        (1, _("Электрическая энергия")),
        (2, _("Нефть")),
        (3, _("Газ"))]
    REGISTRABLE_TYPES = [
        (0, _("Отчуждаемая")),
        (1, _("Неотчуждаемая")),
    ]
    title = models.CharField(_('Название'), max_length=200)
    description = models.TextField(_('Описание'), blank=True)
    detailed_description = HTMLField(_('Описание в справочнике'), blank=True)

    license_group = models.IntegerField(
        choices=LICENSE_GROUP,
        verbose_name="Группа лицензии",
        blank=True,
        null=True
    )
    expiration_date = models.DateField(
        verbose_name="Срок действия лицензии",
        blank=True,
        null=True,
        help_text="Если лицензия бессрочная — оставьте поле пустым"
    )
    license_type = models.IntegerField(
        choices=REGISTRABLE_TYPES,
        verbose_name="Лицензия является"
    )
    license_terms = models.TextField(verbose_name="Лицензионные условия")



    def __str__(self) -> str:
        return f'{self.title}'

    class Meta:
        verbose_name = _('Тип лицензии')
        verbose_name_plural = _('Типы лицензий')


class LicenseTemplate(
    ExportModelOperationsMixin('license-template'),
    models.Model
):
    name = models.CharField(_('Название шаблона лицензии'), max_length=30)
    license_type = models.ForeignKey(
        LicenseType,
        on_delete=models.CASCADE,
        related_name='templates',
        verbose_name=_('Тип лицензии')
    )

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = _('Шаблон лицензии')
        verbose_name_plural = _('Шаблоны лицензий')


class LicenseTemplateField(
    ExportModelOperationsMixin('license-template-field'),
    models.Model
):
    field_name = models.CharField(_('Название поля'), max_length=150)
    field_type = models.PositiveSmallIntegerField(_('Тип данных поля'), choices=FieldType.choices)

    def __str__(self):
        return f'{self.field_name}'

    class Meta:
        verbose_name = _('Поле шаблона лицензии')
        verbose_name_plural = _('Поля шаблонов лицензий')


class LicenseTemplateFieldValue(
    ExportModelOperationsMixin('license-template-field-value'),
    models.Model
):
    application = models.ForeignKey(
        'application.Application',
        on_delete=models.CASCADE,
        related_name='field_values',
        verbose_name=_('Заявка')
    )
    field = models.ForeignKey(
        LicenseTemplateField,
        on_delete=models.CASCADE,
        related_name='field_values',
        verbose_name=_('Поле')
    )
    value = models.TextField(_('Значение'), null=True, blank=True)
    license_type = models.ForeignKey(
        LicenseType,
        on_delete=models.CASCADE,
        related_name='field_values',
        verbose_name=_('Тип лицензии')
    )

    def __str__(self):
         return f'{self.application.id} - {self.field.field_name}'

    class Meta:
        verbose_name = _('Значение поля шаблона лицензии')
        verbose_name_plural = _('Значения полей шаблонов лицензий')


class LicenseTemplateFieldOrder(
    ExportModelOperationsMixin('license-template-field-order'),
    models.Model
):
    template = models.ForeignKey(
        LicenseTemplate,
        on_delete=models.CASCADE,
        related_name='field_order',
        verbose_name=_('Шаблон')
    )
    field = models.ForeignKey(
        LicenseTemplateField,
        on_delete=models.CASCADE,
        related_name='field_order',
        verbose_name=_("Поля")
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_("Порядок"))
    is_required = models.BooleanField("Обязательное поле", default=False)
    min_length = models.PositiveIntegerField("Минимальное значение", blank=True, null=True)
    max_length = models.PositiveIntegerField("Максимальное значение", blank=True, null=True)
    is_static = models.BooleanField(_('Статичное поле'), default=False)
    description = models.TextField(_('Описание для поля'), blank=True, null=True)

    class Meta:
        verbose_name = _("Порядок полей шаблона лицензии")
        verbose_name_plural = _("Порядок полей шаблона лицензии")
        unique_together = ('template', 'field')
        ordering = ['order']

    def __str__(self):
        return f"{self.template} - {self.field} (Order: {self.order})"
    

class LicenseAction(models.Model):
    licenses = models.ManyToManyField(
        'license_template.License',
        related_name='actions',
        verbose_name=_('Лицензии')
    )

    application = models.ForeignKey(
        Application,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='license_actions',
        verbose_name=_('Заявка')
    )


class ExcelImport(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Импорт Excel"
        verbose_name_plural = "Импорт Excel"
        managed = False  # таблица не создаётся в БД
