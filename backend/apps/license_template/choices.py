from django.db import models
from django.utils.translation import gettext_lazy as _


class FieldType(models.IntegerChoices):
    TEXT = 0, _('Текст')
    NUMBER = 1, _('Число')
    BOOLEAN = 2, _('Булевое')
    DOCUMENT = 3, _('Документ')
    VOLUME = 4, _('Объем')


class LicenseStatusType(models.IntegerChoices):
    TEXT = 0, _('Одобренно')
    NUMBER = 1, _('Число')
    BOOLEAN = 2, _('Булевое')
