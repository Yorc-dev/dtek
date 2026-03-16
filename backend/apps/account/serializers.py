from rest_framework import serializers

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class LogOutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(required=True, write_only=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password', )


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class ResetPasswordConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=10,
                                         write_only=True,
                                         required=True,
                                         )
    new_password_confirm = serializers.CharField(min_length=10,
                                                 write_only=True,
                                                 required=True,
                                                 )

    def validate(self, attrs):
        p1 = attrs.get('new_password')
        p2 = attrs.pop('new_password_confirm')

        if p2 != p1:
            raise serializers.ValidationError('Passwords didn\'t match')
        validate_password(password=p1)
        return attrs
