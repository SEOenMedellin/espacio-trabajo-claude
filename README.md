# primeros-pasos

Skill para [Claude Code](https://claude.com/claude-code) que prepara el espacio
de trabajo de cualquier persona en cualquier repositorio. Entrevista a quien
va a trabajar (cargo, proyecto y objetivo, conocimientos que Claude debe tener,
tareas habituales, herramientas), **decide qué arquitectura de carpetas
necesita según su objetivo** y la monta con todo lo que hace falta para que
Claude trabaje con contexto y aprenda de cada tarea.

No asume área, empresa ni herramienta: todo sale de la entrevista.

## Qué deja montado

| Pieza | Para qué |
|---|---|
| Arquitectura de carpetas | Una de seis bases (entregables a clientes, software, datos, contenido, gestión, investigación), ajustada a las tareas de la persona y a lo que ya existe en el repositorio |
| `CLAUDE.md` | Perfil, mapa de carpetas y protocolo de trabajo, en un bloque propio que respeta lo que ya hubiera |
| `espacio.json` | La configuración: perfil, arquitectura y rutas. Todo lo demás se deriva de aquí |
| Bitácora de trabajo | Una entrada por tarea del rol, con patrones, conocimiento adyacente y correcciones |
| Memoria | Un nodo por cosa resuelta (global y por proyecto), con índice regenerable |
| Grafo de orquestación | `grafo.py --plan "<petición>"` dice qué skills, memoria, contexto y tareas previas abrir antes de actuar |
| Investigación profunda | Protocolo para tareas sin antecedentes: desglose, fuentes oficiales, supuestos explícitos, resultado reutilizable |
| Creación de skills | Los procesos que se repiten o se corrigen se proponen como skills nuevos |
| Credenciales | `credenciales/.env` fuera de git; los secretos nunca pasan por el chat |
| Hooks | Al iniciar: última sesión, tareas abiertas, catálogo de skills, memoria y orden. Al escribir: bloquea archivos fuera de la arquitectura. Al mover: pide confirmación. Al cerrar: recuerda registrar la tarea |

## Reglas que el espacio hace cumplir

- **Solo se documenta el trabajo del rol.** La bitácora, la memoria y el grafo
  nunca registran configuración, carpetas, credenciales, skills ni nada del
  propio sistema.
- **El repositorio no se deforma.** Crear un archivo fuera del mapa se bloquea
  y el aviso dice dónde va; `ordenar.py` propone a dónde va cada archivo según
  su contenido y uso.
- **Mover siempre se confirma.** Ningún archivo se mueve ni se renombra sin un
  sí explícito de la persona.
- **Rutas cortas.** Como mucho 6 niveles, 150 caracteres dentro del repositorio
  y nombres de 60, para que nada falle en Windows ni en macOS.
- **Fechas** en formato `10-oct-2026`.

## Requisitos

- Claude Code.
- Python 3.10 o superior (solo biblioteca estándar: no hay nada que instalar con pip).

## Instalación

Copia la carpeta `skill/` dentro del repositorio donde vas a trabajar, con el
nombre `primeros-pasos`:

```bash
# desde la raíz de tu repositorio
mkdir -p .claude/skills
cp -r /ruta/a/espacio-trabajo-claude/skill .claude/skills/primeros-pasos
```

En Windows (PowerShell):

```powershell
New-Item -ItemType Directory -Force .claude\skills | Out-Null
Copy-Item -Recurse C:\ruta\a\espacio-trabajo-claude\skill .claude\skills\primeros-pasos
```

Abre Claude Code en ese repositorio y escribe **«empezar»**. La entrevista
toma unos minutos y no se escribe nada hasta que confirmes la propuesta.

> Se instala por repositorio, no en `~/.claude/skills`: los hooks guardan la
> ruta del skill, y cada espacio de trabajo debe tener la suya.

## Uso después del montaje

| Pide… | Qué pasa |
|---|---|
| «empezar» o «primeros pasos» | Entrevista y montaje (o revisión, si ya está montado) |
| «tengo un proyecto nuevo», «cambió mi cargo», «ahora también hago…» | Amplía el espacio: suma carpetas y proyectos sin quitar nada |
| «ordena mis carpetas» | Plan de reorganización; solo se mueve lo que apruebes |
| «repara mi espacio» | Repone piezas que falten (por ejemplo, hooks borrados por otra herramienta) |

## Estructura de este repositorio

```
skill/                    el skill (lo que se copia a .claude/skills/primeros-pasos/)
  SKILL.md                instrucciones para Claude
  references/             entrevista y catálogo de arquitecturas
  assets/plantilla/       CLAUDE.md, convenciones, bitácora, hooks que se renderizan
  scripts/                montar, verificar, inicio, cierre, orden, ordenar, grafo, bitácora, memoria
tests/prueba_completa.py  prueba de punta a punta en carpetas temporales
```

## Pruebas

```bash
python tests/prueba_completa.py -q
```

Monta dos espacios temporales (un proyecto con código previo y varios
proyectos) y recorre validación, montaje, idempotencia, memoria, bitácora,
grafo, los tres hooks, los límites de ruta, la reorganización y la ampliación.

## Licencia

MIT. Ver [LICENSE](LICENSE).
