from django.db import models
from django.core.exceptions import ValidationError # Para clean()
from django.core.validators import MinValueValidator, MaxValueValidator # Para validadores
from django.utils import timezone
from django.contrib.auth.models import User
# Create your models here.


class Deporte(models.Model):
    
    class TipoDeporte(models.TextChoices):
        EQUIPO = 'EQUIPO', 'Por Equipo'
        INDIVIDUAL = 'INDIVIDUAL', 'Individual'
    class SistemaPuntuacion(models.TextChoices):
        GOLES = 'GOLES', 'Goles (Fútbol, Balonmano)'
        CANASTAS = 'CANASTAS', 'Canastas/Puntos (Baloncesto)'
        SETS = 'SETS', 'Sets (Tenis, Voleibol,Padel)'
        PUNTOS = 'PUNTOS', 'Puntos Genéricos'

    nombre = models.CharField(max_length=100, unique=True, help_text="Ej: Fútbol, Tenis")
    
    tipo = models.CharField(
        max_length=20,
        choices=TipoDeporte.choices,
        default=TipoDeporte.EQUIPO,
        verbose_name="Tipo de Deporte"
    )
    
    sistema_puntuacion = models.CharField(
        max_length=20,
        choices=SistemaPuntuacion.choices,
        default=SistemaPuntuacion.PUNTOS,
        verbose_name="Sistema de Puntuación"
    )

    jugadores_por_equipo = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1, "Debe haber al menos 1 jugador")],
        help_text="Número de jugadores en campo por equipo"
    )

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()},{self.jugadores_por_equipo} jugadores)"



class Equipo(models.Model):

    usuario=models.ForeignKey(User,on_delete=models.CASCADE,related_name='equipos')


    nombre = models.CharField(max_length=100)
    entrenador = models.CharField(max_length=100, help_text="Nombre del entrenador principal")
    ciudad = models.CharField(max_length=100)
    
    # Pillow
    escudo = models.ImageField(upload_to='escudos/', null=True, blank=True)
    
    deporte = models.ForeignKey(Deporte, on_delete=models.CASCADE, related_name='equipos')

    def __str__(self):
        return f"{self.nombre} ({self.deporte.nombre})"

class Jugador(models.Model):
    
    nombre = models.CharField(max_length=100)
    dorsal = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(99)],
        help_text="Número entre 1 y 99",blank=True,null=True
    )
    foto = models.ImageField(upload_to='jugadores/', null=True, blank=True)
    
    
    equipo = models.ForeignKey(Equipo,on_delete=models.SET_NULL,null=True,blank=True,related_name='jugadores'
    )

    def __str__(self):
        return f"{self.nombre} (#{self.dorsal}) del {self.equipo.nombre  if self.equipo else 'Sin Equipo'} para la disciplina de {self.equipo.deporte.nombre if self.equipo else 'N/A'}"

class Torneo(models.Model):
    class EstadoTorneo(models.TextChoices):
        INSCRIPCION = 'INSCRIPCION', 'Inscripción Abierta'
        EN_CURSO = 'EN_CURSO', 'En Curso'
        FINALIZADO = 'FINALIZADO', 'Finalizado'

    nombre = models.CharField(max_length=150)
    temporada = models.CharField(max_length=50, help_text="Ej: 2024/2025")
    
    # Relación "Define"
    deporte = models.ForeignKey(Deporte, on_delete=models.PROTECT)#no se podra borrar un deporte si tiene torneos asociados
    
    
    estado = models.CharField(
        max_length=20,
        choices=EstadoTorneo.choices,
        default=EstadoTorneo.INSCRIPCION
    )
    
    # N:M explícita a través de 'Inscripcion'
    equipos = models.ManyToManyField(
        Equipo, 
        through='Inscripcion',
        related_name='torneos_inscritos'
    )

    def __str__(self):
        return f"{self.nombre} ({self.temporada})"


class Inscripcion(models.Model):
    torneo = models.ForeignKey(Torneo, on_delete=models.CASCADE)
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    
    
    fecha_inscripcion = models.DateField(auto_now_add=True)
    ha_pagado = models.BooleanField(default=False, verbose_name="¿Pagado?")
    puntos_acumulados = models.IntegerField(default=0, verbose_name="Puntos Clasificación")

    class Meta:
        unique_together = ('torneo', 'equipo')#evitamos duplicados
        verbose_name_plural = "Inscripciones"

    #Sobrescritura de clean() para validar a mi gusro
    def clean(self):
        super().clean()
        if self.equipo and self.torneo:
            # Validación Lógica: No mezclar deportes
            if self.equipo.deporte != self.torneo.deporte:
                raise ValidationError(
                    f"El equipo '{self.equipo.nombre}' juega a {self.equipo.deporte} "
                    f"y no puede inscribirse en un torneo de {self.torneo.deporte}."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    def __str__(self):
        return f"Inscripción de {self.equipo.nombre} en {self.torneo.nombre}"

class  Partido(models.Model):
    
    class EstadoPartido(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        JUGADO = 'JUGADO', 'Jugado / Finalizado'
        SUSPENDIDO = 'SUSPENDIDO', 'Suspendido'
        
    class FasePartido(models.TextChoices):
        REGULAR = 'REGULAR', 'Fase Regular'
        SEMIFINAL = 'SEMIFINAL', 'Semifinal'
        FINAL = 'FINAL', 'Final'

    usuario=models.ForeignKey(User,on_delete=models.CASCADE,related_name='partidos')

    torneo = models.ForeignKey(Torneo, on_delete=models.CASCADE, related_name='partidos')
    
    
    fecha_hora = models.DateTimeField()
    lugar = models.CharField(max_length=100)
    jornada = models.CharField(max_length=50, help_text="Ej: Jornada 1")
    
    
    estado = models.CharField(max_length=20,choices=EstadoPartido.choices,
        default=EstadoPartido.PENDIENTE
    )
    
    fase = models.CharField(max_length=20, choices=FasePartido.choices,
        default=FasePartido.REGULAR)

    # Relaciones 1:N (Local/Visitante) para que un equipo pueda ser local o visitante en varios partidos
    equipo_local = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='partidos_local')
    equipo_visitante = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='partidos_visitante')

    marcador_local = models.PositiveIntegerField(default=0)
    marcador_visitante = models.PositiveIntegerField(default=0)

    def clean(self):
        super().clean()
        if self.equipo_local and self.equipo_visitante:
            if self.equipo_local == self.equipo_visitante:
                raise ValidationError("Un equipo no puede jugar contra sí mismo.")
            
            if self.torneo:
                if self.equipo_local.deporte != self.torneo.deporte:
                    raise ValidationError("El equipo local no es del mismo deporte que el torneo.")
                if self.equipo_visitante.deporte != self.torneo.deporte:
                    raise ValidationError("El equipo visitante no es del mismo deporte que el torneo.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.equipo_local} vs {self.equipo_visitante} ({self.get_estado_display()})"


class EstadisticaPartido(models.Model):
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE, related_name='estadisticas')
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE)
    
    
    puntos = models.PositiveIntegerField(default=0, verbose_name="Goles/Puntos/Canastas/Asistencias")
    
    
    observaciones = models.TextField(blank=True, null=True, help_text="Incidencias, MVP, etc.")
    
    minutos_jugados = models.PositiveIntegerField(default=0,null=True,blank=True)
    
    juega = models.BooleanField(default=False)

    class Meta:
        unique_together = ('partido', 'jugador')
        verbose_name = "Estadística de Jugador"
        verbose_name_plural = "Estadísticas de Partido"

    def clean(self):
        super().clean()
        if self.partido and self.jugador:
            ids_equipos_partido = [self.partido.equipo_local_id, self.partido.equipo_visitante_id]
            if self.jugador.equipo_id not in ids_equipos_partido:#esta validacion asegura que el jugador pertenece a uno de los equipos que juegan el partido
                raise ValidationError(f"El jugador {self.jugador} no pertenece a los equipos que juegan este partido.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"Estadísticas de {self.jugador.nombre} en el partido {self.partido}"