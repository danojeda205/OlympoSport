
from django import forms
from django.core.exceptions import ValidationError
from .models import *


class JugadorForm(forms.ModelForm):
    class Meta:
        model = Jugador
        fields = '__all__'
        
        #para que se vea bonito en bootstrap
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del jugador'}),
            'dorsal': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 99}),
            'equipo': forms.Select(attrs={'class': 'form-select'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
        }

    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        palabras_prohibidas = ['admin', 'root', 'superuser', 'tonto']
        
        if nombre:
            for palabra in palabras_prohibidas:
                if palabra in nombre.lower():
                    raise ValidationError(f"El nombre '{nombre}' no está permitido.")
        return nombre

    def clean_dorsal(self):
        dorsal = self.cleaned_data.get('dorsal')
        if dorsal == 0:
                raise ValidationError("El dorsal 0 no es válido en esta liga.")
        return dorsal

# ---------------------------------------------------------
class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        exclude=['usuario'] # Excluir el campo 'usuario' del formulario

        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'entrenador': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'escudo': forms.FileInput(attrs={'class': 'form-control'}),
            'deporte': forms.Select(attrs={'class': 'form-select'}),
        }




# ---------------------------------------------------------
class TorneoForm(forms.ModelForm):
    class Meta:
        model =Torneo
        fields = '__all__'
        widgets={
            'deporte':forms.Select(attrs={'class':'form-select'}),
            'nombre':forms.TextInput(attrs={'class':'form-control'}),
            'temporada':forms.TextInput(attrs={'class':'form-control'}),
            'estado':forms.Select(attrs={'class':'form-select'}),
        }
# ---------------------------------------------------------
class PartidoForm(forms.ModelForm):
    class Meta:
        model=Partido
        exclude=['usuario'] # Excluir el campo 'usuario' del formulario
        fields=('torneo','fecha_hora','lugar','jornada','estado','equipo_local','equipo_visitante','marcador_local','marcador_visitante')
        widgets={
            'torneo':forms.Select(attrs={'class':'form-select'}),
            'fecha_hora':forms.DateTimeInput(attrs={'class':'form-control','type':'datetime-local'}),
            'lugar':forms.TextInput(attrs={'class':'form-control'}),
            'jornada':forms.TextInput(attrs={'class':'form-control'}),
            'estado':forms.Select(attrs={'class':'form-select'}),
            'equipo_local':forms.Select(attrs={'class':'form-select'}),
            'equipo_visitante':forms.Select(attrs={'class':'form-select'}),
            'marcador_local':forms.NumberInput(attrs={'class':'form-control'}),
            'marcador_visitante':forms.NumberInput(attrs={'class':'form-control'}),
        }
# ---------------------------------------------------------

class InscripcionForm(forms.ModelForm):
    class Meta:
        model=Inscripcion
        fields='__all__'
        widgets={
            'equipo':forms.Select(attrs={'class':'form-select'}),
            'torneo':forms.Select(attrs={'class':'form-select'}),
            'puntos_acumulados':forms.NumberInput(attrs={'class':'form-control'}),
            'fecha_inscripcion':forms.DateTimeInput(attrs={'class':'form-control','type':'datetime-local'}),
            'ha_pagado':forms.CheckboxInput(attrs={ 'class':'form-check-input'}),
        }


class EstadisticaPartidoForm(forms.ModelForm):
    class Meta:
        model = EstadisticaPartido
        fields = ('partido', 'jugador', 'juega', 'puntos', 'minutos_jugados', 'observaciones')
        widgets = {
            'partido': forms.Select(attrs={'class': 'form-select'}),
            'jugador': forms.Select(attrs={'class': 'form-select'}),
            'juega': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'puntos': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'minutos_jugados': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }