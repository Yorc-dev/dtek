from django.db import models
from django.utils.translation import gettext_lazy as _


class RoleChoices(models.IntegerChoices):
    DIRECTOR = 0, _('Директор')
    HEAD_OF_DEPARTMENT = 1, _('Начальник управления')
    SPECIALIST = 2, _('Специалист')
    GENERAL_DEPARTMENT = 3, _('Общий отдел')
