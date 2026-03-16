from django.core.mail import send_mail

from decouple import config

FROM_EMAIL = config('FROM_EMAIL')

def send_reset_password_email(email, reset_token):
    link = f'https://dfec.yorc.org/password-reset/?token={reset_token}'
    send_mail(
        subject='Сброс пароля',
        message=f'Для сброса пароля, вам требуется перейти по ссылке ниже и ввести новый пароль\n{link}',
        from_email=FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False
    )
