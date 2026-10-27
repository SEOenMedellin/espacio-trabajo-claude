# Memoria de trabajo

Un nodo por cosa resuelta, enlazados entre sí. Existe para que algo ya
resuelto no haya que volver a razonarlo: se lee `INDICE.md` para decidir y
luego solo el nodo elegido.

## Formato de un nodo (`<id>.md`)

```markdown
---
id: como-se-hace-x
titulo: Una línea que diga qué resuelve
tipo: proceso
ambito: global
fecha: 01-ene-2026
tags: [tema, herramienta]
relacionado: [requiere:otro-nodo, deriva_en:nodo-derivado]
---

## Problema
Qué pasaba y por qué no era obvio.

## Solución / Regla
Lo que hay que hacer, en pasos o en una regla clara.

**Por qué:** la razón (sin ella, la regla se rompe en el primer caso raro).
**Cómo aplicarlo:** cuándo entra en juego.
```

Relaciones (`relacionado`): cada id puede llevar su tipo delante —
`requiere:` (este nodo necesita el otro), `resuelve:` (este nodo resuelve lo
que plantea el otro), `deriva_en:` (de este nodo salió el otro). Sin tipo,
la relación es `relacionado`. El grafo y `docs/espacio-de-trabajo/graph.md`
las muestran con su tipo.

Tipos: `restriccion` (algo que no se puede), `solucion` (un problema y su
arreglo), `decision` (qué se eligió y por qué), `proceso` (pasos que se
repiten), `dato` (un hecho estable del proyecto), `preferencia` (cómo le
gusta trabajar a la persona). Enlaces en el cuerpo con `[[id]]`.

## Reglas

- `ambito: global` solo si sirve a cualquier proyecto. Lo específico va a la
  memoria del proyecto. Un nodo global nunca enlaza a uno de proyecto.
- Antes de crear un nodo, buscar si ya hay uno que lo cubra y actualizarlo.
- Un nodo que resulta falso se corrige o se borra.
- `INDICE.md` se genera con `memoria.py --rebuild`; no se edita a mano.
