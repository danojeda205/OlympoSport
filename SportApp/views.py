from django.shortcuts import render,get_object_or_404,redirect
from django.http import Http404

from SportApp.permissions import IsOwnerOrReadOnly
from .models import *
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView,TemplateView
from .forms import *
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
#=================================================================================================
from rest_framework import viewsets,permissions
from .serializers import EquipoSerializer, JugadorSerializer, PartidoSerializer

class StaffRequiredMixin(UserPassesTestMixin):# mixin para restringir acceso a usuarios staff
    def test_func(self):
        return self.request.user.is_staff

# Create your views here.

def inicio(request):
    return render(request, 'SportApp/inicio.html')

def ver_eventos(request):
    
    deporte_id_raw = request.GET.get('deporte')
    deporte_id = None
    
    # Si es un número, lo usamos, si es texto raro, lo ignoramos (deporte_id se queda en None)
    if deporte_id_raw and str(deporte_id_raw).isdigit():
        deporte_id = int(deporte_id_raw)
    
    
    deportes = Deporte.objects.order_by('nombre')
    
    #
    # Preparamos la superconsulta para evitar el n+1
    partidos_qs = Partido.objects.select_related(
        'torneo', 'torneo__deporte', 'equipo_local', 'equipo_visitante'
    )
    
    #  Aplicar filtro si es valido el deporte_id
    if deporte_id is not None:
        partidos_qs = partidos_qs.filter(torneo__deporte_id=deporte_id)# buscamos en la relacion atraves del torneo

    # Aqui agrupamos los partidos por deporte
    secciones = []
    
    if deporte_id is not None:
        # Un solo deporte
        deporte = deportes.filter(id=deporte_id).first()
        if deporte:
            # Ejecutamos la queri aqui al hacer list()
            secciones.append((deporte, list(partidos_qs.order_by('fecha_hora'))))
    else:
        # Todos los deportes
        # Ejecutamos una sola queri grande ordenada por deporte
        partidos = list(partidos_qs.order_by('torneo__deporte__nombre', 'fecha_hora'))
        
        # agrupamos los partidos por deporte usando un diccionario temporal
        partidos_por_deporte_id = {}
        for partido in partidos:
            # setdefault crea la lista si no existe y luego hace apend
            partidos_por_deporte_id.setdefault(partido.torneo.deporte_id, []).append(partido)

        # Reconstruimos la lista de secciones iterando sobre los deportes disponibles
        for deporte in deportes:
            partidos_del_deporte = partidos_por_deporte_id.get(deporte.id, [])
            #mostramos la sección si tiene partidos par aque no este vacio
            if partidos_del_deporte: 
                secciones.append((deporte, partidos_del_deporte))

    context = {
        'deportes': deportes,
        'deporte_seleccionado': deporte_id,
        'secciones': secciones,
    }

    return render(request, 'SportApp/ver_eventos.html', context)


@login_required
def detalle_evento(request, evento_pk):
    evento=get_object_or_404(Partido.objects.select_related('torneo','equipo_local','equipo_visitante'), pk=evento_pk)
    return render(request, 'SportApp/detalle_evento.html', {'evento': evento})


def actualizar_marcador(request, partido_id, accion):
    partido = get_object_or_404(Partido, pk=partido_id)
    
    if accion == 'local_sumar':
        partido.marcador_local += 1
    elif accion == 'local_restar' and partido.marcador_local > 0:
        partido.marcador_local -= 1
    elif accion == 'visitante_sumar':
        partido.marcador_visitante += 1
    elif accion == 'visitante_restar' and partido.marcador_visitante > 0:
        partido.marcador_visitante -= 1
        
    partido.save()
    
    # Redirigimos de vuelta al detalle del evento
    return redirect('detalle_evento', evento_pk=partido.id)

class EventoCreateView(StaffRequiredMixin, CreateView):
    model = Partido
    form_class = PartidoForm
    template_name = 'SportApp/añadir_evento.html'
    success_url = reverse_lazy('ver_eventos')


#----------------------CBVs Para jugadores -----------------------------------
class JugadorListView(LoginRequiredMixin, ListView):
    model = Jugador
    template_name = 'SportApp/jugador_lista.html'
    context_object_name = 'jugadores'
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Jugador.objects.select_related('equipo').order_by('equipo', 'dorsal')

        return Jugador.objects.filter(equipo__usuario=self.request.user).select_related('equipo').order_by('equipo', 'dorsal')

class JugadorDetailView(DetailView):
    model = Jugador
    template_name = 'SportApp/jugador_detalle.html'
    context_object_name = 'jugador'

class JugadorCreateView(LoginRequiredMixin, CreateView):
    model = Jugador
    form_class = JugadorForm
    template_name = 'SportApp/jugador_crear.html'
    success_url = reverse_lazy('jugador_lista')

    
    def get_form(self, form_class=None):#el form_class lo pasamos a None para que use el por defecto
        form = super().get_form(form_class)
        # En el desplegable 'equipo', solo muestro MIS equipos
        form.fields['equipo'].queryset = Equipo.objects.filter(usuario=self.request.user)
        return form

class JugadorUpdateView(LoginRequiredMixin, UpdateView):
    model = Jugador
    form_class = JugadorForm
    template_name = 'SportApp/jugador_crear.html'
    success_url = reverse_lazy('jugador_lista')
    
    def get_queryset(self):
        return Jugador.objects.filter(equipo__usuario=self.request.user)

class JugadorDeleteView(LoginRequiredMixin, DeleteView):
    model = Jugador
    template_name = 'SportApp/jugador_eliminar.html'
    success_url = reverse_lazy('jugador_lista')
    
    def get_queryset(self):
        return Jugador.objects.filter(equipo__usuario=self.request.user)


    
#----------------------CBVs Para equipos -----------------------------------
@login_required
def ver_equipo(request, equipo_id):
    equipo = get_object_or_404(Equipo, id=equipo_id)

    inscripciones=Inscripcion.objects.filter(equipo=equipo).select_related('torneo').order_by('torneo__nombre')
    return render(request, 'SportApp/ver_equipo.html', {'equipo': equipo,'inscripciones':inscripciones})

class EquipoListView(LoginRequiredMixin,ListView):
    model = Equipo
    def get_queryset(self):
        if self.request.user.is_staff:
            return Equipo.objects.annotate(num_jugadores=models.Count('jugadores')).order_by('nombre')

        queryset = Equipo.objects.filter(usuario=self.request.user)#nos quedamos con los equipos del usuario 

        queryset = queryset.annotate(num_jugadores=models.Count('jugadores'))#anotamos el numero de jugadores de cada equipo
        
        return queryset.order_by('nombre')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)#obtenemos el contexto original de la vista
        stats=self.get_queryset().aggregate(total_equipos=models.Count('id'))#con esto sabemos el nº de equipos que gestiona el usuario
        context['stats']=stats#añadimos las estadisticas al contexto
        return context
    

    template_name = 'SportApp/equipo_lista.html'
    context_object_name = 'equipos'
    ordering = ['deporte', 'nombre']

class EquipoCreateView(LoginRequiredMixin, CreateView):
    model = Equipo
    form_class = EquipoForm
    template_name = 'SportApp/equipo_crear.html'
    success_url = reverse_lazy('equipo_lista')
    
    def form_valid(self, form):
        form.instance.usuario=self.request.user#asignamos el usuario actual como propietario del equipo
        return super().form_valid(form)

class EquipoUpdateView(LoginRequiredMixin, UpdateView):
    model = Equipo
    form_class = EquipoForm
    template_name = 'SportApp/equipo_crear.html'
    success_url = reverse_lazy('equipo_lista')
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Equipo.objects.all()
        return Equipo.objects.filter(usuario=self.request.user)#solo permitimos editar equipos del usuario

class EquipoDeleteView(LoginRequiredMixin, DeleteView):
    model = Equipo
    template_name = 'SportApp/equipo_eliminar.html'
    success_url = reverse_lazy('equipo_lista')
    def get_queryset(self):
        if self.request.user.is_staff:
            return Equipo.objects.all()
        return Equipo.objects.filter(usuario=self.request.user)#solo permitimos eliminar equipos del usuario


#----------------------CBVs Para partidos-----------------------------------

class PartidoCreateView(StaffRequiredMixin, CreateView):
    model = Partido
    form_class = PartidoForm
    template_name = 'SportApp/partido_crear.html'
    success_url = reverse_lazy('ver_eventos') # Al crear, volvemos al calendario

    def form_valid(self,form):
        form.instance.usuario=self.request.user#asignamos el usuario actual como propietario del partido
        return super().form_valid(form)

class PartidoUpdateView(StaffRequiredMixin, UpdateView):
    model = Partido
    form_class = PartidoForm
    template_name = 'SportApp/partido_crear.html'
    
    def get_success_url(self):#sobreescribimos el metodo para redirigir al detalle del partido editado
        return reverse('detalle_evento', kwargs={'evento_pk': self.object.pk}) # Volvemos al detalle del partido editado

class PartidoDeleteView(StaffRequiredMixin, DeleteView):
    model = Partido
    template_name = 'SportApp/partido_eliminar.html'
    success_url = reverse_lazy('ver_eventos')
    

#----------------------CBVs Para TOrneo-----------------------------------

def TorneoDetail(request, pk):
    torneo = get_object_or_404(Torneo, pk=pk)
    
    #repito con select_related para optimizar la consulta. Ordeamos con el"-" para que primero salgon los top
    clasificacion=Inscripcion.objects.filter(torneo=torneo).select_related('equipo').order_by('-puntos_acumulados','equipo__nombre')
    context={
        'torneo': torneo,
        'clasificacion': clasificacion,
    }
    return render(request, 'SportApp/torneo_detalle.html', context)
class TorneoListView(ListView):
    model = Torneo
    template_name = 'SportApp/torneo_lista.html'
    context_object_name = 'torneos'
    ordering = ['deporte', 'nombre']

class TorneoCreateView(StaffRequiredMixin, CreateView):
    model=Torneo
    form_class=TorneoForm
    template_name='SportApp/torneo_crear.html'
    success_url=reverse_lazy('torneo_lista')

class TorneoUpdateView(StaffRequiredMixin, UpdateView):
    model = Torneo
    form_class = TorneoForm
    template_name = 'SportApp/torneo_crear.html'
    success_url = reverse_lazy('torneo_lista')

class TorneoDeleteView(StaffRequiredMixin, DeleteView):
    model = Torneo
    template_name = 'SportApp/torneo_eliminar.html'
    success_url = reverse_lazy('torneo_lista')


#----------------------CBVs Para Inscripcion-----------------------------------
class InscripcionCreateView(LoginRequiredMixin, CreateView):
    model=Inscripcion
    form_class=InscripcionForm
    template_name='SportApp/inscripcion_crear.html'
    success_url=reverse_lazy('equipo_lista')
    def form_valid(self, form):
        equipo=form.cleaned_data['equipo']
        if equipo.usuario != self.request.user:
            form.add_error('equipo', 'No puedes inscribir un equipo que no te pertenece.')
            return self.form_invalid(form)
        return super().form_valid(form)

class InscripcionUpdateView(LoginRequiredMixin, UpdateView):
    model = Inscripcion
    form_class = InscripcionForm
    template_name = 'SportApp/inscripcion_crear.html'
    success_url = reverse_lazy('equipo_lista')
    def get_queryset(self):
        return Inscripcion.objects.filter(equipo__usuario=self.request.user)#solo permitimos editar inscripciones de equipos del usuario
class InscripcionDeleteView(LoginRequiredMixin, DeleteView):
    model = Inscripcion
    template_name = 'SportApp/inscripcion_eliminar.html'
    success_url = reverse_lazy('equipo_lista')
    def get_queryset(self):
        return Inscripcion.objects.filter(equipo__usuario=self.request.user)#solo permitimos eliminar inscripciones de equipos del usuario
    




#----------------------CBVs Para Estadisticas de Partido-----------------------------------



#========================= Estadisticas Globales ==========================
class EstadisticaPartidoListView(LoginRequiredMixin, TemplateView):
    template_name = 'SportApp/estadisticas.html'
    
    def get_context_data(self, **kwargs):
        
        context=super().get_context_data(**kwargs)
        #añadimos el nombre del torneo al contexto para mostrarlo en la plantilla
        context['torneo']=self.request.GET.get('torneo')
        
        datos_globales=EstadisticaPartido.objects.aggregate(# creamos un diccionario con lo s siguientes totales calculados
                total_puntos=models.Sum('puntos'),
                total_minutos=models.Sum('minutos_jugados'),    
                partidos_jugados=models.Count('id',filter=models.Q(juega=True)),#filtramos aquellos ids que cumplan la condicion de juega
            )
        context['globales'] = datos_globales


        top_puntos=Jugador.objects.annotate(
            total_puntos=models.Sum('estadisticapartido__puntos')
            ).filter(total_puntos__gt=0).order_by('-total_puntos')[:5]# el uso del gt signfica greater than
        
        context['top_puntos']=top_puntos

        top_minutos=Jugador.objects.annotate(
            total_minutos=models.Sum('estadisticapartido__minutos_jugados')
            ).filter(total_minutos__gt=0).order_by('-total_minutos')[:5]
        
        context['top_minutos']=top_minutos
        
        
        
        top_participaciones=Jugador.objects.annotate(
            partidos_jugados=models.Count('estadisticapartido', filter=models.Q(estadisticapartido__juega=True))
            ).filter(partidos_jugados__gt=0).order_by('-partidos_jugados')[:5]
        
        context['top_participaciones']=top_participaciones
        
        return context








#========================= Estadisticas de partidos individuales ==========================


class EstadisticaPartidoPorPartidoListView(LoginRequiredMixin, ListView):
    model = EstadisticaPartido
    template_name = 'SportApp/estadisticas_partido.html'
    context_object_name = 'estadisticas'

    def dispatch(self, request, *args, **kwargs):
        self.partido = get_object_or_404(
            Partido.objects.select_related('torneo', 'equipo_local', 'equipo_visitante'),pk=kwargs.get('partido_pk'))
        return super().dispatch(request, *args, **kwargs)
    def get_queryset(self):
        return (# buscamos en todos los jugadores sus equipos, filtramos  y ordenamos , quedandonos asi con con los jugadores del partido al que consultamos correctamente
            EstadisticaPartido.objects.select_related('jugador', 'jugador__equipo')
            .filter(partido=self.partido)
            .order_by('jugador__equipo__nombre', 'jugador__dorsal', 'jugador__nombre')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['partido'] = self.partido
        return context


class EstadisticaPartidoCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = EstadisticaPartido
    form_class = EstadisticaPartidoForm
    template_name = 'SportApp/estadistica_form.html'

    def dispatch(self, request, *args, **kwargs):#con dispatch podemos capturar los parametros de la url antes de que se procese la vist y asi hacer cosas antes de cargar el formulario
        self.partido = None                     #tmb tenemos control total sobre la peticion, por ejemplo en este caso comprobamos si existe el partido
        partido_pk = kwargs.get('partido_pk')
        if partido_pk is not None:
            self.partido = get_object_or_404(
                Partido.objects.select_related('equipo_local', 'equipo_visitante', 'torneo'),pk=partido_pk)
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):#este solo fucniona cuando creamos una nueva estadistica desde un partido detalle, recuperamos la info y se rellena el campo partido
        initial = super().get_initial()
        if self.partido is not None:
            initial['partido'] = self.partido
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        if self.partido is not None:
            form.fields['partido'].queryset = Partido.objects.filter(pk=self.partido.pk)
            form.fields['jugador'].queryset = Jugador.objects.filter(
                equipo__in=[self.partido.equipo_local, self.partido.equipo_visitante]
            ).order_by('equipo__nombre', 'dorsal', 'nombre')

        return form

    def get_success_url(self):
        if self.partido is not None:
            return reverse('estadisticas_partido', kwargs={'partido_pk': self.partido.pk})
        return reverse('estadisticas')


class EstadisticaPartidoUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = EstadisticaPartido
    form_class = EstadisticaPartidoForm
    template_name = 'SportApp/estadistica_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        partido = self.object.partido
        form.fields['partido'].queryset = Partido.objects.filter(pk=partido.pk)
        form.fields['jugador'].queryset = Jugador.objects.filter(
            equipo__in=[partido.equipo_local, partido.equipo_visitante]
        ).order_by('equipo__nombre', 'dorsal', 'nombre')
        return form

    def get_success_url(self):
        return reverse('estadisticas_partido', kwargs={'partido_pk': self.object.partido.pk})


class EstadisticaPartidoDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = EstadisticaPartido
    template_name = 'SportApp/estadistica_eliminar.html'

    def get_success_url(self):
        return reverse('estadisticas_partido', kwargs={'partido_pk': self.object.partido.pk})
        


#========================== Vistas para las API's DE DRF  ==========================



class EquipoViewSet(viewsets.ModelViewSet):
    queryset = Equipo.objects.all()
    serializer_class = EquipoSerializer
    permission_classes=[IsOwnerOrReadOnly]

class JugadorViewSet(viewsets.ModelViewSet):
    queryset = Jugador.objects.all()
    serializer_class = JugadorSerializer
    permission_classes=[IsOwnerOrReadOnly]


class PartidoViewSet(viewsets.ModelViewSet):
    queryset = Partido.objects.all()
    serializer_class = PartidoSerializer
    permission_classes=[IsOwnerOrReadOnly]
    permission_classes=[permissions.IsAuthenticated]

