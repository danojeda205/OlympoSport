# 📘 Guía de Estudio Completa: Modelos en Django

Esta guía unifica la teoría de modelos, tipos de campos y relaciones (incluyendo `through` en ManyToMany) para la preparación del examen.

## 1. Introducción a los Modelos

### ¿Qué es un Modelo?
Un modelo es la fuente definitiva de información sobre tus datos. Es una clase de Python que hereda de `django.db.models.Model`.
* Define la estructura de los datos almacenados.
* Django usa estos modelos para crear las tablas en la base de datos (ORM).

**Sintaxis básica:**
```python
from django.db import models

class Libro(models.Model):
   titulo = models.CharField(max_length=100)
   paginas = models.IntegerField()
```

## 2. Tipos de Campos (Field Types)

Es fundamental elegir el tipo de campo correcto para cada dato.

### Campos de Texto
* `CharField(max_length=...)`: Para cadenas cortas (ej. nombres, títulos). **Obligatorio** especificar `max_length`.
* `TextField()`: Para textos largos de longitud arbitraria (ej. descripciones, blogs).

### Campos Numéricos
* `IntegerField()`: Para números enteros.
* `FloatField()`: Para números con coma flotante.
* `DecimalField(max_digits=..., decimal_places=...)`: Para decimales con precisión fija. **Esencial para dinero**.
   * `max_digits`: Número total de dígitos (enteros + decimales).
   * `decimal_places`: Número de dígitos decimales.

### Campos de Fecha y Hora
* `DateField()`: Almacena solo la fecha (día, mes, año).
* `DateTimeField()`: Almacena fecha y hora exacta.

### Otros Campos Comunes
* `BooleanField()`: Almacena `True` o `False`.
* `FileField(upload_to=...)`: Para subir archivos.
* `ImageField(upload_to=...)`: Para subir imágenes (requiere librería Pillow).

## 3. Opciones Comunes de Campos (Field Options)

Estas opciones se pueden usar en la mayoría de los tipos de campos para controlar su comportamiento en la base de datos y en los formularios.

### `null` vs `blank`
* **`null=True`**: (Nivel Base de Datos)
    * Si es `True`, Django guardará valores vacíos como `NULL` en la base de datos.
    * Por defecto es `False`.
    * **Nota:** Evitar usar en campos de texto (`CharField`, `TextField`), ya que Django prefiere guardar una cadena vacía `""` en lugar de `NULL`.
* **`blank=True`**: (Nivel Validación/Formulario)
    * Si es `True`, el campo puede dejarse vacío en los formularios (ej. `admin` o `ModelForm`).
    * Si es `False` (por defecto), el campo es obligatorio.
    * **Combinación común:** `null=True, blank=True` (para campos opcionales en BD y formulario).

### `default`
* Establece un valor predeterminado para el campo.
* Puede ser un valor o un objeto invocable (función).
* Ejemplo: `fecha_creacion = models.DateTimeField(default=timezone.now)`

### `unique`
* **`unique=True`**:
    * Asegura que no haya dos registros con el mismo valor en este campo.
    * Crea un índice único en la base de datos.
    * Ejemplo: `email = models.EmailField(unique=True)` (para que no se repitan emails).

### `choices`
* Limita las opciones disponibles para un campo.
* Se usa con una lista de tuplas o una clase `TextChoices` / `IntegerChoices`.
* Ejemplo:
    ```python
    class Talla(models.TextChoices):
        PEQUENA = 'S', 'Pequeña'
        MEDIANA = 'M', 'Mediana'
    
    talla = models.CharField(max_length=1, choices=Talla.choices)
    ```

## 4. Validaciones (Validators y Clean)

Django ofrece dos formas principales de validar datos en los modelos: validadores de campo y el método `clean()`.

### A. Validadores (Validators)
Son funciones reutilizables que validan un **único campo**.
* Se definen fuera de la clase del modelo (normalmente).
* Si el dato es inválido, lanzan `ValidationError`.

**Ejemplo:** Validar que una fecha no sea futura.
```python
from django.core.exceptions import ValidationError
from django.utils import timezone

def validar_fecha_pasada(value):
    if value > timezone.now().date():
        raise ValidationError('La fecha no puede ser futura.')

class Evento(models.Model):
    # Se pasa la función (sin paréntesis) a la lista validators
    fecha = models.DateField(validators=[validar_fecha_pasada])
```

### B. Método `clean()`
Se usa para validaciones que involucran **múltiples campos** o lógica específica del modelo completo.
* Se define dentro de la clase del modelo.
* **Importante:** Django ejecuta `clean()` automáticamente en los ModelForms, pero **NO** cuando usas `save()` directamente en código o shell, a menos que llames a `full_clean()`.

**Ejemplo:** Validar que la hora de fin sea después de la de inicio.
```python
class Cita(models.Model):
    inicio = models.TimeField()
    fin = models.TimeField()

    def clean(self):
        # Validar coherencia entre dos campos
        if self.fin <= self.inicio:
            raise ValidationError('La hora de fin debe ser posterior al inicio.')
            
    # Opcional: Forzar validación al guardar (no estándar pero útil)
    def save(self, *args, **kwargs):
        self.full_clean() # Llama a clean() y validadores
        super().save(*args, **kwargs)
```

## 5. Relaciones entre Modelos

Django permite conectar modelos entre sí, simulando las relaciones de bases de datos relacionales.

### A. OneToOneField (Uno a Uno)
Relación 1 a 1 estricta. Un registro del modelo A se asocia con un solo registro del modelo B.
* **Uso:** Extender modelos existentes (ej. añadir datos a `User`).
* **Ejemplo:**
```python
class Perfil(models.Model):
   usuario = models.OneToOneField(User, on_delete=models.CASCADE)
   biografia = models.TextField()
```
* **Clave:** Si se borra el `User`, se borra el `Perfil` (por `CASCADE`).

### B. ForeignKey (Uno a Muchos)
Relación 1 a N. Un objeto pertenece a otro, pero el "padre" tiene muchos hijos.
* **Definición:** Se declara en el modelo "hijo" (el lado "Muchos").
* **Ejemplo:** Un autor tiene muchos libros.
```python
class Libro(models.Model):
   titulo = models.CharField(max_length=100)
   autor = models.ForeignKey(Autor, on_delete=models.CASCADE)
```
* **Acceso:**
    * `libro.autor`: Devuelve el objeto Autor.
    * `autor.libro_set.all()`: Devuelve todos los libros de ese autor.
* **`on_delete`:**
    * `CASCADE`: Borra los hijos si se borra el padre.
    * `SET_NULL`: Pone el campo en `NULL` (requiere `null=True`).
    * `PROTECT`: Impide borrar al padre si tiene hijos.

### C. ManyToManyField (Muchos a Muchos)
Relación N a N. Varios objetos de A se relacionan con varios de B.
* **Definición:** Se puede poner en cualquiera de los dos modelos.
* **Ejemplo:** Estudiantes y Cursos.
```python
class Estudiante(models.Model):
   cursos = models.ManyToManyField(Curso)
```
* **Internamente:** Django crea una tabla intermedia oculta (`estudiante_id`, `curso_id`).
* **Acceso:** `estudiante.cursos.all()` y `curso.estudiante_set.all()`.

## 6. ManyToMany Avanzado: Tabla Intermedia (`through`)

Cuando necesitamos guardar información sobre la relación (ej. nota, fecha de matrícula), la tabla automática de Django no sirve. Debemos crear una manualmente.

### Implementación
```python
# 1. Modelo Principal A
class Curso(models.Model):
   nombre = models.CharField(max_length=100)

# 2. Modelo Principal B (usa 'through')
class Estudiante(models.Model):
   nombre = models.CharField(max_length=100)
   cursos = models.ManyToManyField(Curso, through='Matricula')

# 3. Modelo Intermedio (Tabla 'through')
class Matricula(models.Model):
   estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
   curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
   
   # Campos extra de la relación
   fecha = models.DateField()
   nota = models.DecimalField(max_digits=4, decimal_places=2)

   class Meta:
       # Evita duplicados (mismo alumno en mismo curso 2 veces)
       unique_together = ('estudiante', 'curso')
```

### Diferencias Clave con ManyToMany normal
1. **No funciona `.add()`:**
    * `estudiante.cursos.add(curso)` -> **ERROR**.
    * **Razón:** Django no sabe qué valor poner en `fecha` o `nota`.
2. **Creación Manual:**
    * Hay que crear el objeto intermedio explícitamente:
    ```python
    Matricula.objects.create(estudiante=e1, curso=c1, fecha=hoy, nota=8.5)
    ```
3. **Consultas:**
    * Los accesos directos (`estudiante.cursos.all()`) siguen funcionando para leer.
    * Para leer la nota, consultas el modelo intermedio: `Matricula.objects.filter(estudiante=e1)`.

## 7. Resumen Rápido

| Relación | Cuándo usarla | Dónde se define |
| :--- | :--- | :--- |
| **OneToOne** | Extender un modelo (1-1). | En el modelo que "extiende". |
| **ForeignKey** | Padre-Hijo (1-N). | En el lado "Hijo" (el N). |
| **ManyToMany** | Grupos simples (N-N). | En cualquiera de los dos. |
| **M2M (through)** | Relación con datos extra (N-N). | En cualquiera, apuntando a modelo intermedio. |