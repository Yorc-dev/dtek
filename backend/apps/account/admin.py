from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.contrib.auth.models import Group


from .models import User, UserResetPasswordToken


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput)
    first_name = forms.CharField(label='Имя')
    last_name = forms.CharField(label='Фамилия')

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'role', 'password1', 'password2', 'tin')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2


    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password1")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm

    list_display = ('pk', "email", 'role', "is_staff", "is_active")

    list_filter = ("is_staff", "is_superuser", "is_active")

    fieldsets = (
        ('Essentials', {"fields": ("email", 'tin', 'first_name', 'last_name', 'middle_name',
                                   'role',
                                   "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", 'tin', "password1", "password2", 'first_name', 'last_name', 'middle_name'),
        }),
    )

    search_fields = ("email", 'tin')
    ordering = ("email",)


# class UserResetPasswordAdmin(admin.ModelAdmin):
#     list_display = ['pk', 'user__email', 'reset_token', 'created_at']

admin.site.unregister(Group)

# admin.site.register(Service)
# admin.site.register(UserResetPasswordToken, UserResetPasswordAdmin)


# Axes
# try:
#     from axes.models import AccessAttempt, AccessLog, AccessFailureLog
#     for model in [AccessAttempt, AccessLog, AccessFailureLog]:
#         admin.site.unregister(model)
# except Exception:
#     pass

# # JWT Token Blacklist
# try:
#     from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
#     for model in [BlacklistedToken, OutstandingToken]:
#         admin.site.unregister(model)
# except Exception:
#     pass

# # Password History
# try:
#     from django_password_validators.password_history.models import PasswordHistory, Configuration
#     for model in [PasswordHistory, Configuration]:
#         admin.site.unregister(model)
# except Exception:
#     pass