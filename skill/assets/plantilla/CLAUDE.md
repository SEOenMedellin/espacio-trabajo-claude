# Espacio de trabajo — {{PROYECTO}}

Generado por `primeros-pasos` {{VERSION}} el {{FECHA}} a partir de la
entrevista inicial. Este bloque se regenera desde `espacio.json`: para
cambiarlo, vuelve a correr `primeros-pasos` (o edita `espacio.json` y corre
`montar.py --actualizar`). Lo que escribas fuera de los marcadores no se toca.

## Quién trabaja aquí

- **Cargo:** {{CARGO}} · **Área:** {{AREA}}
- **Objetivo del proyecto:** {{OBJETIVO}}
- **Para quién es el trabajo:** {{DESTINATARIOS}}
- **Modo:** {{MODO}}

Perfil completo (conocimientos, tareas habituales, herramientas, programas):
`{{DOCS}}/perfil.md`. Investigación del rol: {{ROL_DOC}}.

**Lineamientos del rol** — reglas que salen de lo que exige el oficio; cada
tarea las respeta:

{{LINEAMIENTOS}}

**Cómo hablarle:** {{TRATO}} Idioma: `{{IDIOMA}}`.

## Mapa de carpetas — arquitectura «{{TIPO}}»

Por qué esta arquitectura: {{POR_QUE}}

{{MAPA}}

Nada se escribe suelto en la raíz. Las rutas exactas de cada rol están en
`espacio.json` → `rutas`; si este archivo y `espacio.json` no coinciden, gana
`espacio.json`.

Fechas siempre `DD-mmm-YYYY` con el mes abreviado (`10-oct-2026`). Rutas
cortas: como mucho 6 niveles, 150 caracteres y nombres de 60, para que nada
falle en Windows ni macOS.

**El espacio no se deforma.** Un hook bloquea crear archivos fuera de este
mapa y dice dónde van. **Mover o renombrar archivos siempre se confirma con la
persona**: se le muestra qué se mueve, de dónde y a dónde, y se pregunta antes
(el hook además hace que Claude Code pida permiso). Para reordenar:
`ordenar.py` (plan) y `ordenar.py --aplicar --solo <rutas aprobadas>`. Detalle
en `{{DOCS}}/carpetas.md`.

## Antes de cada tarea — verificar antes de inferir

1. `{{PY}} {{SKILL_REL}}/scripts/grafo.py --plan "<la petición>"{{PROYECTO_FLAG}}`:
   dice qué skills invocar, qué memoria leer, qué contexto aplica y qué
   peticiones parecidas ya se resolvieron.
2. Invocar con la herramienta `Skill` los skills que marque. Leer los nodos de
   memoria indicados y **listar completa** la carpeta `{{CONTEXTO}}`.
3. Si el plan dice «sin antecedentes» (no hay skill, memoria, contexto ni
   metodología que aplique), seguir el protocolo de investigación profunda
   (`{{DOCS}}/investigacion.md`) antes de ejecutar.

Toda respuesta que ejecute trabajo empieza diciendo qué skills, memoria y
contexto se consultaron.

## Durante la tarea

- Los entregables van a `{{ENTREGABLES}}<categoria>/<archivo>` (fecha
  `DD-mmm-YYYY`). Lo que otra tarea deba releer como insumo va a `{{CONTEXTO}}`.
- **Enriquecimiento proactivo:** si aparece una restricción, dependencia,
  peculiaridad del negocio o advertencia que nadie mencionó, se anota (en la
  entrada de la bitácora como «Conocimiento adyacente» y, si sirve a futuro,
  como nodo de memoria).
- **Fuentes oficiales:** todo dato que sostenga una decisión y pueda haber
  cambiado (precios, normas, versiones, cifras) se confirma en la fuente
  oficial y se cita. Si no se pudo verificar, se marca *no verificado*.

## Al terminar cada tarea — protocolo de cierre

Solo para tareas del trabajo de la persona (ver «Qué se documenta y qué no»).
Decirle a la persona en una frase qué se hizo y qué se va a recordar, y
preguntar con una sola `AskUserQuestion`: «¿Lo guardo así para la próxima
vez?» (Sí, guárdalo · Corrige algo · No hace falta). Después, en silencio:

1. Entrada en `{{BITACORA}}` con el formato exacto (`{{DOCS}}/bitacoras.md`),
   incluyendo «Patrones y atajos» y «Conocimiento adyacente» cuando los haya.
   Las correcciones de la persona siempre van en la entrada.
2. Nodo de memoria si se aprendió algo: global (`{{MEMORIA_GLOBAL}}`) si sirve a
   cualquier proyecto, del proyecto (`{{MEMORIA_PROYECTO}}`) si es específico
   (`{{DOCS}}/memoria.md`).
3. `bitacora.py --tabla{{PROYECTO_FLAG}}`, `memoria.py --rebuild` y `grafo.py --actualizar`.
4. Si la tabla «Procesos candidatos» marca un proceso repetido o corregido,
   proponerle a la persona convertirlo en un skill (`{{DOCS}}/crear-skills.md`).

Un hook `Stop` lo recuerda una vez por sesión si hubo cambios sin registrar.

## Al empezar cada sesión

El hook `SessionStart` (`inicio.py`) carga la última sesión de trabajo (de la
bitácora), las peticiones abiertas o recientes, el catálogo de skills instalados y las
anotaciones de memoria. En la primera respuesta, recuérdale a la persona en
dos o tres frases dónde quedó y, si hay peticiones abiertas, pregúntale si las
retoma. Ese catálogo es el punto de partida para saber con qué skills se
resuelve cada tarea.

## Credenciales

Viven en `credenciales/.env`, que nunca se versiona; `credenciales/.env.example`
lista los nombres. **Nunca se piden ni se pegan secretos en el chat.** Si un
acceso falta o falla, no se detiene el trabajo: se sigue con lo disponible, se
marca `n/d` y al final se explica en una frase qué faltó y cómo conseguirlo
(`{{DOCS}}/credenciales.md`). Accesos previstos:

{{CREDENCIALES}}

## Salvaguardas

- Nada se publica, envía, sobrescribe ni despliega fuera de este espacio sin
  mostrar la versión final y recibir un «sí» explícito en la misma conversación.
- No se escriben dominios, IDs, claves ni nombres de cliente dentro de un skill
  o script reutilizable: esos valores viven en `espacio.json`, `{{CONTEXTO}}` y
  `credenciales/`.
- Antes de borrar o mover algo, se mira qué es y se pregunta.

## Qué se documenta y qué no

La bitácora, la memoria y el grafo son **solo del trabajo de la persona en su
rol**: las tareas de su cargo, lo que entregó, lo que se aprendió del negocio,
del cliente o del oficio. **Nunca** se registran la configuración de este
espacio, la creación o el orden de carpetas, las credenciales, la creación de
skills, ajustes de hooks o scripts, ni nada sobre el desarrollo de este
sistema. Si una sesión solo tocó el sistema, no deja rastro en la bitácora ni
en la memoria.

## Herramientas del espacio

Todas desde la raíz:

| Comando | Para qué |
|---|---|
| `{{PY}} {{SKILL_REL}}/scripts/grafo.py --plan "<petición>"` | Qué abrir antes de una tarea |
| `{{PY}} {{SKILL_REL}}/scripts/grafo.py --actualizar` | Reconstruir el grafo tras crear o mover archivos |
| `{{PY}} {{SKILL_REL}}/scripts/bitacora.py --siguiente` / `--tabla` | Próxima entrada / procesos candidatos |
| `{{PY}} {{SKILL_REL}}/scripts/memoria.py --rebuild` | Validar la memoria y regenerar sus índices |
| `{{PY}} {{SKILL_REL}}/scripts/verificar.py` | Estado del espacio (reparar con `montar.py`) |

Convenciones completas: `{{DOCS}}/`.
