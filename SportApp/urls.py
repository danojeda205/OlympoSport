from  django.urls import path
from . import views
urlpatterns = [

    path('', views.inicio, name='inicio'),
    path('eventos/', views.ver_eventos, name='ver_eventos'),
    path('eventos/<int:evento_pk>/', views.detalle_evento, name='detalle_evento'),
    path('añadir_evento/', views.EventoCreateView.as_view(), name='añadir_evento'),
    
    
    # URLs para Jugadores (CBV)
    path('jugadores/', views.JugadorListView.as_view(), name='jugador_lista'),
    path('jugadores/<int:pk>/', views.JugadorDetailView.as_view(), name='jugador_detalle'),
    path('jugadores/crear/', views.JugadorCreateView.as_view(), name='jugador_crear'),
    path('jugadores/<int:pk>/editar/', views.JugadorUpdateView.as_view(), name='jugador_editar'),
    path('jugadores/<int:pk>/eliminar/', views.JugadorDeleteView.as_view(), name='jugador_eliminar'),

    # URLs para Equipos (CBV)
    path('equipos/', views.EquipoListView.as_view(), name='equipo_lista'),
    path('equipos/<int:equipo_id>/', views.ver_equipo, name='ver_equipo'),
    path('equipos/crear/', views.EquipoCreateView.as_view(), name='equipo_crear'),
    path('equipos/<int:pk>/editar/', views.EquipoUpdateView.as_view(), name='equipo_editar'),
    path('equipos/<int:pk>/eliminar/', views.EquipoDeleteView.as_view(), name='equipo_eliminar'),

    # URLs para Partidos (CBV)
    path('partidos/crear/', views.PartidoCreateView.as_view(), name='partido_crear'),
    path('partidos/<int:pk>/editar/', views.PartidoUpdateView.as_view(), name='partido_editar'),
    path('partidos/<int:pk>/eliminar/', views.PartidoDeleteView.as_view(), name='partido_eliminar'),
    
    #urls ppara Torneos (CBV)
    path('torneos/', views.TorneoListView.as_view(), name='torneo_lista'),
    path('torneos/<int:pk>/', views.TorneoDetail, name='torneo_detalle'),
    path('torneos/crear/', views.TorneoCreateView.as_view(), name='torneo_crear'),
    path('torneos/<int:pk>/editar/', views.TorneoUpdateView.as_view(), name='torneo_editar'),
    path('torneos/<int:pk>/eliminar/', views.TorneoDeleteView.as_view(), name='torneo_eliminar'),
    
    # URLs para Inscripciones (CBV)
    path('inscripciones/crear/', views.InscripcionCreateView.as_view(), name='inscripcion_crear'),
    path('inscripciones/<int:pk>/editar/', views.InscripcionUpdateView.as_view(), name='inscripcion_editar'),
    path('inscripciones/<int:pk>/eliminar/', views.InscripcionDeleteView.as_view(), name='inscripcion_eliminar'),
    
    #Estadísticas de Partido
    path('estadisticas/',views.EstadisticaPartidoListView.as_view(), name='estadisticas'),
    path('estadisticas/crear/', views.EstadisticaPartidoCreateView.as_view(), name='estadistica_crear'),
    path('estadisticas/<int:pk>/editar/', views.EstadisticaPartidoUpdateView.as_view(), name='estadistica_editar'),
    path('estadisticas/<int:pk>/eliminar/', views.EstadisticaPartidoDeleteView.as_view(), name='estadistica_eliminar'),

    path('partidos/<int:partido_pk>/estadisticas/', views.EstadisticaPartidoPorPartidoListView.as_view(), name='estadisticas_partido'),
    path('partidos/<int:partido_pk>/estadisticas/crear/', views.EstadisticaPartidoCreateView.as_view(), name='estadistica_crear_partido'),
]