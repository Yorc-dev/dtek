from django.db import models

from django.utils.translation import gettext_lazy as _


class Organization(models.Model):
    name = models.CharField(_('Название'), max_length=500)
    inn = models.CharField(_('ИНН организации'), max_length=15, unique=True)
    representative = models.CharField(_('ИНН поручителя'), max_length=14)

    @property
    def is_authenticated(self):
        return True

    def __str__(self) -> str:
        return f'{self.name}'

    class Meta:
        verbose_name = _('Организация')
        verbose_name_plural = _('Организации')