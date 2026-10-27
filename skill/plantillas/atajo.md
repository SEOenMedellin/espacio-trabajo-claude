---
name: {{SLUG}}
description: >
  Atajo para «{{TAREA}}», una tarea habitual de {{CARGO}} en {{PROYECTO}}.
  Úsalo cuando la persona escriba /{{SLUG}} o pida esta tarea con sus
  palabras. Entrega: {{ENTREGA}}. Frecuencia: {{FRECUENCIA}}.
---

# {{TAREA}}

<!-- atajo de primeros-pasos · proceso: {{SLUG}} -->

Atajo creado por `primeros-pasos` para que esta tarea salga igual de bien
cada vez. La persona lo usa escribiendo `/{{SLUG}}` o pidiéndola con sus
palabras.

## Antes de empezar

1. Pon en marcha el reloj de la tarea, para medir el tiempo ahorrado:
   `{{PY}} {{SKILL_REL}}/scripts/tiempo.py --empezar {{SLUG}}{{PROYECTO_FLAG}}`
2. `{{PY}} {{SKILL_REL}}/scripts/grafo.py --plan "{{TAREA}}"{{PROYECTO_FLAG}}`, y lee la
   memoria y el contexto que marque.
3. Repasa los lineamientos del rol en `{{DOCS}}/perfil.md` que apliquen a
   esta entrega.

## Cómo se hace

<!-- proceso:inicio -->
Todavía no se ha hecho esta tarea con Claude. La primera vez, hazla con el
protocolo del espacio (`CLAUDE.md`) y pregúntale a la persona lo que haga
falta. Al cerrar, y solo con su sí, reemplaza este párrafo por los pasos que
funcionaron, el formato de la entrega y las correcciones que hizo, para que la
próxima vez salga igual sin volver a preguntar.
<!-- proceso:fin -->

## Entrega

Va a `{{ENTREGABLES}}{{SLUG}}/` con la fecha del día (`DD-mmm-YYYY`).

## Al terminar

Protocolo de cierre del `CLAUDE.md`, con `proceso: {{SLUG}}` en la entrada de
la bitácora y la pregunta de tiempo: cuánto le habría tomado a mano (si ya
lo estimó antes, `tiempo.py --estimacion {{SLUG}}` y se le propone ese valor) y
cuánto tomó con Claude (`tiempo.py --terminar{{PROYECTO_FLAG}}`). Dile en una
frase cuánto tiempo se ahorró.
