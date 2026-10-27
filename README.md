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

Luego abre Claude Code en esa carpeta y escribe **«empezar»**. Eso es todo.

## Por qué vas a querer tenerlo

Claude es muy capaz, pero empieza cada conversación sin saber nada de ti. Le
repites tu contexto, le corriges lo mismo que ayer, guarda archivos donde no
van y lo que resolvió la semana pasada se pierde. **primeros-pasos acaba con
eso.**

| Sin primeros-pasos | Con primeros-pasos |
|---|---|
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
| «tengo un proyecto nuevo» o «ahora también hago…» | Tu espacio se amplía sin perder nada |
| «ordena mis carpetas» | Te propone dónde va cada archivo; solo se mueve lo que apruebes |
| «repara mi espacio» | Repone lo que falte si algo se dañó |

## Lo que necesitas

- [Claude Code](https://claude.com/claude-code).
- [Python 3.10 o superior](https://www.python.org/downloads/). No hay que
  instalar nada más; el instalador te avisa si falta.

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
