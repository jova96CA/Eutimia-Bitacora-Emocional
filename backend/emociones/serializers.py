from rest_framework import serializers
from .models import Registro


class RegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registro
        fields = ["id", "fecha", "intensidad", "categoria", "texto_libre", "creado_en"]
        read_only_fields = ["id", "creado_en"]

    def validate_texto_libre(self, v):
        if len(v) > 200:
            raise serializers.ValidationError("Máximo 200 caracteres")
        return v
