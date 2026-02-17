# 🏆 Olympo Sport - Gestor de Eventos Deportivos

[![Django](https://img.shields.io/badge/Django-5.2.8-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-En%20Desarrollo-yellow?style=for-the-badge)]()

**Olympo Sport** es una plataforma web integral desarrollada en Django para la gestión y administración de competiciones deportivas. Diseñada para ser flexible, permite gestionar múltiples disciplinas deportivas, desde ligas de fútbol hasta torneos de tenis o baloncesto, adaptándose a sus sistemas de puntuación específicos.

---

## ✨ Características Principales

### 🏅 Gestión Multideporte
- **Adaptabilidad Total**: Soporte para deportes de **Equipo** (Fútbol, Baloncesto) e **Individuales** (Tenis, Pádel).
- **Sistemas de Puntuación Personalizados**:
  - Goles (Fútbol, Balonmano)
  - Canastas/Puntos (Baloncesto)
  - Sets (Tenis, Voleibol, Pádel)
  - Puntos Genéricos
- **Validaciones Inteligentes**: El sistema impide mezclar equipos de diferentes deportes en un mismo torneo o partido.

### 📊 Dashboard de Estadísticas Avanzado
- **Visión Global y Filtrada**: Los usuarios visualizan estadísticas consolidadas (puntos totales, minutos jugados) filtradas automáticamente por los deportes en los que participan sus equipos.
- **Rankings de Rendimiento**:
  - Top Anotadores (MVP)
  - Top Jugadores por Minutos
  - Top Participaciones
- **Detalle por Partido**: Registro minucioso de estadísticas individuales (puntos, faltas, observaciones) por cada encuentro.

### 👥 Gestión de Clubes y Equipos (Usuario)
- **Autogestión**: Los usuarios registrados pueden crear y administrar sus propios **Equipos** y **Plantillas de Jugadores**.
- **Perfiles Completos**:
  - **Equipos**: Entrenador, ciudad, escudo personalizado.
  - **Jugadores**: Ficha técnica con dorsal, foto y vinculación histórica al equipo.

### 🏆 Competición y Torneos (Staff/Admin)
- **Organización de Torneos**: Creación de competiciones por temporadas (ej. 2024/2025) y estados (Inscripción, En Curso, Finalizado).
- **Gestión de Partidos**:
  - Programación de calendario (Fecha, Hora, Lugar, Jornada).
  - Definición de fases (Regular, Semifinal, Final).
  - Registro de resultados y cierre de actas.
- **Inscripciones**: Control de equipos participantes en cada torneo.

---

## 🗂️ Modelo de Datos

El sistema se basa en un modelo relacional robusto que garantiza la integridad de los datos:

- **Deporte**: Define las reglas del juego y puntuación.
- **Torneo**: La competición, contenedora de partidos e inscripciones.
- **Equipo/Jugador**: Entidades base gestionadas por los usuarios.
- **Inscripción**: Vinculación validada entre Equipos y Torneos.
- **Partido**: Encuentro deportivo con gestión de estados y fases.
- **EstadísticaPartido**: Desglose granular del rendimiento de cada jugador por partido.

![Diagrama E/R del Proyecto](OlympoSport.drawio%20(2).png)

---

## 🛠️ Tecnologías Utilizadas

- **Backend**: Python, Django 5.2.8
- **Base de Datos**: 
  - SQLite (Desarrollo simple)
  - Compatible con MySQL (Producción)
- **Gráficos e Imágenes**: Pillow (Procesamiento de escudos y fotos)
- **Frontend**: HTML5, CSS3, Django Templates (Diseño Responsive)


---

## 🚀 Instalación y Puesta en Marcha

Sigue estos pasos para ejecutar el proyecto en tu entorno local:

### 1. Clonar el repositorio
```bash
git clone <url-del-repo>
cd ut6-1proyectopersonal-xdojebal477-hub
```

### 2. Crear y activar un entorno virtual
Aisla las dependencias del proyecto.

**Windows:**
```bash
python -m venv env
.\env\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv env
source env/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Aplicar migraciones
Inicializa la base de datos (SQLite por defecto).
```bash
python manage.py migrate
```

### 5. Crear un superusuario (Administrador)
Necesario para acceder al panel de administración y funciones de Staff.
```bash
python manage.py createsuperuser
```

### 6. Ejecutar el servidor
```bash
python manage.py runserver
```
Accede a la aplicación en: `http://127.0.0.1:8000/`

---

## 📖 Guía de Uso y Roles

### 👤 Usuario Anónimo (Público)
- **Exploración**: Visualizar la página de inicio y novedades.
- **Calendario**: Consultar "Eventos" y filtrar partidos por deporte.
- **Clasificaciones**: Ver tablas de posiciones e información básica de equipos.

### 🛡️ Usuario Registrado (Manager de Club)
- **Mis Equipos**: Crear y editar el perfil de sus equipos (subir escudo, definir ciudad).
- **Plantilla**: Dar de alta jugadores, asignar dorsales y fotos.
- **Estadísticas**: Acceder al "Dashboard de Estadísticas" para ver el rendimiento acumulado de sus jugadores y competiciones.

### ⚙️ Administrador (Staff)
- **Gestión Total**: Acceso completo (CRUD) a todas las entidades desde el panel admin o vistas de gestión.
- **Torneos**: Crear nuevos torneos y abrir fases de inscripción.
- **Arbitraje**: Crear partidos, introducir resultados finales y rellenar actas de estadísticas.

---

## 📂 Estructura del Proyecto

```
proyectopersonal/
├── OlympoSport/        # Configuración principal (settings, urls)
├── SportApp/           # Aplicación Core
│   ├── migrations/     # Control de versiones de BD
│   ├── static/         # Assets (CSS, JS, Imágenes fijas)
│   ├── templates/      # Plantillas HTML (Vistas)
│   ├── models.py       # Definición de datos y lógica de validación
│   ├── views.py        # Controladores y lógica de negocio (CBVs)
│   └── urls.py         # Enrutador de la aplicación
├── media/              # Archivos subidos por usuarios (Dynamic content)
├── manage.py           # CLI de Django
└── requirements.txt    # Dependencias del proyecto
```

---

## 📄 Licencia

Este proyecto es de uso educativo y personal.
