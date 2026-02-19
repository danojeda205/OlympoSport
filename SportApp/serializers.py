from rest_framework import serializers
from .models import Equipo,Jugador,Partido


class EquipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipo
        fields = '__all__'

    def validate_nombre(self,value):
        if len(value) < 3:
            raise serializers.ValidationError("El nombre del equipo debe tener al menos 3 caracteres.")

        if value=="admin" or value=="Admin" or value=="ADMIN":
            raise serializers.ValidationError("El nommbre del equipo nunca puede  ser admin")


class JugadorSerializer(serializers.ModelSerializer):
    class Meta:
        model=Jugador
        fields='__all__'

    def validate_nombre(self,value):
        if len(value) < 2:
            raise serializers.ValidationError("El nombre del jugador debe tener al menos 2 caracteres.")
        if value=="admin" or value=="Admin" or value=="ADMIN":
            raise serializers.ValidationError("El nommbre del jugador nunca puede  ser admin")
        return value
    
    def validate(self, data):
        if data.get('dorsal') == 0:
            raise serializers.ValidationError({"dorsal": "El dorsal no puede ser 0."})
        return data


class PartidoSerializer(serializers.ModelSerializer):
    class Meta:
        model=Partido
        fields='__all__'

    def validate(self, data):
        if data["equipo__local"]==data["equipo__visitante"]:
            raise serializers.ValidationError("No puede jugar un equipo contra si mismo")
        return data