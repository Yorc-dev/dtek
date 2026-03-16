from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.application.models import Application



class Decree(models.Model):
    number = models.PositiveIntegerField(_('Номер'))
    date_of_issue = models.DateField(_('Дата выдачи'))
    scan = models.FileField(_('Скан'), upload_to='decree_scan')

    
    aplication = models.OneToOneField(
        Application,
        on_delete=models.CASCADE,
        related_name='decree',
        verbose_name=_('Заявка')
    )

    class Meta:
        verbose_name = _('Приказ')
        verbose_name_plural = _('Приказы')

