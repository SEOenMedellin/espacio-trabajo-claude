# espacio-trabajo-claude

Repositorio de desarrollo del skill `primeros-pasos`. Es independiente:
las reglas de otros `CLAUDE.md` de carpetas superiores no aplican aquí,
aunque Claude Code las cargue.

## Reglas

- **La fuente es `skill/`.** Es lo que se copia a `.claude/skills/primeros-pasos/`
  en los repositorios de los usuarios. No se instala en este repositorio.
- **Totalmente agnóstico.** Nada de nombres de empresa, cliente, área,
  dominio o herramienta concreta dentro de `skill/`: todo sale de la entrevista.
  Los ejemplos de la documentación son genéricos. La única excepción son los
  programas de base para trabajar (Git, Python, Node.js y Playwright), que el skill
  y los instaladores revisan e instalan con confirmación.
- **Todo lo que ve el usuario va en español.** Fechas en formato `10-oct-2026`.
- **Solo biblioteca estándar de Python 3.10+.** Nada que instalar con pip
  para que los scripts del skill funcionen.
- **Las reglas que el skill hace cumplir no se relajan sin pedirlo:** solo se
  documenta el trabajo del rol, mover siempre se confirma, nada se escribe
  fuera de la arquitectura, rutas de como mucho 6 niveles, 150 caracteres y
  nombres de 60.
- **Antes de cada commit:** `python tests/prueba_completa.py -q` debe terminar
  con «ninguno». Si un cambio agrega comportamiento, se agrega su caso a la prueba.
- **Publicar** (GitHub, releases) solo después de mostrar la versión final y
  recibir confirmación explícita.
- Los cambios al skill no se registran en bitácoras ni memorias: su historial
  son los commits.
