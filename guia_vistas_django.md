# GUÍA COMPLETA DE VISTAS EN DJANGO — Olympo Sport

---

## PARTE 1: LOS DOS PARADIGMAS — FBV vs CBV

En Django hay dos formas de escribir vistas:

### FBV (Function-Based View) — Vista basada en función
```python
def inicio(request):
    return render(request, 'SportApp/inicio.html')
```
- **Qué es**: Una función Python normal que recibe un `request` y devuelve un `response`.
- **Cuándo usarla**: Cuando la lógica es **única**, **personalizada** o **compleja** (agrupaciones, diccionarios temporales, lógica condicional elaborada). Ejemplos en tu proyecto: `ver_eventos`, `detalle_evento`, `TorneoDetail`, `ver_equipo`.
- **Cómo funciona**: Tú controlas TODO manualmente (buscar datos, armar el contexto, elegir el template, devolver la respuesta).

### CBV (Class-Based View) — Vista basada en clase
```python
class TorneoListView(ListView):
    model = Torneo
    template_name = 'SportApp/torneo_lista.html'
```
- **Qué es**: Una clase que hereda de una vista genérica de Django. Django ya tiene toda la lógica CRUD escrita; tú solo configuras atributos.
- **Cuándo usarla**: Cuando la operación es **estándar** (listar, crear, editar, borrar). Django hará el trabajo pesado.
- **Cómo funciona**: Django ejecuta una cadena de métodos internos en orden. Tú **sobreescribes** solo los que necesitas modificar.

---

## PARTE 2: ATRIBUTOS DE CLASE — La configuración base de toda CBV

Estos son los "ajustes" que defines directamente en la clase, sin sobreescribir ningún método:

| Atributo | Qué hace | Ejemplo en tu proyecto |
|---|---|---|
| `model` | Le dice a Django de qué tabla sacar los datos | `model = Jugador` |
| `template_name` | Qué HTML renderizar | `template_name = 'SportApp/jugador_lista.html'` |
| `context_object_name` | Nombre de la variable en el template (por defecto es `object_list`) | `context_object_name = 'jugadores'` |
| `form_class` | Qué formulario usar (en Create/Update) | `form_class = JugadorForm` |
| `success_url` | A dónde redirigir tras éxito (Create/Update/Delete) | `success_url = reverse_lazy('jugador_lista')` |
| `ordering` | Orden por defecto del queryset | `ordering = ['deporte', 'nombre']` |
| `fields` | Alternativa rápida a `form_class`: lista de campos a mostrar | (No lo usas, usas `form_class`) |

### `reverse_lazy` vs `reverse`
- **`reverse_lazy('nombre_url')`**: Se evalúa **después** de que Django cargue todas las URLs. Se usa en **atributos de clase** (porque la clase se carga antes que las URLs).
- **`reverse('nombre_url')`**: Se evalúa **inmediatamente**. Se usa **dentro de métodos** (porque cuando el método se ejecuta, las URLs ya están cargadas).

```python
# EN ATRIBUTO DE CLASE → reverse_lazy (obligatorio)
success_url = reverse_lazy('equipo_lista')

# DENTRO DE UN MÉTODO → reverse (seguro, ya están cargadas)
def get_success_url(self):
    return reverse('detalle_evento', kwargs={'evento_pk': self.object.pk})
```

---

## PARTE 3: MIXINS — Las "capas de seguridad"

Un Mixin es una clase que añade funcionalidad extra a tu vista sin ser una vista por sí misma. Se heredan **antes** de la vista genérica (orden de izquierda a derecha importa).

### `LoginRequiredMixin`
```python
class JugadorListView(LoginRequiredMixin, ListView):
```
- **Qué hace**: Si el usuario NO ha iniciado sesión → lo redirige al login.
- **Equivalente en FBV**: el decorador `@login_required`.
- **Cuándo usarlo**: En CUALQUIER vista que requiera estar logueado.

### `UserPassesTestMixin` (y tu `StaffRequiredMixin`)
```python
class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff
```
- **Qué hace**: Ejecuta `test_func()`. Si devuelve `True` → pasa. Si devuelve `False` → error 403 (Forbidden).
- **Método que sobreescribes**: `test_func(self)`.
- **Cuándo usarlo**: Cuando necesitas un control de acceso **más específico** que solo "estar logueado". En tu caso: "ser staff".
- **Por qué creaste un Mixin propio**: Para no repetir `test_func` en cada vista de staff. Lo defines una vez y lo reutilizas.

### Orden de herencia
```python
class PartidoCreateView(StaffRequiredMixin, CreateView):
```
Python lee de **izquierda a derecha**. Primero comprueba `StaffRequiredMixin` (¿es staff?) y solo si pasa, ejecuta `CreateView`. Si pones `CreateView` primero, la seguridad no funcionaría correctamente.

---

## PARTE 4: MÉTODOS SOBREESCRITOS — El cuándo, cómo y por qué de CADA UNO

### 4.1 `get_queryset(self)` — "QUÉ datos traigo"

**Vista genérica que lo usa**: `ListView`, `UpdateView`, `DeleteView`

**Qué hace por defecto**: Devuelve `self.model.objects.all()` (TODOS los registros de la tabla).

**Por qué lo sobreescribes**: Para **filtrar** los datos. Normalmente para que un usuario solo vea/edite/borre **sus propios objetos**.

**Ejemplos en tu proyecto:**

```python
# JugadorListView — Filtrar jugadores por usuario
class JugadorListView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        if self.request.user.is_staff:
            return Jugador.objects.select_related('equipo').order_by('equipo', 'dorsal')
        # Si NO es staff, solo sus jugadores
        return Jugador.objects.filter(equipo__usuario=self.request.user).select_related('equipo').order_by('equipo', 'dorsal')
```
**Patrón**: `if is_staff → todo; else → filtrar por usuario`. Lo repites en `EquipoListView`, `EquipoUpdateView`, `EquipoDeleteView`.

```python
# JugadorDeleteView — Seguridad: que solo borre SUS jugadores
class JugadorDeleteView(LoginRequiredMixin, DeleteView):
    def get_queryset(self):
        return Jugador.objects.filter(equipo__usuario=self.request.user)
```
**Importancia de seguridad**: Sin esto, un usuario podría poner `/jugadores/999/eliminar/` en la URL y borrar el jugador de otro usuario. Con `get_queryset` filtrado, Django devuelve **404** si el objeto no pertenece al usuario (porque no lo encuentra en el queryset filtrado).

---

### 4.2 `get_context_data(self, **kwargs)` — "QUÉ variables extra mando al HTML"

**Vista genérica que lo usa**: TODAS (ListView, DetailView, CreateView, TemplateView...)

**Qué hace por defecto**: Crea un diccionario con las variables básicas (la lista de objetos en ListView, el objeto individual en DetailView, el formulario en CreateView).

**Por qué lo sobreescribes**: Para **añadir variables extra** al template que la vista genérica no proporciona.

**Regla de oro**: SIEMPRE llamar a `super().get_context_data(**kwargs)` primero para no perder las variables que Django ya preparó.

**Ejemplos en tu proyecto:**

```python
# EquipoListView — Añadir estadísticas al contexto
class EquipoListView(LoginRequiredMixin, ListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # ← Paso 1: traer lo que Django ya preparó
        stats = self.get_queryset().aggregate(total_equipos=models.Count('id'))
        context['stats'] = stats       # ← Paso 2: añadir datos extra
        return context                 # ← Paso 3: devolver el diccionario completo
```
El template recibe `{{ equipos }}` (de la ListView) **Y** `{{ stats.total_equipos }}` (de tu override).

```python
# EstadisticaPartidoPorPartidoListView — Pasar el partido al template
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['partido'] = self.partido  # ← self.partido se guardó en dispatch()
    return context
```

```python
# EstadisticaPartidoListView (TemplateView) — AQUÍ METES TODO
# Como TemplateView no trae datos automáticamente, get_context_data es donde
# haces TODAS las consultas (globales, top_puntos, top_minutos, top_participaciones)
```

---

### 4.3 `form_valid(self, form)` — "QUÉ hago JUSTO ANTES de guardar en la BD"

**Vista genérica que lo usa**: `CreateView`, `UpdateView`

**Qué hace por defecto**: Ejecuta `form.save()` y redirige a `success_url`.

**Por qué lo sobreescribes**: Para **inyectar datos** que el formulario no tiene (como el usuario actual) o para hacer **validaciones extra** antes de guardar.

**Ejemplos en tu proyecto:**

```python
# EquipoCreateView — Asignar el usuario propietario
class EquipoCreateView(LoginRequiredMixin, CreateView):
    def form_valid(self, form):
        form.instance.usuario = self.request.user  # ← "Este equipo es MÍO"
        return super().form_valid(form)            # ← Ahora sí, guarda
```
**Por qué aquí y no en el formulario**: Porque el campo `usuario` está en `exclude = ['usuario']` del formulario (no se muestra al usuario). El `form.instance` es el objeto del modelo **antes de guardarse** en la BD. Le inyectas el dato faltante y luego llamas a `super()` para que Django haga el `save()`.

```python
# InscripcionCreateView — Validación de seguridad extra
class InscripcionCreateView(LoginRequiredMixin, CreateView):
    def form_valid(self, form):
        equipo = form.cleaned_data['equipo']
        if equipo.usuario != self.request.user:
            form.add_error('equipo', 'No puedes inscribir un equipo que no te pertenece.')
            return self.form_invalid(form)   # ← Recarga el formulario CON el error
        return super().form_valid(form)
```
**Patrón**: `form.add_error()` + `return self.form_invalid(form)` — Forma de rechazar un formulario válido técnicamente pero inválido lógicamente.

---

### 4.4 `get_form(self, form_class=None)` — "CÓMO configuro el formulario antes de mostrarlo"

**Vista genérica que lo usa**: `CreateView`, `UpdateView`

**Qué hace por defecto**: Instancia el formulario con los datos de la petición.

**Por qué lo sobreescribes**: Para **modificar los campos del formulario dinámicamente** (reducir opciones de un desplegable, cambiar un queryset, etc.).

**Ejemplos en tu proyecto:**

```python
# JugadorCreateView — Solo mostrar MIS equipos en el dropdown
class JugadorCreateView(LoginRequiredMixin, CreateView):
    def get_form(self, form_class=None):
        form = super().get_form(form_class)       # ← Obtener el formulario normal
        form.fields['equipo'].queryset = Equipo.objects.filter(usuario=self.request.user)
        return form                               # ← Devolver el formulario modificado
```
**Sin esto**: El desplegable "Equipo" mostraría TODOS los equipos de la BD (incluidos los de otros usuarios). Con esto, solo muestra los del usuario logueado.

```python
# EstadisticaPartidoCreateView — Filtrar jugadores y partido
def get_form(self, form_class=None):
    form = super().get_form(form_class)
    if self.partido is not None:
        # Solo muestro ESTE partido en el dropdown
        form.fields['partido'].queryset = Partido.objects.filter(pk=self.partido.pk)
        # Solo muestro jugadores de los DOS equipos que juegan
        form.fields['jugador'].queryset = Jugador.objects.filter(
            equipo__in=[self.partido.equipo_local, self.partido.equipo_visitante]
        ).order_by('equipo__nombre', 'dorsal', 'nombre')
    return form
```

---

### 4.5 `get_success_url(self)` — "A DÓNDE redirijo después del éxito"

**Vista genérica que lo usa**: `CreateView`, `UpdateView`, `DeleteView`

**Qué hace por defecto**: Devuelve `self.success_url`.

**Por qué lo sobreescribes**: Cuando la URL de destino **depende del objeto** que acabas de crear/editar/borrar.

```python
# PartidoUpdateView — Volver al detalle del partido que acabas de editar
class PartidoUpdateView(StaffRequiredMixin, UpdateView):
    def get_success_url(self):
        return reverse('detalle_evento', kwargs={'evento_pk': self.object.pk})
        #                                        ↑ self.object = el Partido que acabamos de guardar
```
**`self.object`**: Dentro de una CBV, después de hacer `save()`, Django guarda el objeto en `self.object`. Puedes acceder a su `pk` o cualquier campo.

**Cuándo usar `success_url` (atributo) vs `get_success_url()` (método)**:
- `success_url = reverse_lazy('lista')` → URL fija, siempre la misma.
- `get_success_url()` → URL dinámica, depende del objeto.

---

### 4.6 `dispatch(self, request, *args, **kwargs)` — "QUÉ hago ANTES de que la vista procese NADA"

**Vista genérica que lo usa**: TODAS

**Qué hace por defecto**: Determina si la petición es GET o POST y llama al método correspondiente (`get()` o `post()`).

**Por qué lo sobreescribes**: Para **capturar parámetros de la URL** y guardarlos en `self` ANTES de que se ejecuten `get_queryset`, `get_form`, etc.

```python
# EstadisticaPartidoPorPartidoListView
class EstadisticaPartidoPorPartidoListView(LoginRequiredMixin, ListView):
    def dispatch(self, request, *args, **kwargs):
        self.partido = get_object_or_404(
            Partido.objects.select_related('torneo', 'equipo_local', 'equipo_visitante'),
            pk=kwargs.get('partido_pk')  # ← Captura de la URL: /partidos/5/estadisticas/
        )
        return super().dispatch(request, *args, **kwargs)
```
**Flujo**: 
1. URL → `dispatch()` → guarda `self.partido`
2. Django llama `get_queryset()` → usa `self.partido` para filtrar
3. Django llama `get_context_data()` → mete `self.partido` en el contexto

**Sin dispatch**: No tendrías forma de compartir `self.partido` entre `get_queryset` y `get_context_data`. Tendrías que hacer `get_object_or_404` en cada método (duplicando consultas).

---

### 4.7 `get_initial(self)` — "QUÉ valores pongo por defecto en el formulario VACÍO"

**Vista genérica que lo usa**: `CreateView`

**Qué hace por defecto**: Devuelve un diccionario vacío `{}`.

**Por qué lo sobreescribes**: Para **pre-rellenar** campos del formulario cuando el usuario llega desde un contexto específico.

```python
# EstadisticaPartidoCreateView — Pre-rellenar el campo 'partido'
def get_initial(self):
    initial = super().get_initial()
    if self.partido is not None:
        initial['partido'] = self.partido  # ← El dropdown ya viene seleccionado
    return initial
```
**Caso de uso**: El usuario está viendo las estadísticas del partido Madrid vs Barcelona y hace clic en "Añadir Estadística". Cuando llega al formulario, el campo "Partido" ya está seleccionado con "Madrid vs Barcelona" gracias a `get_initial`.

---

## PARTE 5: FLUJO COMPLETO DE UNA CBV — El orden interno

Cuando Django procesa una petición, ejecuta los métodos en este orden:

### Para un GET (mostrar formulario / listar):
```
1. dispatch()          → ¿Es GET o POST? Captura parámetros
2. get_queryset()      → Busca los datos en la BD (ListView/Update/Delete)
3. get_form()          → Construye el formulario (Create/Update)
4. get_initial()       → Valores por defecto del formulario (solo Create)
5. get_context_data()  → Empaqueta todo en un diccionario
6. render()            → Pinta el template con el contexto
```

### Para un POST (enviar formulario):
```
1. dispatch()          → ¿Es GET o POST?
2. get_form()          → Construye el formulario CON los datos enviados
3. form.is_valid()?    → ¿Pasan las validaciones?
   ├─ SÍ → form_valid()      → Guarda en BD + redirige a success_url
   └─ NO → form_invalid()    → Recarga el formulario con errores
```

---

## PARTE 6: VISTAS GENÉRICAS — Resumen de cada tipo

| Vista | Verbo HTTP | Métodos típicos a sobreescribir | Cuándo la usas |
|---|---|---|---|
| **ListView** | GET | `get_queryset`, `get_context_data` | Listar objetos |
| **DetailView** | GET | `get_context_data`, `get_queryset` | Ver detalle de 1 objeto |
| **CreateView** | GET/POST | `form_valid`, `get_form`, `get_initial` | Crear un objeto nuevo |
| **UpdateView** | GET/POST | `form_valid`, `get_form`, `get_queryset` | Editar un objeto existente |
| **DeleteView** | GET/POST | `get_queryset`, `get_success_url` | Borrar un objeto |
| **TemplateView** | GET | `get_context_data` | Dashboard, páginas con datos mixtos |

---

## PARTE 7: FBVs EN TU PROYECTO — Decoradores y patrones

### `@login_required`
```python
@login_required
def detalle_evento(request, evento_pk):
```
Equivalente FBV de `LoginRequiredMixin`. Si no está logueado → redirige al login.

### `get_object_or_404()`
```python
evento = get_object_or_404(Partido, pk=evento_pk)
```
**Qué hace**: Busca un objeto. Si existe → lo devuelve. Si NO existe → lanza error **404** (Página no encontrada).
**Por qué no usar `.get()`**: Porque `.get()` lanza una excepción genérica de Python (`DoesNotExist`). Con `get_object_or_404` obtienes un error HTTP 404 limpio para el navegador del usuario.

### `render(request, template, context)`
```python
return render(request, 'SportApp/ver_equipo.html', {'equipo': equipo, 'inscripciones': inscripciones})
```
Construye la respuesta HTTP final: toma el template, lo rellena con las variables del diccionario `context`, y devuelve el HTML generado.

---

## PARTE 8: CONSULTAS ORM AVANZADAS (las necesitarás)

### `filter()` — Filtrar registros
```python
Equipo.objects.filter(usuario=self.request.user)           # Campo directo
Jugador.objects.filter(equipo__usuario=self.request.user)   # Relación FK (doble guion bajo)
```

### `select_related()` — JOIN para FK (hacia adelante)
```python
Partido.objects.select_related('torneo', 'equipo_local')   # 1 consulta en vez de N+1
```

### `annotate()` — Añadir un campo calculado a CADA objeto
```python
Equipo.objects.annotate(num_jugadores=models.Count('jugadores'))
# Cada equipo ahora tiene equipo.num_jugadores
```

### `aggregate()` — Calcular un TOTAL global (devuelve diccionario, no queryset)
```python
EstadisticaPartido.objects.aggregate(total_puntos=models.Sum('puntos'))
# Resultado: {'total_puntos': 245}
```

### `models.Q()` — Condiciones complejas
```python
models.Count('id', filter=models.Q(juega=True))  # Contar solo donde juega=True
```

### `[:5]` — LIMIT (limitar resultados)
```python
.order_by('-total_puntos')[:5]  # Los 5 mejores
```

### `__gt` / `__lt` / `__in` — Lookups
```python
.filter(total_puntos__gt=0)     # gt = Greater Than (mayor que)
.filter(equipo__in=[eq1, eq2])  # IN = está en esta lista
```

---

## PARTE 9: CHEAT SHEET — "Me piden implementar X, ¿qué hago?"

| El profesor dice... | Tú haces... |
|---|---|
| "Que solo vea sus datos" | Sobreescribir `get_queryset()` con `.filter(usuario=self.request.user)` |
| "Que el desplegable solo muestre sus opciones" | Sobreescribir `get_form()` y cambiar `.queryset` del field |
| "Que el usuario se asigne automáticamente" | Sobreescribir `form_valid()` con `form.instance.usuario = self.request.user` |
| "Que solo pueda acceder el staff" | Usar `StaffRequiredMixin` (o crear uno nuevo con `UserPassesTestMixin`) |
| "Que después de guardar vaya al detalle" | Sobreescribir `get_success_url()` con `reverse('detalle', kwargs={'pk': self.object.pk})` |
| "Añadir datos extra a la página" | Sobreescribir `get_context_data()` y meter variables en `context` |
| "Pre-rellenar un campo del formulario" | Sobreescribir `get_initial()` y devolver un dict con el valor |
| "Necesito cargar algo de la URL antes de todo" | Sobreescribir `dispatch()` y guardar en `self.algo` |
| "Crear una página tipo dashboard con datos mixtos" | Usar `TemplateView` + `get_context_data()` con múltiples consultas |
| "Validar algo que el formulario no valida" | En `form_valid()`: comprobar → `form.add_error()` → `return self.form_invalid(form)` |
