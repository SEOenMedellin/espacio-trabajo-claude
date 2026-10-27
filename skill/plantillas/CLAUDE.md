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

## Tus atajos

Si el repositorio ya traía skills, `{{CONTEXTO}}skills-del-repositorio.md`
dice cuál usar para cada tarea, qué reglas imponen y qué conocimiento no está
validado; las tareas que cubre un skill existente se hacen con ese skill.
Cuando aparece uno nuevo o cambia alguno, se revisa antes de usarlo
(`references/skills-existentes.md` del skill primeros-pasos).

Cada tarea habitual sin skill propio tiene un atajo en `.claude/skills/<tarea>/`, que la
persona usa escribiendo `/<tarea>` o pidiéndola con sus palabras. Si la
petición coincide con un atajo, se invoca con la herramienta `Skill` y se
siguen sus pasos: así la tarea sale igual cada vez. La primera vez que se usa
un atajo, al cerrar se completa su sección «Cómo se hace» (con el sí de la
persona).

## Antes de cada tarea — verificar antes de inferir

0. Si es una tarea del trabajo de la persona (no configurar el espacio ni
   crear skills), abrirla: da el id, crea su carpeta y pone el reloj:
   `{{PY}} {{SKILL_REL}}/scripts/tarea.py --empezar --proceso <tipo> --categoria <categoria>{{PROYECTO_FLAG}}`.
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

- Los entregables van a la carpeta que dio `tarea.py --empezar`
  (`{{ENTREGABLES}}{{PATRON_ENTREGA}}`). Lo que otra tarea deba releer como
  insumo va a `{{CONTEXTO}}`.
- **Enriquecimiento proactivo:** si aparece una restricción, dependencia,
  peculiaridad del negocio o advertencia que nadie mencionó, se anota (en la
  entrada de la bitácora como «Conocimiento adyacente» y, si sirve a futuro,
  como nodo de memoria).
- **Fuentes oficiales:** todo dato que sostenga una decisión y pueda haber
  cambiado (precios, normas, versiones, cifras) se confirma en la fuente
  oficial y se cita. Si no se pudo verificar, se marca *no verificado*.

## Al terminar cada tarea — protocolo de cierre

Solo para tareas del trabajo de la persona (ver «Qué se documenta y qué no»):
un informe, una investigación, un análisis; nunca configurar el espacio, crear
skills ni ajustar funciones. Decirle en una frase qué se hizo y qué se va a
recordar, y hacer **una sola** `AskUserQuestion` con dos preguntas:

- «¿Lo guardo así para la próxima vez?» (Sí, guárdalo · Corrige algo · No hace falta).
- «¿Cuánto te habría tomado hacerlo a mano, en promedio?». Si ya lo estimó
  para este tipo de tarea (`tiempo.py --estimacion <proceso>`), la primera
  opción es ese valor («Lo mismo que la vez pasada: 2 h»); si no, opciones
  como 30 min · 1 h · 2 h · medio día. Con «Otro» dice el tiempo exacto.

Con el sí, un solo comando registra todo (entrada de la bitácora con fecha y
hora, `memoria.md` junto al entregable, tiempo ahorrado, tabla de procesos,
memoria y grafo) y te da la frase que le dices a la persona («Con Claude:
25 min; a mano: 2 h. Te ahorraste 1 h 35 min.»):

```bash
{{PY}} {{SKILL_REL}}/scripts/tarea.py --cerrar --datos -{{PROYECTO_FLAG}} <<'FIN'
{"titulo": "…", "peticion": "…con sus palabras", "como": "…pasos y decisiones",
 "patrones": "…", "adyacente": "…", "correccion": "…",
 "skills": [], "memoria": [], "deriva_en": [], "estado": "resuelta", "manual": 120}
FIN
```

Los campos `patrones`, `adyacente`, `correccion`, `skills`, `memoria` y
`deriva_en` se omiten si no aplican; `manual` son los minutos que dijo la
persona. Después, solo si aplica:

1. Nodo de memoria si se aprendió algo que sirve a futuro: global
   (`{{MEMORIA_GLOBAL}}`) o del proyecto (`{{MEMORIA_PROYECTO}}`), con sus
   relaciones tipadas (`{{DOCS}}/memoria.md`); su id va en `deriva_en`.
2. Si la tarea usó un atajo por primera vez, completar sus secciones «Cómo se
   hace» y «Validaciones» con lo que funcionó (con el sí de la persona).
3. Si la tabla «Procesos candidatos» marca un proceso repetido o corregido
   que aún no tiene atajo, proponerle convertirlo en uno (`{{DOCS}}/crear-skills.md`).

Un hook `Stop` lo recuerda una vez por sesión si hubo cambios sin registrar.

## Al empezar cada sesión

El hook `SessionStart` (`inicio.py`) carga la última sesión de trabajo (de la
bitácora), las peticiones abiertas o recientes, el catálogo de skills instalados y las
anotaciones de memoria. En la primera respuesta, recuérdale a la persona en
dos o tres frases dónde quedó y, si hay peticiones abiertas, pregúntale si las
retoma. Ese catálogo es el punto de partida para saber con qué skills se
resuelve cada tarea.

- **Lista de arranque.** Mientras el espacio no esté al 100 %, el aviso dice
  cuánto falta («Arranque: 4 de 7 listo»). Muéstraselo en una línea; si dice
  «sigamos», completa lo siguiente con `arranque.py` (instalar o mover
  siempre se confirma).
- **Resumen semanal.** Si pasó una semana desde el último, ofrécele su
  resumen (`resumen.py`): tareas hechas, tiempo ahorrado, lo que aprendió
  Claude, lo que corrigió y lo que se repite. Si lo quiere guardar o enviar a
  alguien, `resumen.py --guardar{{PROYECTO_FLAG}}`. También cuando la persona
  pregunte por su semana, por lo que ha hecho o por cuánto tiempo ha ahorrado.

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
| `{{PY}} {{SKILL_REL}}/scripts/arranque.py` | Lo que falta para tener el espacio al 100 % |
| `{{PY}} {{SKILL_REL}}/scripts/tarea.py --empezar` / `--cerrar` | Abrir y cerrar una tarea: carpeta, reloj, bitácora, `memoria.md` y grafo |
| `{{PY}} {{SKILL_REL}}/scripts/tiempo.py --estimacion <proceso>` | Última estimación manual de ese tipo de tarea |
| `docs/espacio-de-trabajo/graph.md` | El grafo legible: qué requirió cada tarea, qué resolvió y en qué derivó |
| `{{PY}} {{SKILL_REL}}/scripts/resumen.py [--guardar]` | Resumen semanal: tareas, tiempo ahorrado, aprendizajes |
| `{{PY}} {{SKILL_REL}}/scripts/programas.py` | Programas para trabajar y cómo instalarlos |

Convenciones completas: `{{DOCS}}/`.
