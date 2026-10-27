# Entrevista inicial

Objetivo: conocer a la persona y su trabajo lo suficiente para decidir la
arquitectura de carpetas y preparar el entorno. Son **dos rondas**, más una
confirmación. Lo que la persona ya haya dicho en la conversación (o lo que
esté en los documentos del repositorio) se da por respondido: no se pregunta
dos veces.

## 1. Ronda abierta — un solo mensaje

Estas respuestas son texto libre, así que van en un mensaje normal (no en
`AskUserQuestion`, que obliga a elegir opciones). Usa este texto, adaptando
el tono:

> Voy a preparar tu espacio de trabajo. Primero quiero entender qué haces;
> responde con tus palabras, no hace falta que sea largo:
>
> 1. **¿Cuál es tu cargo** y en qué área o equipo trabajas?
> 2. **¿En qué proyecto vas a trabajar aquí** y cuál es su objetivo? ¿Qué
>    tiene que existir cuando el proyecto esté bien hecho?
> 3. **¿Qué conocimientos debería tener yo** para ayudarte bien? (temas,
>    normas, metodologías, herramientas, el negocio del cliente…)
> 4. **¿Cuáles son tus tareas habituales?** Las que haces cada semana o cada
>    mes, y lo que entregas en cada una.
> 5. **¿Qué herramientas o servicios usas?** (hojas de cálculo, un CRM, una
>    plataforma, APIs, repositorios de código…)
>
> No me compartas contraseñas ni claves: cuando haga falta un acceso, te
> explico cómo dejarlo guardado de forma segura.

Si una respuesta queda corta para decidir (por ejemplo, «hago informes» sin
decir de qué ni para quién), haz **una** repregunta concreta en el mismo
estilo. No más de una.

## 2. Ronda cerrada — una sola `AskUserQuestion`

Hasta cuatro preguntas con opciones. Omite las que ya se respondieron.

| Pregunta | Opciones | Para qué se usa |
|---|---|---|
| ¿Cuántos proyectos vas a llevar en este espacio? | Uno solo · Varios (clientes, cuentas o iniciativas distintas) | `arquitectura.modo` |
| ¿Para quién es principalmente lo que produces? | Clientes externos · Mi equipo o mi jefe · Solo para mí · Público (publicaciones, comunidad) | `perfil.destinatarios`; pesa en la elección de arquitectura y en el tono de los entregables |
| ¿Cómo prefieres que te hable? | Directo y sin tecnicismos · Técnico, conozco las herramientas · Con explicaciones paso a paso | `trato` |
| ¿Quieres que lleve un historial de versiones de los archivos? | Sí (recomendado) · No | `git` |

Si eligió «Varios», pregunta en un mensaje corto los nombres de los proyectos
que ya sabe (se pueden agregar después).

## 3. Inferir sin preguntar

- **Idioma:** el de la conversación.
- **Credenciales:** de las herramientas mencionadas, deduce qué accesos van a
  hacer falta y propón nombres de variable (`CRM_TOKEN`,
  `NUBE_CREDENCIALES`…) con una línea de para qué sirve cada uno.
  Solo nombres: **nunca valores**.
- **Arquitectura:** con `references/arquitecturas.md` (objetivo + tareas +
  destinatarios + modo + lineamientos del rol + lo que ya hay en el repositorio).
- **Programas:** de las tareas, las herramientas y la investigación del rol,
  deduce qué programas deben estar instalados (lenguajes, entornos de
  ejecución, utilidades de línea de comandos, bibliotecas) y cómo comprobar
  cada uno. Solo los que una tarea concreta necesite.
- **Conocimientos:** normaliza la lista (temas concretos, no frases largas).
- **Tareas:** cada una con `tarea`, `frecuencia` (si la dijo) y `entrega`
  (qué produce). De aquí salen las categorías de entregables y, a futuro, los
  candidatos a skill.

## 4. Confirmación

Muestra la propuesta en lenguaje sencillo (ver SKILL.md, paso 6) y pregunta
con `AskUserQuestion`: «Sí, prepáralo» · «Quiero cambiar algo» · «Ahora no».
Sin un «Sí, prepáralo» en esta conversación no se escribe nada.

## 5. Esquema de `respuestas-espacio.json`

Se escribe en la raíz con `Write`; `montar.py` lo borra al terminar bien.

```json
{
  "idioma": "es",
  "trato": "Directo y sin tecnicismos; explicar las decisiones en una frase.",
  "git": true,
  "perfil": {
    "nombre": "opcional",
    "cargo": "Analista de operaciones",
    "area": "Operaciones",
    "proyecto": "Tablero de indicadores logísticos",
    "objetivo": "Que la gerencia vea cada lunes el cumplimiento de entregas y los cuellos de botella.",
    "destinatarios": "Mi jefe y la gerencia de operaciones",
    "conocimientos": ["Indicadores logísticos (OTIF, lead time)", "Hojas de cálculo y limpieza de datos", "Normas de la empresa sobre datos de clientes"],
    "tareas": [
      {"tarea": "Actualizar el tablero semanal", "frecuencia": "semanal", "entrega": "tablero + resumen de 1 página"},
      {"tarea": "Investigar causas de retrasos", "frecuencia": "cuando hay alertas", "entrega": "informe corto"}
    ],
    "herramientas": ["Hoja de cálculo", "Sistema de gestión (exporta CSV)", "Correo"]
  },
  "arquitectura": {
    "tipo": "analisis-de-datos",
    "modo": "unico",
    "por_que": "El trabajo es transformar exportes del ERP en indicadores periódicos: datos crudos inmutables, análisis reproducible y reportes por fecha.",
    "carpetas": [
      {"ruta": "datos/crudos/", "para": "Exportes originales del ERP, sin modificar"},
      {"ruta": "datos/procesados/", "para": "Datos limpios y transformados, regenerables"},
      {"ruta": "analisis/", "para": "Consultas, cuadernos y scripts del análisis"}
    ]
  },
  "rutas": {
    "contexto": "contexto/",
    "entregables": "reportes/",
    "investigacion": "investigacion/",
    "memoria_global": "memoria/",
    "bitacora_peticiones": "bitacora-peticiones.md"
  },
  "credenciales": [
    {"variable": "ERP_USUARIO", "para": "Usuario de solo lectura para exportar del ERP"}
  ],
  "programas": [
    {"nombre": "Intérprete del lenguaje de análisis", "para": "Correr los scripts de limpieza y cálculo",
     "comprobar": "<comando> --version", "instalar": "Instalador oficial (URL de la fuente oficial)"}
  ],
  "investigacion_rol": { "…": "ver references/investigar-rol.md § 6" },
  "skills_existentes": { "…": "solo si el repositorio ya tenía skills: references/skills-existentes.md § 5" }
}
```

`programas`: cada uno con `nombre`, `para` y `comprobar` (el comando que
muestra su versión; su primera palabra debe ser el ejecutable, que
`verificar.py` busca en el sistema). `instalar` es opcional: la fuente oficial
o la orden del gestor de paquetes. Para una biblioteca o un complemento que no
es un ejecutable propio, `comprobar` es el comando de la herramienta que lo
carga.

Modo multiproyecto: `"modo": "multiproyecto"`, un bloque
`"proyectos": {"base": "proyectos", "lista": ["cliente-a", "cliente-b"]}` y
rutas con `<proyecto>`: `contexto`, `entregables` (`proyectos/<proyecto>/`),
`bitacora_peticiones` y `memoria_proyecto` (por ejemplo
`proyectos/<proyecto>/memoria/`). La memoria
global se queda en la raíz. Las carpetas extra pueden llevar `<proyecto>` si
son por proyecto.

Reglas que valida `montar.py` (código 2 si no se cumplen): perfil con cargo,
proyecto, objetivo y al menos una tarea; `investigacion_rol` completa (ver
`references/investigar-rol.md`); cada programa con `nombre`, `para` y
`comprobar`; rutas relativas, sin `..`, fuera de
`.claude/`, `.git/` y `.espacio/`; cada carpeta extra con `ruta` y `para`;
nombres de proyecto en minúsculas con guiones y hasta 30 caracteres; que cada
carpeta deje sitio a sus archivos sin pasar de 6 niveles ni 150 caracteres
(`references/arquitecturas.md`, «Silos»); variables de credenciales en
MAYÚSCULAS y sin campo `valor`. Las fechas siempre en formato `DD-mmm-YYYY`
con el mes abreviado: `10-oct-2026`.
