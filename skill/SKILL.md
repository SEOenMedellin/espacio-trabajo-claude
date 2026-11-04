---
name: primeros-pasos
description: >
  Configuración inicial del espacio de trabajo de un colaborador en la carpeta
  donde se instala, esté donde esté, para cualquier cargo y proyecto. Lee todo
  lo que ya hay en la carpeta (documentos, hojas, presentaciones) e instala
  las skills que encuentre sueltas; luego entrevista a la persona (cargo,
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

# Primer Paso

Prepara un espacio de trabajo hecho a la medida de quien lo va a usar. No
asume área, empresa ni herramienta: todo sale de la entrevista. El resultado
es un repositorio en el que Claude sabe quién es la persona, qué hace, dónde
va cada cosa, qué se resolvió antes y cómo aprender de cada tarea.

## Qué deja montado

| Pieza | Para qué |
|---|---|
| `espacio.json` | La configuración: perfil, arquitectura y rutas de cada rol. Todo lo demás se deriva de aquí |
| Lo que había en la carpeta | Cada documento que la persona ya tenía, leído, con lo que aporta y lo aprendido (`<contexto>/lo-que-habia-en-la-carpeta.md`); las skills sueltas quedan instaladas en `.claude/skills/` |
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

**Es un acompañamiento, no un formulario.** Supón que la persona no es técnica
hasta que demuestre lo contrario, y que cualquier tropiezo puede hacer que
abandone:

- **Su lenguaje manda.** Toma las palabras que usa para su trabajo, sus
  archivos y sus tareas, y úsalas tú. Si escribe corto e informal, responde
  corto e informal; si usa términos de su oficio, úsalos con naturalidad. Si
  muestra dominio técnico, sube el nivel; si duda o pregunta qué significa
  algo, bájalo y explícalo con un ejemplo de su propio trabajo.
- **Un paso a la vez.** Cada mensaje dice qué está pasando, qué sigue y qué
  tiene que hacer ella, si algo. Nada de listas largas de opciones técnicas ni
  de comandos para que los ejecute: los ejecutas tú.
- **Los errores no llegan a la persona.** Si un comando, un programa o un
  script falla, resuélvelo tú (otra vía, otro intérprete, instalar lo que
  falte con su permiso) y cuéntale en una frase sencilla lo que pasó y que ya
  está resuelto. Solo si hace falta algo que solo ella puede hacer (una
  contraseña, aceptar una ventana del sistema, aprobar una instalación), pídelo
  con instrucciones exactas de qué ver y dónde hacer clic.
- **Celebra el avance.** Al cerrar cada paso, dile en una línea qué quedó listo
  y cuánto falta, para que sepa que va bien.

Este skill **nunca**: borra ni mueve archivos de la persona, sobrescribe un
archivo existente (el bloque de `CLAUDE.md` solo se rehace con
`--actualizar`, y con copia previa), quita entradas de
`.claude/settings.json`, pide o escribe valores de credenciales, agrega
remotos de git ni publica nada fuera del repositorio.

## Cuándo corre

| Situación | Ir a |
|---|---|
| No hay `espacio.json` en la raíz | Montaje completo, pasos 1 a 9 |
| Hay skills en la carpeta sin instalar en `.claude/skills/` | `explorar.py --instalar-skills` (obligatorio), y luego la fila siguiente |
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

## Paso 2 — Conocer la carpeta

La carpeta donde se instaló el skill es la de la persona, esté en la ruta que
esté. Todo lo que ya tiene ahí es la primera fuente: se lee **antes** de
preguntar nada, y la entrevista solo confirma lo que se dedujo y pregunta lo
que falte.

```bash
python <skill>/scripts/explorar.py
```

Muestra cuántos archivos hay y de qué tipo, las carpetas, lo más reciente, lo
que se repite (pistas de tareas habituales: `informe-ventas` cada mes), los
documentos en orden de prioridad con un extracto de cada uno, los archivos
que pueden tener claves (nunca se leen ni se abren) y las skills sin instalar.

1. **Skills sin instalar (obligatorio).** Si la carpeta trae skills fuera de
   `.claude/skills/<nombre>/` (una carpeta con `SKILL.md` en cualquier parte,
   o un `.skill` o `.zip` que la contenga), instálalas antes de seguir. Copia
   cada una a `.claude/skills/<nombre>/` sin tocar el original:

   ```bash
   python <skill>/scripts/explorar.py --instalar-skills
   ```

   Si una choca con otra instalada distinta del mismo nombre, no se toca:
   pregúntale a la persona cuál vale. `montar.py` no acepta el montaje
   mientras quede alguna sin instalar, y `verificar.py` lo marca como
   `FALTA` si aparece una después. Ya instaladas, entran en la revisión de
   skills de abajo como cualquier otra.
2. **Leer los documentos.** Léelos completos, en el orden que da el script:
   los de texto y PDF con `Read`, y los `.docx`, `.xlsx`, `.pptx` y `.odt`
   con `explorar.py --texto "<ruta>"`. De las hojas de cálculo basta con
   las hojas, los encabezados y unas filas. Si son muchos (más de 40),
   lee completos los que más pesan (los que el script pone primero, los más
   recientes y uno de cada grupo que se repite) y del resto, el extracto;
   lo que no leas va en `sin_leer` con su motivo («fotos del evento»,
   «exportes mensuales con la misma estructura que el de marzo»).
3. **Sacar conclusiones.** De lo leído, anota qué dice la carpeta del cargo,
   el proyecto y su objetivo, las tareas habituales (lo que se repite), lo
   que se entrega y a quién, las herramientas (por los tipos de archivo y lo
   que mencionan los documentos), los conocimientos que exige, las personas
   u organizaciones que aparecen y los accesos que harán falta. Solo lo que
   el material dice: lo que no esté escrito se pregunta, no se supone.
4. **Guardarlo para el montaje** en el bloque `carpeta` de
   `respuestas-espacio.json` (`references/entrevista.md` § 6): cada documento
   leído con lo que aporta, lo aprendido y lo que no se leyó con su motivo.
   `montar.py` lo exige cuando la carpeta tiene documentos (cada uno, leído o
   justificado) y lo deja en `<contexto>/lo-que-habia-en-la-carpeta.md`.

Si la carpeta está vacía, todo sale de la entrevista. Si ya hay `README`,
`CLAUDE.md` o código, también sirven para el paso 4 de
`references/arquitecturas.md` (adoptar lo que existe, no mover nada).

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

Sigue `references/entrevista.md`. En corto:

1. **Apertura:** por qué importa lo que vas a preguntar (para ayudarle en su
   cargo: qué temas dominar, cómo ordenar sus carpetas, qué tareas hacer con
   él desde el primer día) y qué pasa con sus datos: se usan solo para eso,
   quedan en su carpeta, no se publican ni se comparten con otras personas.
   Nunca digas que la IA no los ve.
2. **Invitación opcional** a compartir su hoja de vida en PDF, su perfil de
   LinkedIn descargado en PDF o un enlace o documento del proyecto. De la
   hoja de vida solo se saca lo profesional; sus habilidades se cruzan con lo
   que exige el rol (paso 4).
3. **Si la carpeta o los archivos ya lo dicen**, muéstrale lo que entendiste
   (cinco o seis líneas) y confírmalo con una opción.
4. **Como mucho dos preguntas abiertas de una línea** (cargo; proyecto y
   objetivo), solo si no se saben.
5. **El resto, para elegir:** dos `AskUserQuestion` como mucho (tareas,
   entregables, herramientas y temas; luego modo, destinatarios, trato e
   historial), con opciones armadas con lo que ya se sabe.

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
`references/entrevista.md` § 6) y valida en seco:

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
> - **Lo que aprendí de tu carpeta** (si tenía material): cuántos documentos
>   leí, lo que entendí de ellos y lo que no leí, con su motivo.
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
- **Traer los documentos que falten** a la carpeta de contexto (briefs,
  manuales, contratos, datos de ejemplo que no estaban en la carpeta). Leerlos
  completos y sumar a `lo-que-habia-en-la-carpeta.md` una línea de qué aporta
  cada uno.
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

Si `verificar.py` marca una `skill` sin instalar, primero
`explorar.py --instalar-skills` y su revisión (`references/skills-existentes.md`).
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
| `explorar.py` | Lo que hay en la carpeta antes de la entrevista (`--json`, `--texto <ruta>`, `--skills`, `--instalar-skills`) |
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
