# primeros-pasos

**Deja de explicarle a Claude quién eres cada vez que abres una conversación.**

Un skill para [Claude Code](https://claude.com/claude-code) que en unos
minutos convierte cualquier carpeta en tu espacio de trabajo: ordenado a tu
medida, con Claude sabiendo qué haces y para qué, y con una memoria que crece
con cada tarea.

![Cómo funciona primeros-pasos](docs/como-funciona.svg)

## Instálalo en una línea

Abre una terminal **en la carpeta de tu proyecto** y pega el comando de tu
sistema.

**Mac y Linux**

```bash
curl -fsSL https://raw.githubusercontent.com/davidortiz-ops/espacio-trabajo-claude/main/install.sh | bash
```

**Windows (PowerShell)**

```powershell
irm https://raw.githubusercontent.com/davidortiz-ops/espacio-trabajo-claude/main/install.ps1 | iex
```

Luego abre Claude Code en esa carpeta y escribe **«empezar»** (o «iniciar», «configurar», «empecemos»). Eso es todo.

## Por qué vas a querer tenerlo

Claude es muy capaz, pero empieza cada conversación sin saber nada de ti. Le
repites tu contexto, le corriges lo mismo que ayer, guarda archivos donde no
van y lo que resolvió la semana pasada se pierde. **primeros-pasos acaba con
eso.**

| Sin primeros-pasos | Con primeros-pasos |
|---|---|
| No sabes cuánto tiempo te ahorra la IA | Cada tarea te dice cuánto ahorraste, y cada semana lo suma |
| Cada conversación empieza de cero | Claude arranca sabiendo tu cargo, tu objetivo y cómo trabajas |
| Explicas lo mismo una y otra vez | Lo dices una vez en la entrevista y queda escrito |
| Archivos regados por todas partes | Cada cosa tiene su lugar, y Claude lo respeta |
| Lo que ya se resolvió se vuelve a investigar | Claude revisa primero lo que ya se sabe |
| El mismo error vuelve a aparecer | Cada corrección queda registrada para la próxima |
| Claves y contraseñas pegadas en el chat | Tus accesos quedan guardados aparte, nunca en la conversación |

## Hecho para tu trabajo, no para uno genérico

No es una plantilla. primeros-pasos te hace una entrevista corta (tu cargo, en
qué proyecto estás, qué quieres lograr, qué tareas haces y con qué
herramientas) y a partir de ahí **decide qué estructura te sirve**:

- ¿Entregas trabajo a clientes? Una carpeta por cliente, con su historial.
- ¿Desarrollas software? Tu código intacto y el contexto al lado.
- ¿Analizas datos? Datos crudos, procesados y reportes separados.
- ¿Creas contenido, gestionas equipos o investigas? También hay una base para eso.

Si ya tienes archivos, se respetan. Si mañana cambian tus tareas o llega un
proyecto nuevo, el espacio crece contigo sin perder nada.

## ¿Ya tienes habilidades instaladas? Las aprovecha

Si tu repositorio no está en blanco, primeros-pasos **revisa todo lo que ya
tiene** antes de proponerte nada: habilidades (skills), comandos, reglas y
conexiones.

- **Las entiende y las aprovecha.** Sabe qué hace cada una y qué tareas tuyas
  cubre. Esas tareas siguen usando tu habilidad; no te duplica nada.
- **Comprueba lo que saben.** Las normas, versiones y cifras que usan se
  validan en fuentes oficiales, y lo que esté desactualizado se te avisa.
- **Te cuida.** Te avisa si alguna guarda una contraseña a la vista, envía
  información fuera de tu equipo, puede borrar trabajo, se contradice con otra
  o guarda archivos fuera de tu orden.
- **Lo arregla contigo.** Te propone cada corrección en sencillo y solo la
  aplica si dices que sí, con copia de seguridad antes.
- **Sigue atento.** Si mañana instalas una habilidad nueva o cambia alguna,
  te lo dice al empezar la sesión y la revisa. También puedes pedirlo:
  «revisa mis skills».

Todo lo mecánico lo hacen sus propios scripts, así que es rápido y gasta
poco: Claude solo dedica su criterio a lo que depende de tu rol.

## Conoce tu oficio antes de organizarte

Lo que cuentas en la entrevista es solo una parte. Antes de proponerte nada,
primeros-pasos **investiga a fondo tu rol** en fuentes oficiales:

- **Responsabilidades:** de qué respondes y cómo se mide tu trabajo.
- **Obligaciones:** normas que te rigen, registros que debes conservar e
  información que debes proteger. Son las que más se olvidan y las que más
  pesan cuando faltan.
- **Tareas comunes de tu rol:** te pregunta por las que no mencionaste, y solo
  se suman las que de verdad haces.
- **Programas que necesitas:** además de Python, Node.js y Playwright, que
  vienen de base, los que pida tu rol; cuáles ya tienes y cuáles faltan. Te ofrece instalarlos, uno por
  uno y con tu permiso, y te avisa al empezar cada sesión si falta alguno.

De ahí salen **los lineamientos de tu espacio**: reglas con su porqué que
deciden tus carpetas y que Claude respeta en cada tarea. La investigación
queda guardada con sus fuentes, para que puedas revisarla cuando quieras.

## Tus tareas, a un comando de distancia

Cada tarea que haces seguido se convierte en un **atajo con nombre propio**:
`/informe-mensual`, `/acta-de-reunion`, `/revision-de-contrato`. Lo escribes y
Claude sigue siempre los mismos pasos, con el formato de tu oficio y las
correcciones que ya le hiciste. La primera vez aprende cómo la haces; desde la
segunda, sale igual sin volver a explicar nada.

## Mide cuánto tiempo te ahorras

Al terminar cada tarea de tu trabajo (un informe, una investigación, un
análisis), Claude te hace una sola pregunta: **¿cuánto te habría tomado
hacerlo a mano?** Lo compara con lo que tomó con él y te lo dice en una
frase:

> Con Claude: 25 min; a mano: 2 h. Te ahorraste 1 h 35 min.

La segunda vez que haces el mismo tipo de tarea ya no tienes que pensarlo: te
propone tu estimación anterior. Configurar el espacio o crear atajos nunca
cuenta como tarea; solo se mide tu trabajo de verdad.

## Tu semana, en un resumen

Cada semana Claude te ofrece un resumen listo para ti o para tu jefe:

- **Qué hiciste**, tarea por tarea.
- **Cuánto tiempo ahorraste**, en total y por tipo de tarea, y lo acumulado
  desde que empezaste.
- **Qué aprendió Claude** y **qué le corregiste**.
- **Qué quedó pendiente.**
- **Qué se repite** lo suficiente para volverse un atajo.

Si lo quieres guardar o compartir, queda como un documento más de tu trabajo.

## Al 100 % desde el primer día

Después de instalar, una **lista de arranque** te muestra cuánto llevas y qué
falta: investigar tu rol, instalar un programa, guardar un acceso, traer los
documentos de tu proyecto, hacer tu primera tarea. Cada vez que abres Claude
ves tu avance («Arranque: 5 de 7 listo»); escribe **«sigamos»** y te ayuda
con lo siguiente. La primera tarea la hacen juntos, para que veas el tiempo
que ahorras desde el primer día.

## Un espacio que aprende

Esto es lo que lo hace distinto: **mejora cuanto más lo usas.**

- **Memoria.** Cada cosa que se resuelve queda guardada. La próxima vez,
  Claude la encuentra antes de empezar a buscar.
- **Bitácora.** Cada tarea queda registrada con lo que funcionó y lo que hubo
  que corregir.
- **Nuevas habilidades.** Cuando una tarea se repite, Claude te propone
  convertirla en un skill propio para hacerla igual de bien cada vez.
- **Investigación con método.** Ante algo nuevo, Claude separa el problema,
  busca fuentes confiables y deja el resultado listo para reutilizarlo.

## Tú tienes el control

- **Nada se crea sin tu visto bueno.** Primero ves la propuesta, después se monta.
- **Nada se mueve ni se renombra sin un sí explícito.**
- **Nada se borra ni se sobrescribe.** Lo que ya tenías sigue ahí.
- **Tus claves no pasan por el chat.** Se guardan en un archivo fuera de git.
- **Todo queda en tu equipo.** No hay servidores, cuentas ni nada que pagar.

## Qué le puedes pedir

| Escribe… | Y pasa esto |
|---|---|
| «empezar» | Entrevista y montaje de tu espacio |
| `/<tu-tarea>` | Tu tarea habitual, siempre con los mismos pasos |
| «sigamos» | Completa lo siguiente de tu lista de arranque |
| «revisa mis skills» | Revisa, valida y adapta las habilidades que ya tienes |
| «¿cómo me fue esta semana?» | Tu resumen: tareas, tiempo ahorrado y lo aprendido |
| «tengo un proyecto nuevo» o «ahora también hago…» | Tu espacio se amplía sin perder nada |
| «ordena mis carpetas» | Te propone dónde va cada archivo; solo se mueve lo que apruebes |
| «repara mi espacio» | Repone lo que falte si algo se dañó |

## Lo que necesitas

- [Claude Code](https://claude.com/claude-code).
- [Python 3.10 o superior](https://www.python.org/downloads/),
  [Node.js 18 o superior](https://nodejs.org/) y
  [Playwright](https://playwright.dev/). No tienes que buscarlos: el instalador
  revisa cuáles faltan y te ofrece instalarlos (con winget en Windows,
  Homebrew en Mac, apt o dnf en Linux). Nada se instala sin que digas que sí.

## Preguntas frecuentes

**¿Sirve para mi área?**
Sí. No asume empresa, área ni herramienta: todo sale de la entrevista. Funciona
igual para quien hace consultoría, desarrollo, análisis, contenido o gestión.

**¿Lo instalo una vez para todos mis proyectos?**
Se instala por proyecto: cada carpeta tiene su propio espacio. Ejecuta el
comando de instalación dentro de cada proyecto donde lo quieras.

**¿Cómo lo actualizo?**
Vuelve a ejecutar el mismo comando de instalación. Se reemplaza el skill y tu
trabajo (carpetas, memoria, bitácora) no se toca.

**¿Cómo lo quito?**
Borra la carpeta `.claude/skills/primeros-pasos` y las entradas de `hooks` que
apuntan a ella en `.claude/settings.json`. Tus carpetas y notas se quedan.

**Prefiero no ejecutar un script descargado.**
Es comprensible. Revisa antes [`install.sh`](install.sh) o
[`install.ps1`](install.ps1), o instálalo a mano: copia la carpeta `skill/` de
este repositorio en `.claude/skills/primeros-pasos` dentro de tu proyecto.

## Para quien quiera contribuir

```
skill/                    el skill: lo que se instala en .claude/skills/primeros-pasos/
install.sh, install.ps1   instaladores de una línea
docs/                     material de la documentación
tests/prueba_completa.py  prueba de punta a punta en carpetas temporales
```

```bash
python tests/prueba_completa.py -q   # debe terminar con «ninguno»
```

## Licencia

MIT. Ver [LICENSE](LICENSE).
