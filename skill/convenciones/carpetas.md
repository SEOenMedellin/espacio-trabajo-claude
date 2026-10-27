# Carpetas y entregables

La arquitectura de este espacio («{{TIPO}}») se eligió en la entrevista
inicial: {{POR_QUE}}

{{MAPA}}

## Reglas

- **Nada suelto en la raíz.** Todo archivo de trabajo va a la carpeta de su rol.
- **Entregables:** `{{ENTREGABLES}}<categoria>/<archivo>`, con la fecha en
  formato `DD-mmm-YYYY` (`27-oct-2026`). La categoría la decide la tarea
  (`informes`, `presentaciones`, `codigo`, `datos`…); se reutilizan las que ya
  existen antes de inventar una nueva.
- **Contexto:** `{{CONTEXTO}}` es insumo. Se lista y se lee completo antes de
  trabajar; no tiene nombres de archivo fijos. Lo que una tarea produce y otra
  debe releer como insumo se copia aquí.
- **Datos crudos** (si la arquitectura tiene carpeta de datos): no se
  modifican; las transformaciones generan archivos nuevos.
- **Nombres:** minúsculas, sin acentos ni espacios, con guiones
  (`propuesta-comercial-v2.md`), de hasta 60 caracteres.
- **Fechas:** siempre `DD-mmm-YYYY` con el mes abreviado (`10-oct-2026`), en
  carpetas, nombres de archivo y registros.
- **Sin silos profundos:** como mucho 6 niveles por ruta y 150 caracteres
  dentro del repositorio, para que todo funcione en Windows y macOS. Si hace
  falta clasificar más, se usa el nombre del archivo, no otra subcarpeta.
- Nunca se borra ni se mueve un archivo de la persona sin preguntar.

## El orden se vigila solo

- **Al escribir** (hook `PreToolUse`, `orden_check.py`): crear un archivo
  nuevo fuera de la arquitectura se bloquea y el aviso dice la ruta correcta.
  Editar archivos existentes no se bloquea.
- **Al mover** (mismo hook): todo comando que mueva o renombre archivos pide
  confirmación a la persona antes de ejecutarse. **Mover siempre se confirma.**
- **Al empezar la sesión** (`inicio.py`): si hay archivos fuera de lugar o
  duplicados, se le menciona a la persona y se le ofrece reorganizar.
- **Reorganizar** (`ordenar.py`): propone a dónde va cada archivo según su
  contenido y uso. Se le muestra el plan archivo por archivo, se pregunta con
  `AskUserQuestion`, y se mueve **solo lo que confirme**:

  ```bash
  {{PY}} {{SKILL_REL}}/scripts/ordenar.py                        # plan, no mueve nada
  {{PY}} {{SKILL_REL}}/scripts/ordenar.py --aplicar --solo a,b   # solo lo aprobado
  ```

  Al mover, actualiza las referencias en los documentos, registra cada
  movimiento solo en `.espacio/movimientos.log` (registro técnico: no va a la
  bitácora de trabajo) y nunca sobrescribe. Lo que no tiene destino claro se decide con la persona.

Lo que ya existía en la raíz antes del montaje (`espacio.json` →
`arquitectura.preexistentes`) se respeta y no cuenta como desorden.

## Cambiar la arquitectura

Si el trabajo cambia (nuevo proyecto, nuevo tipo de entregable, nueva
fuente de datos), se vuelve a correr Primer Paso (`/primeros-pasos`): suma carpetas y
proyectos sin quitar nada. Mover o renombrar carpetas existentes se hace a
mano, con la persona. Nada de esto se registra en la bitácora de trabajo.
