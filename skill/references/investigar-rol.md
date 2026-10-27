# Investigar el rol

Lo que la persona cuenta en la entrevista es su versión del trabajo: suele
dejar por fuera obligaciones que da por obvias, tareas que hace pocas veces y
normas que la rigen. Antes de decidir la arquitectura se investiga el rol a
fondo, y de esa investigación salen los **lineamientos** con los que se diseña
el espacio. La entrevista dice qué hace la persona; la investigación dice qué
exige su oficio.

Se aplica en el montaje (SKILL.md, paso 4) y al ampliar cuando cambia el cargo
o se suman tareas de otro tipo («cambió mi cargo», «ahora también hago…»).

## 1. Delimitar

Antes de buscar, fija en una línea qué rol se investiga y en qué marco:

- **Cargo y área**, tal como los dijo la persona, y su equivalente más común
  si usó un nombre interno.
- **Sector y país**, si los dijo. Si las obligaciones dependen del país o del
  sector (normas, registros, plazos) y no los dijo, inclúyelo en la única
  repregunta de la entrevista.
- **Objetivo y destinatarios** del proyecto: acotan qué parte del oficio
  importa aquí.

Dile a la persona en una frase qué vas a investigar y para qué: *«Antes de
proponerte las carpetas voy a investigar qué implica tu rol —
responsabilidades, obligaciones y tareas típicas— para que no se me escape
nada.»* Son entre 5 y 10 búsquedas. No hace falta pedir permiso: es parte del
montaje. Si la persona dice que no, o no hay acceso a internet, se sigue con
la entrevista y se anota el motivo en `limitacion`.

## 2. Qué investigar

| Eje | Preguntas que responde |
|---|---|
| Responsabilidades | ¿De qué responde este rol? ¿Qué resultados se le piden y cómo se miden? |
| Obligaciones | ¿Qué normas, regulaciones, estándares, códigos de ética o políticas lo rigen? ¿Qué registros, evidencias o documentos debe conservar, y por cuánto tiempo? ¿Qué información sensible maneja? |
| Tareas comunes | ¿Qué hace en el día a día, cada semana, cada mes, cada cierre de periodo y de forma ocasional? ¿Qué entrega en cada una y a quién? |
| Ciclos | ¿Hay calendarios, plazos, cierres o auditorías que marquen su trabajo? |
| Métodos | ¿Qué metodologías, marcos o buenas prácticas reconoce el oficio? |
| Insumos y herramientas | ¿Qué tipo de información recibe y de qué clase de sistemas? (categorías, no marcas) |
| Programas para trabajar | ¿Qué hay que tener instalado en el equipo para hacer sus tareas aquí: lenguajes y entornos de ejecución, utilidades de línea de comandos, bibliotecas, navegadores para automatizar, controladores? ¿Cómo se comprueba cada uno y cuál es su fuente oficial de instalación? |
| Riesgos | ¿Qué errores son típicos o costosos en este rol? |

## 3. Cómo buscar

- `WebSearch` para ubicar y `WebFetch` (o `curl`) para leer la fuente
  completa. Si hay un agente o un skill de investigación instalado, úsalo.
- **Preferir fuentes oficiales y primarias:** clasificaciones oficiales de
  ocupaciones, organismos de trabajo o de estadística, asociaciones y
  colegios profesionales, entes reguladores del sector, normas y estándares
  publicados, y descripciones de cargo de organizaciones reconocidas. Las
  ofertas de empleo sirven para confirmar tareas comunes, no para obligaciones.
- **Cruzar al menos dos fuentes** en cada obligación y en cada lineamiento
  que cambie la arquitectura. Lo que solo tenga una fuente, o ninguna, va a
  `supuestos`.
- Nunca inventar una fuente, una norma ni una cifra. Si no se encontró, se dice.

## 4. Contrastar con la persona

La investigación no reemplaza la entrevista; la completa. Antes de convertir
hallazgos en carpetas:

- Las **tareas comunes que la persona no mencionó** se le preguntan en la
  propuesta (paso 6): «Es habitual en tu rol hacer X; ¿también lo haces?».
  Solo las que confirme pasan a `perfil.tareas`. El espacio documenta el
  trabajo real de la persona, no el de un cargo genérico.
- Las **obligaciones** se le muestran aunque no las haya mencionado: son las
  que más cuesta recordar y las que más pesan si faltan.
- Si algo de la investigación contradice lo que dijo la persona, gana la
  persona, y la diferencia se anota en `supuestos`.

## 5. De hallazgos a lineamientos

Un **lineamiento** es una regla de diseño del espacio que sale de un hallazgo:
dice qué se hace y por qué. Cada uno debe poder rastrearse a un hallazgo y
terminar en algo concreto de la arquitectura o del protocolo de trabajo.

| Si la investigación encuentra… | El lineamiento suele ser… |
|---|---|
| Registros o evidencias que hay que conservar | Una carpeta propia para ellos, nunca mezclados con borradores, y nada se borra de ella |
| Información sensible o personal | Separarla en su carpeta y proponer sacarla de git; acceso a sistemas solo de lectura |
| Normas, estándares o metodologías del oficio | Guardarlas en la carpeta de contexto y que cada entregable las cite |
| Ciclos periódicos (semanal, mensual, cierre, auditoría) | Entregables por fecha con una categoría por ciclo |
| Tareas ocasionales pero críticas | Una categoría de entregable o una plantilla, no una carpeta nueva |
| Varios destinatarios o clientes que no deben cruzarse | Modo multiproyecto |
| Errores típicos del rol | Un punto de verificación en el protocolo, anotado como memoria inicial |
| Conocimientos que el oficio exige y la persona no listó | Sumarlos a `perfil.conocimientos` |

Los lineamientos se aplican en el paso 5 con `references/arquitecturas.md`:
deciden entre tipos base parecidos, justifican carpetas extra y escriben el
`por_que`. Nunca justifican pasar los límites de la arquitectura (siete
carpetas en el primer nivel, rutas de seis niveles).

## 6. Dónde queda

En `respuestas-espacio.json`, bloque `investigacion_rol`:

```json
"investigacion_rol": {
  "fecha": "27-oct-2026",
  "rol": "Analista de operaciones, sector logístico",
  "responsabilidades": ["Medir el cumplimiento de entregas y reportarlo a la gerencia"],
  "obligaciones": ["Conservar los datos fuente de cada indicador publicado para poder auditarlo"],
  "tareas_comunes": ["Cierre mensual de indicadores", "Análisis de causa raíz de incumplimientos"],
  "lineamientos": [
    {"regla": "Los exportes originales no se modifican nunca", "por_que": "Cada indicador debe poder rehacerse desde su fuente", "aplica_en": "datos/crudos/"}
  ],
  "supuestos": ["La retención exigida depende de la política interna; no se pudo confirmar"],
  "fuentes": [
    {"titulo": "Nombre del documento o la página", "url": "https://…", "consultado": "27-oct-2026"}
  ]
}
```

- `responsabilidades`, `tareas_comunes` y `lineamientos` no pueden ir vacíos.
- Cada lineamiento lleva `regla` y `por_que`; `aplica_en` es la carpeta o la
  parte del protocolo donde se nota (opcional).
- `fuentes` no puede ir vacía salvo que haya `limitacion` explicando por qué
  no se investigó. Cada fuente lleva `titulo`, `url` y `consultado`.
- Fechas en formato `DD-mmm-YYYY`.

Python, Node.js y Playwright son la base de todo espacio y no se listan:
`programas.py` ya los revisa. Los programas que el rol sume no van dentro de
este bloque sino en `programas`, en la raíz de
`respuestas-espacio.json` (esquema en `references/entrevista.md` § 5), porque
`verificar.py` y el aviso de inicio los comprueban en cada sesión. Solo se
listan los que una tarea confirmada necesite, cada uno con el comando que
muestra su versión y su fuente oficial de instalación. Instalar algo siempre
se confirma con la persona.

`montar.py` guarda la investigación completa en la carpeta de investigación
como `<fecha>-rol-<cargo>.md` (nunca sobrescribe una anterior) y pone las
responsabilidades, obligaciones y lineamientos en el perfil, que Claude carga
en cada sesión.
