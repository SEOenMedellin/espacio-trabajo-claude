# Cómo decidir la arquitectura de carpetas

La arquitectura sale del **objetivo** de la persona, no de su cargo: dos
personas con el mismo cargo pueden necesitar estructuras distintas. Se decide
en cuatro pasos y se le explica a la persona en una frase.

Los **lineamientos del rol** (`references/investigar-rol.md`) se aplican en
cada paso: ayudan a elegir entre tipos base parecidos, justifican carpetas
extra (registros que hay que conservar, información sensible separada,
normas en el contexto) y van citados en el `por_que`. Un lineamiento nunca
justifica pasar los límites de abajo.

## Paso 1 — ¿Qué produce el trabajo?

Mira las tareas habituales y su `entrega`. La salida dominante decide el tipo
base:

| Si lo que más produce es… | Tipo base |
|---|---|
| Informes, propuestas, diagnósticos o presentaciones para alguien | `entregables-a-clientes` |
| Código, aplicaciones, integraciones, automatizaciones | `desarrollo-de-software` |
| Análisis, tableros, modelos o conclusiones a partir de datos | `analisis-de-datos` |
| Piezas de contenido: artículos, guiones, publicaciones, campañas | `contenido-y-comunicacion` |
| Seguimiento, actas, planes, procesos, reportes de gestión | `gestion-y-operaciones` |
| Conocimiento propio: estudio, investigación, documentación de un tema | `investigacion-y-aprendizaje` |

Si dos salidas pesan parecido, el tipo base es el de la tarea **más
frecuente** y la otra aporta carpetas extra (paso 3). Nunca más de un tipo base.

## Paso 2 — ¿Uno o varios proyectos?

- **Uno solo** (`unico`): los roles viven en la raíz.
- **Varios** (`multiproyecto`): cada proyecto en `proyectos/<nombre>/` con su
  propio contexto, entregables, bitácora de peticiones y memoria; la memoria
  global y la investigación compartida quedan en la raíz. Elígelo cuando haya
  clientes o cuentas distintas cuyo material no debe mezclarse, aunque hoy
  solo haya uno.

## Paso 3 — Carpetas extra según tareas y herramientas

El núcleo (contexto, entregables, investigación, memoria, bitácora,
credenciales) existe siempre. Encima se suman solo las carpetas que una tarea
concreta justifique; cada una con su `para`. Regla: **máximo 7 carpetas en el
primer nivel** (sin contar las ocultas). Si una tarea solo produce un tipo de
documento más, eso es una *categoría* dentro de entregables, no una carpeta nueva.

### Silos: anchos, no profundos

Rutas largas fallan en Windows (260 caracteres para la ruta completa) y
complican macOS, la sincronización en la nube y los ZIP. Límites que se
validan y vigila el hook de orden:

| Límite | Valor |
|---|---|
| Niveles por ruta, contando el archivo | 6 |
| Caracteres de la ruta dentro del repositorio | 150 |
| Caracteres de un nombre de archivo o carpeta | 60 |
| Nombre de un proyecto | 30 |

Por eso: la arquitectura propone **como mucho 3 niveles** antes del archivo
en un proyecto único y 4 en multiproyecto (`proyectos/<p>/<rol>/`), los
entregables son siempre `<DD-mmm-YYYY>/<categoria>/<archivo>`, y si hace falta
más clasificación se resuelve con el nombre del archivo (`acta-comite-v2.md`),
no con otra subcarpeta. Si el repositorio vive en una carpeta muy anidada
(por ejemplo, dentro de una carpeta sincronizada con un nombre largo),
sugerirle a la persona moverlo a una ruta corta (`C:\trabajo\`, `~/trabajo/`).

## Paso 4 — ¿Qué hay ya en el repositorio?

Lista la raíz antes de proponer.

- **Repositorio vacío o casi:** se usa la arquitectura tal cual.
- **Repositorio con código o documentos:** **no se mueve nada.** Se adoptan
  las carpetas que ya cumplen un rol (si existe `docs/`, puede ser el
  contexto; si existe `data/`, los datos crudos) y lo que falta se agrega
  con nombres que no choquen. En un repositorio de software, el espacio de
  trabajo no se mezcla con el código fuente: va en carpetas propias
  (`trabajo/`, `docs/…`) y nunca dentro de `src/`.
- **Ya hay un `CLAUDE.md`:** se conserva; el montaje agrega su bloque al final.

## Los seis tipos

Rutas de los roles del núcleo (`rutas`) y carpetas extra típicas
(`arquitectura.carpetas`). Son puntos de partida: ajusta nombres al idioma y a
lo que ya existe.

### `entregables-a-clientes`

Consultoría, agencias, preventa, auditorías, legal, finanzas para terceros.

```
contexto/                    documentos del cliente: briefs, contratos, datos que entrega
entregables/<DD-mmm-YYYY>/   informes, propuestas, presentaciones, por fecha y categoría
historial/                   datos crudos de cada corrida, para comparar en el tiempo
plantillas/                  formatos base de los entregables que se repiten
investigacion/  memoria/  bitacora-peticiones.md
```

Casi siempre `multiproyecto` (un proyecto por cliente): `proyectos/<cliente>/`
con contexto, entregables, historial, memoria y bitácora; `plantillas/`,
`investigacion/` y `memoria/` globales en la raíz.

### `desarrollo-de-software`

Desarrollo, QA, DevOps, integraciones, automatización.

```
(código existente: src/, tests/, … — no se toca)
docs/contexto/               requisitos, historias de usuario, decisiones de negocio
docs/decisiones/             registros de decisiones de arquitectura (ADR), uno por archivo
docs/specs/                  especificaciones y criterios de aceptación por funcionalidad
trabajo/<DD-mmm-YYYY>/       entregables que no son código: análisis, planes, informes
investigacion/  memoria/  bitacora-peticiones.md
```

Rutas: `contexto` → `docs/contexto/`, `entregables` → `trabajo/<DD-mmm-YYYY>/`.
El código sigue su propia estructura; los skills que se creen pueden incluir
scripts del proyecto.

### `analisis-de-datos`

Analítica, BI, ciencia de datos, investigación cuantitativa, finanzas internas.

```
contexto/                    diccionarios de datos, definiciones de indicadores, preguntas de negocio
datos/crudos/                exportes y fuentes originales — inmutables
datos/procesados/            datos limpios y transformados — regenerables
analisis/                    consultas, cuadernos, scripts reproducibles
reportes/<DD-mmm-YYYY>/      tableros, informes y conclusiones por fecha
investigacion/  memoria/  bitacora-peticiones.md
```

Rutas: `entregables` → `reportes/<DD-mmm-YYYY>/`. Si los datos son
sensibles o pesados, sugerir agregar `datos/` al `.gitignore` (se pregunta).

### `contenido-y-comunicacion`

Marketing, redacción, redes, prensa, comunicación interna, formación.

```
contexto/                    marca, voz y tono, público, lineamientos, calendario
ideas/                       banco de ideas y briefs por pieza
borradores/                  piezas en elaboración
publicado/<DD-mmm-YYYY>/     versión final de lo que salió, con su fecha y canal
recursos/                    imágenes, logos y material reutilizable
investigacion/  memoria/  bitacora-peticiones.md
```

Rutas: `entregables` → `publicado/<DD-mmm-YYYY>/`. El flujo es
`ideas → borradores → publicado`; publicar fuera del espacio siempre pide
confirmación.

### `gestion-y-operaciones`

Gerencia de proyectos, coordinación, operaciones, RR. HH., compras, calidad.

```
contexto/                    alcance, contratos, organigrama, procesos vigentes
seguimiento/                 actas, reuniones, pendientes y riesgos, por fecha
procesos/                    procedimientos y listas de verificación del área
reportes/<DD-mmm-YYYY>/      reportes de gestión y presentaciones al comité
plantillas/                  formatos de acta, reporte, solicitud
investigacion/  memoria/  bitacora-peticiones.md
```

Rutas: `entregables` → `reportes/<DD-mmm-YYYY>/`. Los procedimientos que se
repiten son los mejores candidatos a skill.

### `investigacion-y-aprendizaje`

Estudio de un tema, I+D, tesis, preparación de certificaciones, documentación.

```
contexto/                    temario, objetivos, bibliografía base
fuentes/                     artículos, libros, enlaces y notas de lectura
notas/                       síntesis por tema, enlazadas entre sí
producciones/<DD-mmm-YYYY>/  ensayos, resúmenes, presentaciones, código de práctica
investigacion/  memoria/  bitacora-peticiones.md
```

Rutas: `entregables` → `producciones/<DD-mmm-YYYY>/`. Aquí la memoria y las
investigaciones son el corazón: se enfatiza el protocolo de investigación.

## Cómo explicarlo a la persona

Una frase con el porqué, en sus términos, y el árbol (solo primer y segundo
nivel). Ejemplo:

> Como tu trabajo es convertir los exportes del ERP en indicadores cada
> semana, voy a separar los datos originales (que nunca se tocan) de los
> procesados, y los reportes quedarán ordenados por fecha:
>
> ```
> contexto/        lo que define los indicadores
> datos/crudos/    exportes originales
> datos/procesados/
> analisis/
> reportes/        uno por semana
> investigacion/   lo que investiguemos, con fuentes
> memoria/         lo que aprendamos para no repetirlo
> ```

Ese «por qué» se guarda en `arquitectura.por_que`.
