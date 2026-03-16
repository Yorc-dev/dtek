import uuid
from datetime import timedelta

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from django_prometheus.models import ExportModelOperationsMixin

from .choices import RoleChoices
from .manager import UserManager


# class Service(
#     ExportModelOperationsMixin('services'),
#     models.Model
# ):    # ToDo Удалить
#     title = models.CharField(_('Название услуги'), max_length=100)

#     def __str__(self):
#         return f'{self.title}'


class User(
    ExportModelOperationsMixin('users'),
    AbstractUser
):
    email = models.EmailField(_('email'), unique=True)
    first_name = models.CharField(_('Имя'), max_length=150)
    last_name = models.CharField(_('Фамилия'), max_length=150)
    middle_name = models.CharField(
        _('Отчество'),
        max_length=150,
        blank=True,
        null=True
    )
    role = models.PositiveSmallIntegerField(
        _('Роль сотрудника'), blank=True, null=True,
        choices=RoleChoices.choices
    )
    # service = models.ForeignKey(
    #     Service,
    #     on_delete=models.SET_NULL,
    #     related_name='users',
    #     null=True,
    #     verbose_name=_('Услуга')
    # )
    is_active = models.BooleanField(_('Статус сотрудника'), default=True)
    username = None
    encrypted_fields = ['first_name', 'last_name', 'middle_name']
    tin = models.CharField(_('ИНН'), max_length=15, blank=True, null=True)

    def __str__(self) -> str:
        return f'{self.email}'

    class Meta:
        verbose_name = _('Сотрудник')
        verbose_name_plural = _('Сотрудники')

    objects = UserManager()

    REQUIRED_FIELDS = []
    USERNAME_FIELD = "email"


class UserResetPasswordToken(
    ExportModelOperationsMixin('reset tokens'),
    models.Model
):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Сотрудник'))
    reset_token = models.UUIDField(_('Токен для сброса'), default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)

    def is_valid(self):
        return self.created_at >= timezone.now() - timedelta(minutes=10)

    class Meta:
        verbose_name = _('Токен для восстановления пароля')
        verbose_name_plural = _('Токены для восстановления пароля')
