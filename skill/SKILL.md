---
name: primeros-pasos
description: >
  Configuración inicial del espacio de trabajo de un colaborador en cualquier
  repositorio, para cualquier cargo y proyecto. Entrevista a la persona (cargo,
  proyecto y objetivo, conocimientos que Claude debe tener, tareas habituales,
  herramientas), investiga a fondo su rol (responsabilidades, obligaciones,
  tareas comunes y programas que necesita), saca de ahí los lineamientos de la
  arquitectura de carpetas que necesita según su objetivo y la monta con CLAUDE.md, bitácoras, memoria de trabajo, grafo de
  orquestación, protocolo de investigación profunda, creación de skills a
  partir del trabajo, credenciales seguras y hooks de inicio y cierre de
  sesión. Actívalo cuando alguien escriba "empezar", "empecemos", "iniciar",
  "comenzar", "arrancar", "configurar", "preparar", "setup", "primeros pasos",
  "configura mi espacio", "prepara este repositorio", "soy nuevo en el
  proyecto", "organiza mis carpetas", o cuando la carpeta no tenga
  espacio.json. Un hook (activar.py) también lo pide cuando el mensaje es
  solo una de esas palabras. También para ampliarlo ("tengo un proyecto nuevo", "cambió mi
  cargo", "ahora también hago…") o repararlo si el aviso de inicio dice que
  faltan piezas. No es el skill de onboarding de usuarios de un producto.
---

# Primeros pasos

Prepara un espacio de trabajo hecho a la medida de quien lo va a usar. No
asume área, empresa ni herramienta: todo sale de la entrevista. El resultado
es un repositorio en el que Claude sabe quién es la persona, qué hace, dónde
va cada cosa, qué se resolvió antes y cómo aprender de cada tarea.

## Qué deja montado

| Pieza | Para qué |
|---|---|
| `espacio.json` | La configuración: perfil, arquitectura y rutas de cada rol. Todo lo demás se deriva de aquí |
| Investigación del rol | Responsabilidades, obligaciones, tareas comunes y programas del oficio, con fuentes; de ella salen los lineamientos (`references/investigar-rol.md`) |
| Arquitectura de carpetas | Elegida según el objetivo y los lineamientos del rol (`references/arquitecturas.md`) |
| Programas para trabajar | Git, Python, Node.js y Playwright siempre, más los que pida el rol; `programas.py` los comprueba e instala, el aviso de inicio dice cuáles faltan y nada se instala sin confirmación |
| `CLAUDE.md` (bloque entre marcadores) | Perfil, mapa de carpetas y protocolo de trabajo; respeta lo que ya hubiera |
| `docs/espacio-de-trabajo/` | Convenciones: carpetas, bitácoras, memoria, grafo, investigación, crear skills, credenciales, y el perfil |
| Bitácora de trabajo | Una entrada por tarea del rol, con patrones, conocimiento adyacente y correcciones. Nunca registra configuración ni nada del sistema |
| Memoria (global y por proyecto) | Un nodo por cosa resuelta, con índice regenerable |
| Grafo de orquestación | `grafo.py --plan` dice qué skills, memoria y contexto abrir antes de cada tarea |
| `credenciales/` | `.env` fuera de git y `.env.example` con los accesos previstos |
| Revisión de lo existente | Inventario y auditoría de los skills, reglas, hooks y MCP que ya tenía el repositorio; su conocimiento validado va al contexto y las correcciones se aplican con confirmación |
| Activación | `activar.py` (hook `UserPromptSubmit`, registrado ya por el instalador): si el mensaje es «empezar», «iniciar», «configurar» o equivalente, le indica a Claude que invoque este skill |
| Hooks | `SessionStart`: última sesión, peticiones abiertas, catálogo de skills, anotaciones y orden. `PreToolUse`: bloquea archivos fuera de la arquitectura y pide confirmación para mover. `Stop`: recuerda el cierre |
| Orden | `ordenar.py` propone a dónde va cada archivo según su contenido y uso; mueve solo lo que la persona confirme |
| Atajos | Un skill por tarea habitual (`.claude/skills/<tarea>/`), invocable como `/<tarea>`; su «Cómo se hace» se completa la primera vez que se usa |
| Lista de arranque | `arranque.py`: lo que falta para tener el espacio al 100 %; el aviso de inicio la muestra mientras esté incompleta |
| Tiempo ahorrado | `tiempo.py` mide cada tarea con Claude y, al cerrar, se le pregunta a la persona cuánto le tomaría a mano; queda en la bitácora |
| Resumen semanal | `resumen.py`: tareas, tiempo ahorrado, lo aprendido, correcciones, pendientes y qué se repite; el aviso de inicio lo ofrece cada semana |

## Qué se documenta

La bitácora, la memoria y el grafo que monta este skill son **solo del
trabajo de la persona en su rol**. Nada de lo que hace este skill (entrevista,
carpetas, credenciales, hooks, reorganizar, crear skills, reparar,
actualizar) se registra en ellos, y la persona tampoco debe ver entradas
sobre el sistema.

## A quién le hablas

A cualquier persona: puede no saber qué es un skill, un hook o un JSON, y no
tiene por qué saberlo. Habla de «tu espacio de trabajo», «tus carpetas»,
«lo que aprendamos», «tus accesos». Los nombres técnicos, solo si la persona
los usa primero o los pide. Nunca muestres trazas de error ni salidas crudas
de un script: explica en una frase y aplica la solución.

Este skill **nunca**: borra ni mueve archivos de la persona, sobrescribe un
archivo existente (el bloque de `CLAUDE.md` solo se rehace con
`--actualizar`, y con copia previa), quita entradas de
`.claude/settings.json`, pide o escribe valores de credenciales, agrega
remotos de git ni publica nada fuera del repositorio.

## Cuándo corre

| Situación | Ir a |
|---|---|
| No hay `espacio.json` en la raíz | Montaje completo, pasos 1 a 9 |
| Hay skills nuevos o cambiados sin revisar, o la persona pide «revisa mis skills» | `references/skills-existentes.md`, y luego Ampliar con el bloque `skills_existentes` |
| Hay `espacio.json` y la persona trae algo nuevo (proyecto, cargo, tareas) | Ampliar |
| El aviso de inicio o `verificar.py` dice que faltan piezas | Reparar |
| Hay una versión nueva de este skill | Actualizar |

Todos los comandos se corren desde la raíz del repositorio con Bash.
`<skill>` es la carpeta de este skill (normalmente
`.claude/skills/primeros-pasos`).

## Paso 1 — Python y estado

Los scripts usan solo la biblioteca estándar de Python 3.10 o superior. Prueba
`python --version`, `python3 --version` y `py -3 --version`, y usa el primero
que responda 3.10+ en todo lo que sigue. En Windows, `python` puede abrir la
tienda o fallar con 9009: eso cuenta como «no está». Si no hay Python, dile a
la persona que lo instale desde python.org (en Windows, marcando «Add Python
to PATH»), que reabra Claude y que vuelva a escribir «empezar».

```bash
python <skill>/scripts/verificar.py
```

Código 2 = sin montar (paso 2). Código 1 = Reparar. Código 0 = ya está
montado: pregunta si quiere ampliarlo o si solo quería empezar a trabajar.

Revisa también los programas de base para trabajar (Git, Python, Node.js y
Playwright):

```bash
python <skill>/scripts/programas.py
```

Si falta alguno, díselo en una frase y pregunta con `AskUserQuestion`
(«Sí, instálalos» · «Ahora no»). Con un sí, uno por uno:
`python <skill>/scripts/programas.py --instalar <nombre>` (Node.js antes que
Playwright). Si la instalación pide permisos de administrador o una ventana,
pásale la orden (`programas.py --comando <nombre>`) para que la corra con
`! <orden>`. Un programa que falte no detiene el montaje.

## Paso 2 — Mirar el repositorio

Antes de preguntar, lista la raíz y lee lo que ya haya: `README`, `CLAUDE.md`,
`docs/`, la estructura de código. Sirve para no preguntar lo que ya está
escrito y para el paso 4 de `references/arquitecturas.md` (adoptar lo que
existe, no mover nada).

Luego, el inventario de lo que ya trae:

```bash
python <skill>/scripts/inventario.py
```

Si hay skills, la revisión es obligatoria (`montar.py` no acepta el montaje
sin ella), pero casi toda la hace un script. Después de la entrevista, con
`respuestas-espacio.json` ya escrito:

```bash
python <skill>/scripts/revisar.py --borrador     # arma la revisión y la deja en las respuestas
python <skill>/scripts/revisar.py --pendientes   # lo único que hay que validar buscando
```

`--borrador` audita, extrae qué hace cada skill, qué tareas cubre, sus reglas,
los problemas y contradicciones, y los datos que conviene validar. A ti te
toca solo lo que depende del rol: validar en fuentes oficiales los datos de
`--pendientes` (junto con la investigación del rol, paso 4), confirmar los
hallazgos dudosos y decidir con la persona. Detalle en
`references/skills-existentes.md`.

## Paso 3 — Entrevista

Abre con una frase: *«Voy a preparar tu espacio de trabajo. Son unas pocas
preguntas y no guardo nada hasta que me confirmes.»* Sigue
`references/entrevista.md`: una ronda abierta (cargo, proyecto y objetivo,
conocimientos, tareas, herramientas), como mucho una repregunta, y una ronda
cerrada con `AskUserQuestion` (uno o varios proyectos, destinatarios, trato,
historial de versiones).

## Paso 4 — Investigar el rol

Obligatorio antes de decidir la arquitectura. Con `references/investigar-rol.md`:
investiga a fondo el rol (responsabilidades, obligaciones, tareas comunes,
ciclos, métodos, riesgos y **programas que hay que tener instalados**) en
fuentes oficiales, cruzando al menos dos en lo que cambie la arquitectura.
Convierte los hallazgos en **lineamientos**: reglas de diseño con su porqué.
Anuncia en una frase que lo vas a hacer; no hace falta pedir permiso. Si no
hay internet o la persona no quiere, sigue con la entrevista y anota el motivo
en `limitacion`.

Git, Python, Node.js y Playwright ya los cubre `programas.py`. Para cada programa
adicional que pida el rol, comprueba si ya está instalado corriendo su comando
de versión: así la propuesta dice cuáles faltan.

## Paso 5 — Decidir la arquitectura

Con `references/arquitecturas.md` y los lineamientos del paso 4: tipo base
según lo que produce el trabajo, modo único o multiproyecto, carpetas extra
que justifique cada tarea o lineamiento (como mucho 7 en el primer nivel) y
adaptación a lo que ya existe. Deduce además los
accesos que harán falta (solo nombres de variable) y las categorías de
entregables. Escribe el porqué en una frase.

## Paso 6 — Proponer y confirmar

Escribe `respuestas-espacio.json` en la raíz (esquema en
`references/entrevista.md` § 5) y valida en seco:

```bash
python <skill>/scripts/montar.py --respuestas respuestas-espacio.json --dry-run
```

Código 2: corrige lo que diga la validación (si es un formato, tú; si falta
un dato, pregúntalo) y repite. Código 0: la propuesta en sencillo la escribe
un script; muéstrasela tal cual, sin reescribirla:

```bash
python <skill>/scripts/propuesta.py
```

Incluye esto (referencia de lo que genera):

> Así va a quedar tu espacio para **Tablero logístico**:
> - **Tus carpetas** (porque tu trabajo es convertir exportes del ERP en
>   indicadores semanales): *(árbol de primer y segundo nivel, con una
>   línea de para qué sirve cada carpeta)*
> - **Lo que voy a saber de ti:** tu cargo, tus tareas habituales y los temas
>   que debo dominar.
> - **Lo que encontré de tu rol:** responsabilidades y obligaciones (con sus
>   fuentes) y las reglas que salen de ahí para tu espacio. *«Es habitual en
>   tu rol hacer X; ¿también lo haces?»* para cada tarea común que no
>   mencionó: solo se suman las que confirme.
> - **Lo que ya tenías** (si el repositorio traía skills): qué hace cada uno,
>   qué conocimiento quedó validado y qué no, y los problemas encontrados
>   —primero los graves— con lo que propones para cada uno.
> - **Programas que vas a necesitar:** cuáles ya tienes y cuáles faltan, con
>   una línea de para qué sirve cada uno.
> - **Memoria:** anotaré lo que aprendamos y cada tarea que hagamos, para no
>   repetirte preguntas y para proponerte automatizar lo que se repita.
> - **Accesos que vamos a necesitar:** ERP (usuario de solo lectura). Te
>   explicaré cómo guardarlos de forma segura cuando toque.

`AskUserQuestion`: «Sí, prepáralo» · «Quiero cambiar algo» · «Ahora no». Con
cambios, ajusta el JSON y vuelve a este paso. Con «Ahora no», borra el JSON.
**No sigas sin un «Sí, prepáralo» en esta conversación.**

## Paso 7 — Montar y verificar

```bash
python <skill>/scripts/montar.py --respuestas respuestas-espacio.json
python <skill>/scripts/verificar.py
```

`montar.py` crea solo lo que falta y reporta cada pieza (`creado`, `ya
existía`, `mergeado`, `actualizado`, `omitido`, `error`); al final regenera la
memoria y el grafo. Es idempotente. El montaje **no** deja entrada en la
bitácora ni en la memoria: esas son solo del trabajo de la persona.

| Resultado | Qué hacer |
|---|---|
| `error` en `.claude/settings.json` | JSON roto: corrige la sintaxis sin quitar entradas y repite. A la persona: «un archivo de configuración estaba dañado; ya lo arreglé» |
| `omitido git` | Seguir; no mencionarlo |
| `verificar.py` con `AVISO credenciales/.env` | Normal mientras no haya valores |
| Cualquier `FALTA` o `DIVERGE` | Sección Reparar |

## Paso 8 — Contarle a la persona

Dos o tres frases, sin términos técnicos: que su espacio quedó listo, dónde
va a encontrar su trabajo, que cada tarea habitual ya tiene su atajo
(`/<tarea>`) y que nunca pegue claves en el chat. Luego muéstrale su lista de
arranque (`python <skill>/scripts/arranque.py`) en sencillo: cuánto lleva y
qué le falta para quedar al 100 %. Para ti: los
hooks se activan desde la próxima sesión de Claude Code.

## Paso 9 — Primeros pasos de verdad

Lo que sigue es completar la lista de arranque. Si el repositorio traía
skills, primero **reconstruye** (`references/skills-existentes.md` § 6): las
correcciones aprobadas, una por skill y con respaldo; el orden con
`ordenar.py`, moviendo solo lo que la persona confirme; y `auditar.py` otra
vez para comprobar que no queden problemas sin decidir.

Después ofrece, en una sola `AskUserQuestion` con selección múltiple, lo que
le falte (todo opcional), y pon primero **hacer su primera tarea real**:

- **Instalar los programas que faltan** (solo si `programas.py` marca
  alguno): uno por uno con `programas.py --instalar <nombre>` para los de
  base, y desde la fuente oficial para los del rol, diciendo antes qué se
  instala y para qué. Si un instalador pide permisos de administrador, se lo
  explicas y lo corre la persona (`! <orden>`). Al final, `programas.py` para
  confirmarlo.
- **Traer los documentos del proyecto** a la carpeta de contexto (briefs,
  manuales, contratos, datos de ejemplo). Leerlos completos y resumir en una
  línea qué aporta cada uno.
- **Investigar los conocimientos** de su perfil que aún no tengan memoria ni
  investigación: el protocolo de `docs/espacio-de-trabajo/investigacion.md`,
  empezando por el tema que más pese en sus tareas. Antes, dile cuántas
  búsquedas implica.
- **Revisar qué skills instalados cubren sus tareas habituales**: cruza cada
  tarea con `grafo.py --plan "<tarea>"` y dile cuáles ya tienen un skill y
  cuáles no. Las que no, quedan anotadas como candidatas.
- **Hacer su primera tarea real** con su atajo, aplicando ya el protocolo
  del espacio: reloj en marcha al empezar y, al cerrar, la pregunta de cuánto
  le habría tomado a mano. Que vea el tiempo ahorrado desde el primer día.

## Retirar el skill

Cuando el espacio queda listo (la lista de arranque al 100 %, o al terminar el
paso 9 si la persona no quiere seguir con la lista), ofrécele **una sola
vez** retirar este asistente; lo que creó no se toca. El aviso de inicio te
lo recuerda. Pregunta con `AskUserQuestion`:

- **Mantenerlo** (recomendado si va a sumar proyectos, cambiar de cargo o
  instalar más skills): sigue disponible para ampliar, reparar y revisar.
- **Desactivarlo**: deja de aparecer y las palabras «empezar» o «configurar»
  ya no lo abren. Todo sigue funcionando y se puede reactivar.
- **Eliminarlo**: sus herramientas del día a día pasan a `.claude/espacio/`
  y se borra el asistente. Para ampliar o reparar habrá que reinstalarlo con
  el comando de una línea.

```bash
python <skill>/scripts/retirar.py --desactivar   # o --eliminar, --reactivar, --estado
```

Corre `--desactivar` o `--eliminar` solo con su sí, y dile la frase que
devuelve el script.

## Reorganizar

Cuando el aviso de inicio dice que hay archivos fuera de lugar, o la persona
pide «ordena mis carpetas»:

1. `python <skill>/scripts/ordenar.py`: plan con el motivo y el destino
   propuesto de cada archivo (no mueve nada).
2. Muéstraselo en sencillo, archivo por archivo («`Informe final.docx` está
   suelto en la raíz; lo llevaría a `entregables/27-oct-2026/informes/`»).
3. **Pregunta siempre** con `AskUserQuestion` (selección múltiple con los
   movimientos, o «Sí, todos» · «Elegir uno por uno» · «No muevas nada»).
   **Ningún archivo se mueve sin confirmación**, ni siquiera uno solo.
4. `python <skill>/scripts/ordenar.py --aplicar --solo <rutas aprobadas>`.
   El hook `orden_check.py` hará que Claude Code pida permiso otra vez: es
   intencional.
5. Lo que no tenía destino se decide con la persona: registrarlo como carpeta
   nueva (Ampliar) o repartir su contenido.

Esta misma regla aplica fuera de `ordenar.py`: cualquier `mv`, `git mv`,
`Move-Item` o renombre de un archivo del espacio se confirma antes.

## Ampliar

Cuando hay `espacio.json` y cambia algo del trabajo: entrevista solo lo nuevo.
Si cambió el cargo, o se suman tareas de otro tipo, o el espacio no tiene
investigación del rol, vuelve a investigarlo (paso 4): la nueva queda con su
fecha y la anterior se conserva. Luego
lee el `espacio.json` actual, arma `respuestas-espacio.json` con el perfil
completo actualizado y lo que se suma (proyectos, carpetas, credenciales), y
sigue desde el paso 6. `montar.py` reemplaza el perfil y la investigación del
rol y **suma** carpetas, proyectos, credenciales y programas; nunca quita. Si el cambio pide quitar o mover
carpetas, se hace a mano con la persona (moverlas siempre se confirma).
Después, `montar.py --actualizar` para que `CLAUDE.md` refleje el perfil nuevo.

## Reparar

Dile en una frase que faltan piezas y que las repones sin tocar su trabajo
(`AskUserQuestion`: «Sí, repáralo» · «Ahora no»). Luego:

```bash
python <skill>/scripts/montar.py
python <skill>/scripts/verificar.py
```

Sin `--respuestas`, todo sale de `espacio.json`. Repone carpetas, plantillas,
líneas de `.gitignore` y hooks (útil si otra herramienta reemplazó
`.claude/settings.json`). Si `espacio.json` está roto o falta, vuelve a la
entrevista.

## Actualizar

Cuando este skill trae plantillas nuevas, los espacios ya montados conservan
las anteriores porque el montaje no sobrescribe. Con el permiso de la persona:

```bash
python <skill>/scripts/montar.py --actualizar
```

Rehace el bloque de `CLAUDE.md` y las convenciones, con copia previa en
`.espacio/respaldos/<fecha>/`. Lo que la persona escribió fuera de los
marcadores de `CLAUDE.md` no se toca. Si había editado una convención,
revisa la copia y vuelve a aplicar su cambio.

## Scripts

| Comando | Para qué |
|---|---|
| `montar.py --respuestas r.json [--dry-run]` | Montar o ampliar (`--actualizar`, `--json`, `--raiz`) |
| `verificar.py` | Estado: OK, FALTA, DIVERGE, AVISO (`--json`) |
| `revisar.py` | Borrador automático de la revisión de skills existentes (`--borrador`, `--pendientes`, `--resumen`) |
| `propuesta.py` | La propuesta del paso 6, en lenguaje sencillo y lista para mostrar |
| `inventario.py` | Skills, comandos, agentes, reglas, hooks y MCP que ya trae el repositorio (`--json`, `--cambios`, `--guardar`) |
| `auditar.py` | Problemas de seguridad, lógica, contradicciones y arquitectura en lo existente (`--json`, `--reglas`) |
| `retirar.py` | Desactivar, reactivar o eliminar este skill sin tocar lo que creó (`--estado`) |
| `activar.py` | Hook de activación por palabras (`--probar "texto"`, `--registrar`) |
| `programas.py` | Programas para trabajar: estado, `--comando <nombre>` y `--instalar <nombre>` (solo con el sí de la persona) |
| `arranque.py` | Lista de arranque: avance y cómo completar cada pendiente (`--breve`, `--json`) |
| `tiempo.py` | Reloj de una tarea del rol: `--empezar <proceso>`, `--terminar`, `--estimacion <proceso>` |
| `resumen.py` | Resumen semanal (`--dias`, `--hasta`, `--proyecto`, `--guardar`, `--json`) |
| `inicio.py` | Hook SessionStart: última sesión, peticiones abiertas, skills y anotaciones |
| `cierre_check.py` | Hook Stop: recuerda el protocolo de cierre una vez por sesión |
| `orden_check.py` | Hook PreToolUse: niega escrituras fuera de la arquitectura y pide confirmación para mover |
| `ordenar.py` | Plan de reorganización (`--aplicar --solo r1,r2` con confirmación, `--resumen`, `--json`) |
| `grafo.py --plan "<petición>" [--proyecto P]` | Qué abrir antes de una tarea (`--actualizar`) |
| `bitacora.py [--proyecto P]` | Validar (`--siguiente`, `--tabla`) |
| `memoria.py` | Validar la memoria (`--rebuild`) |

## Archivos de este skill

| Archivo | Cuándo leerlo |
|---|---|
| `references/entrevista.md` | Pasos 3 y 6: preguntas, inferencias y esquema del JSON |
| `references/investigar-rol.md` | Paso 4: qué investigar del rol, cómo convertirlo en lineamientos y el bloque `investigacion_rol` |
| `references/arquitecturas.md` | Paso 5: cómo decidir y los seis tipos |
| `references/skills-existentes.md` | Pasos 2, 4, 6 y 9: revisar, validar y adaptar lo que ya traía el repositorio |
| `plantillas/` | Lo que renderiza `montar.py` (CLAUDE.md, perfil, bitácora, atajos, hooks). No se edita por proyecto |
| `convenciones/` | Las reglas del espacio que se copian a `docs/espacio-de-trabajo/` |
