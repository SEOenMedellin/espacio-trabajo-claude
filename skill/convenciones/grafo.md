# Grafo de orquestación

`grafo.py` cruza cinco fuentes para decidir qué abrir antes de una tarea:

| Fuente | De dónde |
|---|---|
| Skills | `.claude/skills/*/SKILL.md` (nombre y descripción) |
| Memoria | `{{MEMORIA_GLOBAL}}` y `{{MEMORIA_PROYECTO}}` |
| Contexto | `{{CONTEXTO}}` |
| Investigaciones | `{{INVESTIGACION}}` |
| Peticiones | `{{BITACORA}}` (y los skills, nodos y archivos que usó cada una) |

El grafo solo conoce trabajo del rol: como la bitácora y la memoria no
registran nada del sistema, tampoco aparece en el plan.

```bash
{{PY}} {{SKILL_REL}}/scripts/grafo.py --plan "<la petición>"{{PROYECTO_FLAG}}
{{PY}} {{SKILL_REL}}/scripts/grafo.py --actualizar
```

- `--plan` es obligatorio antes de la primera acción de cada tarea. Lo que
  marque como skill se invoca con la herramienta `Skill`: conocer el nombre de
  un script no reemplaza invocar el skill.
- Si el plan marca algo que no corresponde, o no aplica ningún skill, se dice
  explícitamente antes de seguir a mano.
- Si dice «sin antecedentes», se aplica `investigacion.md`.
- `--actualizar` después de crear o mover archivos. Su salida
  (`.espacio/grafo.json`) es derivada: si diverge del disco, gana el disco.

La búsqueda es por palabras, no semántica. Para que el grafo encuentre las
cosas: títulos descriptivos en los nodos y en las entradas de la bitácora, y
el mismo `proceso` para tareas del mismo tipo.
