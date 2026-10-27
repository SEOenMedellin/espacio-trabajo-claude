# Memoria de trabajo

`{{MEMORIA_GLOBAL}}` guarda lo que sirve a cualquier proyecto;
`{{MEMORIA_PROYECTO}}` lo específico de este. Un nodo por cosa resuelta; el
formato está en el `README.md` de la carpeta de memoria.

## Cuándo se escribe un nodo

- Se entendió un error y su arreglo (`solucion`).
- Se tomó una decisión con su porqué (`decision`).
- Un procedimiento se va a repetir (`proceso`).
- Apareció un hecho estable del proyecto que no está en los documentos (`dato`).
- Hay algo que no se puede hacer y por qué (`restriccion`).
- La persona corrigió cómo trabajar o cómo entregar (`preferencia`).

No se escribe lo que ya está en los documentos de contexto, en el código o en
la bitácora: la memoria guarda lo que no es obvio. **Y solo del trabajo del
rol**: nunca nodos sobre la configuración del espacio, carpetas, credenciales,
skills, hooks o el desarrollo de este sistema.

## Cómo se lee

1. `grafo.py --plan` sugiere nodos para la petición.
2. Si hace falta más, leer el `INDICE.md` del ámbito.
3. Abrir solo el nodo elegido.

## Reglas

- Antes de crear, buscar si ya hay un nodo que lo cubra y actualizarlo.
- Un nodo global nunca enlaza a uno de proyecto (`memoria.py` lo reporta).
- Si un nodo resulta falso, se corrige o se borra: la memoria que miente es
  peor que no tener memoria.
- Tras crear o editar: `{{PY}} {{SKILL_REL}}/scripts/memoria.py --rebuild`.

La memoria automática de Claude (personal, fuera del espacio) no reemplaza a
esta: lo que deba alimentar el grafo va aquí.
