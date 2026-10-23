from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Usuario


class RegistroCuentaSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate_email(self, value):
        return value.strip().lower()

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password2": "Las contraseñas no coinciden."}
            )
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        return Usuario.objects.create_user(
            username=validated_data["email"].lower(),
            email=validated_data["email"].lower(),
            first_name=validated_data["nombre"],
            password=validated_data["password"],
            rol="usuario",
        )
