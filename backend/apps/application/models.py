from django.db import models

from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField

from django_prometheus.models import ExportModelOperationsMixin

from apps.application.choices import ApplicantsStatusType, ApplicationStatusType, ApplicationSendStatus, ApplicationType
from apps.application.validators import PhoneValidator
from apps.organization.models import Organization

User = get_user_model()


class Application(
    ExportModelOperationsMixin('application'),
    models.Model
):
    phone_validator = PhoneValidator

    license_type = models.ManyToManyField(
    'license_template.LicenseType',
        related_name='applications',
        verbose_name=_('Тип лицензии'),
        blank=True
    )
    send_status = models.PositiveSmallIntegerField(
        _('Статус отправки'),
        choices=ApplicationSendStatus.choices,
        null=True, blank=True
        )
    organization_name = models.CharField(_('Название организации'), max_length=100)
    applicants_status = models.PositiveSmallIntegerField(
        _('Статус заявителя'),
        choices=ApplicantsStatusType.choices
    )
    email = models.EmailField(_('Почта'))
    phone_number = models.CharField(
        _('Номер телефона'),
        max_length=15,
        validators=[phone_validator]
    )
    other_information = models.TextField(_('Другие сведения'), blank=True, null=True)
    applicants_full_name = models.CharField(_('ФИО заявителя'), max_length=300)
    form_type = models.CharField(
        _('Организационно правовая форма'),
        max_length=10,
        blank=True,
        null=True)
    ownership_form = models.CharField(_('Форма собственности'), max_length=30)
    legal_address = models.CharField(_('Юридический адрес'), max_length=500)
    actual_address = models.CharField(_('Фактический адрес'), max_length=500)
    inn = models.CharField(
        _('ИНН'),
        validators=[
            MinLengthValidator(14),
            MaxLengthValidator(14)
    ])
    okpo_code = models.CharField(_('Код ОКПО'), max_length=10)
    register_date = models.DateTimeField(_('Дата регистрации юр.лица'), blank=True, null=True)
    created_at = models.DateTimeField(_('Дата заполнения'), auto_now_add=True)
    owner_full_name = models.CharField(_('ФИО руководителя'), max_length=300)
    date_of_signing = models.DateTimeField(
        _('Дата подписания заявки'),
        blank=True, null=True
    )
    review_period = models.DateTimeField(
        _('Срок рассмотрения'),
        null=True, blank=True)    # ToDo добавить сигнал или что то другое на постановку дедлайна в 30 дней
    finish_date = models.DateTimeField(
        _('Дата фактического рассмотрения'),
        blank=True, null=True
    )
    status = models.PositiveSmallIntegerField(
        _('Статус заявки'),
        choices=ApplicationStatusType.choices,
        null=True, blank=True
        )
    application_type = models.PositiveSmallIntegerField(
        _('Тип заявки'),
        choices=ApplicationType.choices,
        null=True, blank=True
        )
    is_archived = models.BooleanField(default=False)
    
    approved_by_director = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="approved_applications_as_director",
        verbose_name=_('Одобрено директором')
    )
    track_with_signal = True
    signature = models.CharField(_('Подпись'), max_length=500, blank=True, null=True)
    # documents = models.ManyToManyField(_('Документы на переоформление'), Document)
    sedo_code = models.CharField(_('Код с СЭД'), max_length=10, blank=True, null=True)
    cause = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list
    )
    doc = models.FileField(upload_to='applications/docs/', null=True, blank=True)

    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="applications",
        verbose_name=_('Организация')
    )
    def __str__(self) -> str:
        return f'{self.applicants_full_name}'

    class Meta:
        verbose_name = _('Заявка')
        verbose_name_plural = _('Заявки')

# class ReRegistration(models.Model):
#     from apps.license_template.models import License
#     application = models.ForeignKey(
#         Application,
#         on_delete=models.CASCADE,
#         related_name='reregistration',
#         verbose_name='Заявка')

#     license = models.ForeignKey(
#         License,
#         on_delete=models.CASCADE,
#         related_name='reregistration',
#         verbose_name='Лицензия')
    
class PaymentReceipt(models.Model):
    document = models.FileField(_('Чек об оплате'), upload_to='receipt/')
    application = models.ForeignKey(
        Application, 
        on_delete=models.CASCADE, 
        related_name='payment_receipts', 
        verbose_name= _('Заявка'))

class ApprovedRejected(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='approveds',
        verbose_name=_('Пользователь')
                             )
    approved = models.BooleanField(_('Подтверждение'),default=None, null=True)
    rejected = models.BooleanField(_('Отказ'),default=None, null=True)
    reason_for_refusal = models.TextField(_('Причина отказа'),blank=True, null=True)
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='approved_rejection',
        verbose_name=_('Заявка')
    )

    class Meta:
        verbose_name = _('Подтверждение и отказ')
        verbose_name_plural = _('Подтверждения и отказы')


class ApplicationEmployee(
    ExportModelOperationsMixin('application-employees'),
    models.Model
):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='employees',
        verbose_name=_('Заявка'),
        unique=True
    )
    employees = models.ManyToManyField(
        User,
        related_name='employees',
        verbose_name=_('Назначенные сотрудники'),
    )
    track_with_signal = True
    def __str__(self):
        return f'{self.application}'

    class Meta:
        verbose_name = _('Принятая на рассмотрение заявка')
        verbose_name_plural = _('Принятые на рассмотрение заявки')


# class RejectionReasons(models.Model):
#     text = models.CharField(max_length=100, verbose_name=_('Причина'))


#     class Meta:
#         verbose_name = _('Словарь')
#         verbose_name_plural = _('Словарь')