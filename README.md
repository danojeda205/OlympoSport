[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=21998979&assignment_repo_type=AssignmentRepo)
º
# 🏆 Olympo Sport - Gestor de Eventos Deportivos

[![Django](https://img.shields.io/badge/Django-5.2.8-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-En%20Desarrollo-yellow?style=for-the-badge)]()

**Olympo Sport** es una plataforma web integral desarrollada en Django para la gestión y administración de competiciones deportivas. Diseñada para ser flexible, permite gestionar múltiples disciplinas deportivas, desde ligas de fútbol hasta torneos de tenis o baloncesto, adaptándose a sus sistemas de puntuación específicos.

---

## ✨ Características Principales

### 🏅 Gestión Multideporte
- Soporte para deportes de **Equipo** (Fútbol, Baloncesto) e **Individuales** (Tenis, Pádel).
- **Sistemas de Puntuación Adaptables**:
  - Goles (Fútbol, Balonmano)
  - Canastas/Puntos (Baloncesto)
  - Sets (Tenis, Voleibol, Pádel)
  - Puntos Genéricos

### 🏆 Administración de Torneos
- Creación de torneos por temporadas (ej. 2024/2025).
- **Estados del Torneo**: Inscripción Abierta, En Curso, Finalizado.
- **Clasificación Automática**: Tabla de posiciones generada dinámicamente basada en los puntos acumulados por los equipos inscritos.

### 👥 Gestión de Equipos y Jugadores
- **Equipos**: Perfiles completos con entrenador, ciudad y escudo.
- **Jugadores**: Fichas con dorsal, foto y asociación a equipos.
- **Validaciones**: Control lógico para asegurar que los equipos y jugadores correspondan al deporte del torneo.

### 📅 Calendario y Partidos
- Programación de partidos con fecha, hora, lugar y jornada.
- **Fases de Competición**: Fase Regular, Semifinales, Finales.
- **Estados del Partido**: Pendiente, Jugado, Suspendido.
- Registro de marcadores y estadísticas detalladas por partido.

### 🔒 Roles y Permisos
- **Vista Pública**: Acceso libre a calendarios, resultados, clasificaciones y detalles de equipos.
- **Panel de Staff**: Área restringida para administradores para crear, editar y eliminar registros (CRUD completo).

---

## 🗂️ Modelo de Datos

El sistema se basa en un modelo relacional robusto que garantiza la integridad de los datos:

- **Deporte**: Define las reglas básicas (tipo y puntuación).
- **Torneo**: La competición en sí misma.
- **Equipo/Jugador**: Los participantes.
- **Inscripción**: Tabla intermedia que vincula equipos a torneos y almacena la puntuación.
- **Partido**: Encuentros entre equipos dentro de un torneo.

![Diagrama E/R del Proyecto](OlympoSport.drawio%20(2).png)

---

## 🛠️ Tecnologías Utilizadas

- **Backend**: Python, Django 5.2.8
- **Base de Datos**: 
  - SQLite (Por defecto en desarrollo)
  - Compatible con MySQL (Librería `mysqlclient` incluida)
- **Imágenes**: Pillow (Gestión de escudos y fotos de jugadores)
- **Frontend**: HTML5, CSS3, Django Templates

---

## 🚀 Instalación y Puesta en Marcha

Sigue estos pasos para ejecutar el proyecto en tu entorno local:

### 1. Clonar el repositorio
```bash
git clone <url-del-repo>
cd proyectopersonal-xdojebal477-hub
```

### 2. Crear y activar un entorno virtual
Es recomendable usar un entorno virtual para aislar las dependencias.

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
Esto creará la estructura de la base de datos (SQLite por defecto).
```bash
python manage.py migrate
```

### 5. Crear un superusuario (Administrador)
Necesario para acceder al panel de administración y a las funciones de Staff.
```bash
python manage.py createsuperuser
```

### 6. Ejecutar el servidor de desarrollo
```bash
python manage.py runserver
```
Accede a la aplicación en: `http://127.0.0.1:8000/`

---

## 📖 Guía de Uso

### Para Usuarios (Público)
- Navega por la página de inicio para ver las últimas novedades.
- Accede a **"Eventos"** para ver el calendario de partidos, filtrando por deporte.
- Consulta la **"Clasificación"** dentro del detalle de cada torneo.
- Explora los perfiles de los **Equipos** y sus plantillas.

### Para Administradores (Staff)
- Inicia sesión con tu cuenta de superusuario.
- Aparecerán opciones de edición (botones de crear, editar, eliminar) en las diferentes secciones.
- Puedes gestionar:
  - Altas de nuevos deportes, torneos y equipos.
  - Inscripción de equipos en torneos.
  - Actualización de resultados de partidos y estados de torneos.

---

## 📂 Estructura del Proyecto

```
proyectopersonal/
├── OlympoSport/        # Configuración principal del proyecto (settings, urls)
├── SportApp/           # Aplicación principal
│   ├── migrations/     # Historial de cambios en la BD
│   ├── static/         # Archivos CSS, JS e imágenes estáticas
│   ├── templates/      # Plantillas HTML
│   ├── models.py       # Definición de datos
│   ├── views.py        # Lógica de negocio
│   └── urls.py         # Rutas de la aplicación
├── media/              # Archivos subidos por usuarios (escudos, fotos)
├── manage.py           # Script de gestión de Django
└── requirements.txt    # Lista de dependencias
```

---

## 🔮 Próximos Pasos

- [ ] Implementación de base de datos MySQL para producción.
- [ ] Sistema de autenticación para usuarios no-staff (aficionados).
- [ ] API REST con Django REST Framework.
- [ ] Generación de actas de partido en PDF.

---

## 📄 Licencia

Este proyecto es de uso educativo y personal.
