from django.db import models
from django.utils.translation import gettext_lazy as _


class ApplicantsStatusType(models.IntegerChoices):
    INDIVIDUAL = 0, _('Физ. лицо')
    LEGAL_ENTITY = 1, _('Юр. лицо')

class ApplicationType(models.IntegerChoices):
    SUBMITTING = 0, _('Подача')
    RE_REGISTRATION = 1, _('Переоформление')
    REFUSAL = 2, _('Отказ')
    RENEWAL = 3, _('Продление')

class ApplicationStatusType(models.IntegerChoices):
    CREATED = 0, _('Создано')
    REVIEW = 1, _('Принято на рассмотрение')
    APPROVED = 2, _('Одобрено')
    DENIED = 3, _('отказано')

class ApplicationSendStatus(models.IntegerChoices):
    SENT = 0, _('Отправлено')
    NOT_SENT = 1, _('Не отправлено')
    PENDING = 2, _('В ожидании')

