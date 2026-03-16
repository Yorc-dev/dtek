from django.core import validators
from django.utils.translation import gettext_lazy as _

PhoneValidator = validators.RegexValidator(
    r"^996\d{9}$",
    message=_(
        "Номер телефона должен быть заполнен в формате: 996*********** Разрешено до 9 символов после кода страны."
    ),
)