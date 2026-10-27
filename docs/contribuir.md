# Contribuir

## Estructura del repositorio

```
skill/                    lo que se instala en .claude/skills/primeros-pasos/
  SKILL.md                instrucciones para Claude
  references/             entrevista, arquitecturas, investigación del rol, skills existentes
  plantillas/             lo que renderiza montar.py: CLAUDE.md, perfil, bitácora, atajos, hooks
  convenciones/           reglas que se copian a docs/espacio-de-trabajo/ en cada espacio
  scripts/                todo lo mecánico, en Python 3.10+ con biblioteca estándar
install.sh, install.ps1   instaladores de una línea
docs/                     guía de uso, diagrama y esta página
tests/prueba_completa.py  prueba de punta a punta en carpetas temporales
```

## Principios

- El skill es agnóstico: nada de nombres de empresa, cliente, área o
  herramienta dentro de `skill/`, salvo los programas de base (Python,
  Node.js y Playwright).
- Lo que se puede decidir con un script se hace con un script. Claude solo
  pone criterio donde depende del rol de la persona.
- Todo lo que ve la persona va en español, sin términos técnicos y con fechas
  en formato `10-oct-2026`.
- Las reglas que el espacio hace cumplir (confirmar antes de mover, rutas de
  como mucho 6 niveles, 150 caracteres y nombres de 60, credenciales fuera
  del chat) no se relajan sin pedirlo.

## Pruebas

```bash
python tests/prueba_completa.py -q   # debe terminar con «ninguno»
```

Monta cuatro espacios temporales y recorre la validación, el montaje, la
memoria, la bitácora, el grafo, los hooks, los límites de ruta, la
reorganización, la revisión de skills existentes, el cierre de tareas, el
resumen, el retiro del skill y los dos instaladores. Si un cambio agrega
comportamiento, se agrega su caso a la prueba.
