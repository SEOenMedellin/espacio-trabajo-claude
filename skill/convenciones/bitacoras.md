# Bitácora de trabajo y protocolo de cierre

`{{BITACORA}}` registra **el trabajo de la persona en su rol**: una entrada
por tarea de su cargo, qué se pidió y cómo se resolvió.

## Qué entra y qué no

| Sí se registra | Nunca se registra |
|---|---|
| Tareas de su cargo: análisis, entregables, investigaciones, decisiones del negocio o del cliente | Configurar el espacio, crear o reordenar carpetas |
| Lo aprendido del oficio, del cliente o de las herramientas que usa en su trabajo | Credenciales, accesos, hooks, scripts, skills creados |
| Correcciones sobre cómo quiere el trabajo | Cualquier cosa sobre el desarrollo de este sistema |

Si una sesión solo tocó el sistema, no deja entrada ni nodo de memoria.

## La bitácora

**Por qué existe.** Es la fuente del grafo: lo que se pide, con qué se
resolvió y qué se corrigió. Y sirve para **destilar procesos**: cuando un
mismo `proceso` aparece dos o más veces, o tuvo una corrección, es candidato a
nodo de memoria o a skill.

### Formato exacto

Las entradas van bajo `## Entradas`, antes de `## Procesos candidatos`:

```markdown
### P-NNN — <título corto>
<!-- fecha: DD-mmm-YYYY | skills: a, b | memoria: id1, id2 | archivos: ruta1, ruta2 | proceso: <slug> | estado: resuelta | manual: 120 | claude: 25 -->

**Petición:** qué pidió la persona, con sus palabras.

**Cómo se resolvió:** pasos y decisiones, en pocas líneas.

**Patrones y atajos:** lo que ahorra tiempo si se repite.            (opcional)

**Conocimiento adyacente:** restricciones o dependencias que nadie
mencionó pero que importan para próximas tareas.                     (opcional)

**Corrección del usuario:** solo si la hubo.                         (opcional)
```

- `P-NNN` sale de `bitacora.py --siguiente{{PROYECTO_FLAG}}`. El separador del título es
  una raya (—), no un guion.
- La línea de metadatos va justo debajo del título; los campos vacíos se dejan
  vacíos (`memoria: `), no se omiten.
- `proceso`: slug kebab-case del **tipo** de tarea (`informe-mensual`,
  `revisar-contrato`), no de esta tarea. Antes de inventar uno, reutiliza un
  slug de la tabla si la tarea es del mismo tipo: así se cuentan las repeticiones.
- `estado`: `resuelta`, `parcial` o `abierta`.
- `manual` y `claude`: minutos enteros. `manual` es lo que la persona estima
  que le tomaría a mano, en promedio; `claude`, lo que tomó con Claude
  (`tiempo.py --terminar`). Si la persona no quiso responder, se dejan fuera.
  De aquí salen el tiempo ahorrado y el resumen semanal.
- Si la tarea se hizo con un atajo, `proceso` es el nombre del atajo: así se
  cuentan juntas todas las veces que se hizo.

### Protocolo de cierre

Al terminar **cada tarea del trabajo de la persona** (no cada mensaje, y nunca
por tareas de configuración del espacio ni por crear skills): una frase a la
persona con qué se hizo y qué se va a recordar, y una sola `AskUserQuestion`
con dos preguntas: «¿Lo guardo así para la próxima vez?» (Sí, guárdalo ·
Corrige algo · No hace falta) y «¿Cuánto te habría tomado hacerlo a mano, en
promedio?». Para la segunda, si ya hay una estimación de ese tipo de tarea
(`tiempo.py --estimacion <proceso>`), se le propone primero; la persona puede
cambiarla. Luego `tiempo.py --terminar` da el tiempo con Claude y se le dice
en una frase cuánto se ahorró.

- *Corrige algo*: se ajusta y se guarda. Las correcciones son la señal más
  valiosa: siempre van en la entrada y casi siempre se vuelven un nodo
  (`preferencia` o `decision`).
- *No hace falta*: no se escribe nada.

Después del sí, en silencio:

```bash
{{PY}} {{SKILL_REL}}/scripts/bitacora.py --siguiente{{PROYECTO_FLAG}}
# … escribir la entrada …
{{PY}} {{SKILL_REL}}/scripts/bitacora.py --tabla{{PROYECTO_FLAG}}
{{PY}} {{SKILL_REL}}/scripts/memoria.py --rebuild      # si hubo nodo
{{PY}} {{SKILL_REL}}/scripts/grafo.py --actualizar
```

La tabla «Procesos candidatos» se genera, no se escribe: una tabla mantenida
a mano deja de actualizarse y miente sobre qué se repite. Solo la columna
«Decisión» es manual.

El hook `Stop` (`cierre_check.py`) lo recuerda una vez por sesión si cambiaron
archivos de trabajo y la bitácora no se tocó. Si la tarea sigue abierta, se
ignora: no se repite.

