---
name: {{SLUG}}
description: >
  Atajo para «{{TAREA}}», una tarea habitual de {{CARGO}} en {{PROYECTO}}.
  Úsalo cuando la persona escriba /{{SLUG}} o pida esta tarea con sus
  palabras. Entrega: {{ENTREGA}}. Frecuencia: {{FRECUENCIA}}.
---

# {{TAREA}}

<!-- atajo de primeros-pasos · proceso: {{SLUG}} -->

Atajo creado al preparar el espacio de trabajo, para que esta tarea salga
igual de bien cada vez. La persona lo usa escribiendo `/{{SLUG}}` o
pidiéndola con sus palabras.

## Disparadores

Cuando la persona pide «{{TAREA}}» o algo equivalente. Si pide otra cosa,
este atajo no aplica.

## Antes de empezar

1. Abre la tarea (da el id, crea su carpeta y pone el reloj en marcha):
   `{{PY}} {{SKILL_REL}}/scripts/tarea.py --empezar --proceso {{SLUG}} --categoria {{SLUG}}{{PROYECTO_FLAG}}`
2. `{{PY}} {{SKILL_REL}}/scripts/grafo.py --plan "{{TAREA}}"{{PROYECTO_FLAG}}`, y lee la
   memoria y el contexto que marque.
3. Repasa los lineamientos del rol en `{{DOCS}}/perfil.md` que apliquen.

## Cómo se hace

<!-- proceso:inicio -->
Todavía no se ha hecho esta tarea con Claude. La primera vez, hazla con el
protocolo del espacio (`CLAUDE.md`) y pregúntale a la persona lo que haga
falta. Al cerrar, y solo con su sí, reemplaza este párrafo por los pasos que
funcionaron, el formato de la entrega y las correcciones que hizo.
<!-- proceso:fin -->

## Validaciones

Antes de entregar, comprueba:

<!-- validaciones:inicio -->
- La entrega es la que se pidió ({{ENTREGA}}) y responde a la petición.
- Respeta los lineamientos del rol y las correcciones anteriores de la persona.
- Cada dato que sostiene una decisión cita su fuente o está marcado *no verificado*.
- El archivo está en la carpeta de la tarea y su nombre no tiene espacios ni acentos.

La primera vez que se haga, al cerrar y con el sí de la persona, agrega aquí
los criterios propios de esta tarea (cifras que deben cuadrar, secciones
obligatorias, formato que exige quien la recibe).
<!-- validaciones:fin -->

## Salida

La entrega queda en la carpeta que dio `tarea.py --empezar`
(`{{ENTREGABLES}}{{SLUG}}/<P-NNN>-<fecha>/`), junto a su `memoria.md`.

## Al terminar

Protocolo de cierre del `CLAUDE.md`: una sola pregunta con «¿Lo guardo así?»
y «¿Cuánto te habría tomado a mano?» (si ya lo estimó antes,
`tiempo.py --estimacion {{SLUG}}` y se le propone ese valor). Luego
`tarea.py --cerrar --datos -{{PROYECTO_FLAG}}` hace el resto y te da la frase
del tiempo ahorrado para decírsela.
