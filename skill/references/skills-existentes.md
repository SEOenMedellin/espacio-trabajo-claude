# Skills que ya trae el repositorio

Si el repositorio no está en blanco, lo que ya tiene (skills, comandos,
agentes, archivos de reglas, hooks y servidores MCP) es conocimiento valioso
y, a la vez, una fuente de riesgos: claves escritas en un archivo, envíos a
servicios externos, reglas que se contradicen entre sí o con el espacio.
Antes de montar, se revisa todo; lo validado se vuelve parte del contexto del
espacio y lo que tenga problemas se corrige, siempre con el sí de la persona.

Se aplica en el montaje (SKILL.md, paso 2) y cada vez que aparece un skill
nuevo o cambiado: el aviso de inicio y `verificar.py` lo detectan, y la
persona también puede pedirlo («revisa mis skills»).

## Qué hace el script y qué haces tú

| Lo hace `revisar.py --borrador` | Te toca a ti (depende del rol) |
|---|---|
| Inventario, auditoría de seguridad, lógica, contradicciones y arquitectura | Confirmar los hallazgos dudosos leyendo solo esas líneas |
| Qué hace cada skill, sus reglas y qué tareas de la persona cubre | Corregir lo que el borrador haya cruzado mal |
| Los datos que conviene validar (normas, versiones, cifras, enlaces) | Validarlos en fuentes oficiales (`--pendientes`) |
| El resumen en sencillo para la persona (`--resumen`) | Decidir con ella qué se corrige |
| Marcar en `perfil.tareas` qué tarea ya cubre un skill | — |

Lee un skill completo solo cuando el borrador no alcance para entenderlo
(sin descripción, o con hallazgos que haya que confirmar). Lo demás ya está
resumido.

## 1. Inventario

```bash
python <skill>/scripts/inventario.py          # resumen
python <skill>/scripts/inventario.py --json   # completo
```

Lee **completos** cada `SKILL.md`, sus `references/` y sus scripts, y los
archivos de reglas (`CLAUDE.md`, `AGENTS.md`) que no sean el bloque de este
espacio. Sin leerlos enteros no se puede validar ni comparar nada.

## 2. Auditoría automática

```bash
python <skill>/scripts/auditar.py             # hallazgos
python <skill>/scripts/auditar.py --reglas    # reglas de cada fuente, para compararlas
```

Busca de forma mecánica:

| Tipo | Qué detecta |
|---|---|
| Seguridad | Claves escritas en archivos, envíos a servicios externos, borrados masivos, push forzado, saltarse verificaciones, ejecutar código descargado, certificados desactivados, secretos impresos. En hooks y servidores MCP pesa más: corren sin que nadie lo pida |
| Lógica | Skills sin nombre o sin descripción, nombres repetidos, archivos mencionados que no existen |
| Contradicción | Dos skills que se activan con la misma frase (o con las de este skill), formatos de fecha distintos al del espacio, reglas opuestas entre fuentes |
| Arquitectura | Rutas donde un skill escribe que no caben en la arquitectura del espacio (se revisa cuando ya existe `respuestas-espacio.json` o `espacio.json`) |

Los hallazgos de la auditoría son **pistas, no veredictos**: confirma cada
uno leyendo el archivo. Un falso positivo se descarta; uno real pasa a
`problemas` con su decisión.

## 3. Lo que solo tú puedes revisar

La auditoría no entiende de qué habla un skill. Por cada uno:

- **Conocimiento que trae.** Lista los datos que sostienen sus decisiones:
  normas, metodologías, cifras, precios, versiones de herramientas, rutas de
  APIs, formatos exigidos. Valídalos con el protocolo de investigación
  profunda (fuentes oficiales, dos fuentes para lo que decide algo) y marca
  cada uno: `verificado`, `desactualizado` (con lo que dice hoy la fuente) o
  `no verificado`. Nunca inventes una fuente.
- **Lógica.** ¿Los pasos llevan a lo que promete? ¿Hay pasos que dependen de
  algo que no existe o que se contradicen dentro del mismo skill?
- **Contradicciones.** Compara las reglas de todos (`auditar.py --reglas`):
  entre skills, con los archivos de reglas, con los lineamientos del rol y
  con las reglas del espacio (fechas `DD-mmm-YYYY`, límites de rutas, nada
  sale del espacio sin un sí, credenciales fuera del chat).
- **Tareas que cubre.** Cruza cada skill con las tareas habituales de la
  persona. Una tarea que ya resuelve un skill existente no recibe un atajo
  nuevo: en `perfil.tareas` lleva `"skill": "<nombre>"` y se usa ese skill.

Antes de validar, dile a la persona en una frase cuántos skills vas a revisar
y aproximadamente cuántas búsquedas implica.

## 4. Decidir con la persona

En la propuesta (SKILL.md, paso 6) muéstrale en sencillo:

- Qué skills encontraste y para qué sirve cada uno.
- Qué conocimiento quedó validado y qué está desactualizado o sin validar.
- Los problemas, empezando por los de gravedad alta, cada uno con lo que
  propones: **corregir**, **aceptar** (queda como está, con su motivo) o
  dejar **pendiente**.

Las reglas que hacen cumplir los scripts del espacio (fechas, límites de
rutas, credenciales) no se relajan por un skill: el choque se resuelve
adaptando el skill o dejando sus salidas en una carpeta propia que el espacio
adopta. Si dos reglas chocan y ninguna es del espacio, decide la persona.

## 5. Dónde queda

En `respuestas-espacio.json`, bloque `skills_existentes`. `montar.py` no
acepta el montaje si el repositorio tiene skills y falta la revisión de
alguno.

```json
"skills_existentes": {
  "fecha": "27-oct-2026",
  "skills": [
    {
      "nombre": "generar-informe",
      "ruta": ".claude/skills/generar-informe",
      "para": "Generar el informe mensual con el formato de la marca",
      "tareas": ["Informe mensual"],
      "reglas": ["La marca se declara siempre; no hay marca por defecto"],
      "conocimiento": [
        {"dato": "La norma de accesibilidad exige contraste mínimo 4.5:1", "estado": "verificado",
         "fuente": "https://…"},
        {"dato": "La API de exportación usa la versión 2", "estado": "desactualizado",
         "fuente": "https://…", "nota": "La versión vigente es la 3"}
      ],
      "problemas": [
        {"gravedad": "alta", "tipo": "seguridad", "que": "Clave escrita en scripts/render.py",
         "decision": "corregir"}
      ]
    }
  ],
  "contradicciones": [
    {"entre": ["generar-informe", "CLAUDE.md"], "que": "Uno publica al terminar; el otro exige confirmación",
     "decision": "corregir"}
  ],
  "fuentes": [{"titulo": "…", "url": "https://…", "consultado": "27-oct-2026"}]
}
```

- `estado`: `verificado`, `desactualizado` o `no verificado`; los dos
  primeros llevan `fuente`.
- `tipo` de problema: `seguridad`, `logica`, `contradiccion` o
  `arquitectura`. `decision`: `corregir`, `aceptar` o `pendiente`.

`montar.py` deja:

- `<investigación>/<fecha>-skills-del-repositorio.md`: la revisión completa,
  con fuentes. Nunca se sobrescribe; cada revisión nueva lleva su fecha.
- `<contexto>/skills-del-repositorio.md`: qué skill usar para cada tarea,
  qué reglas imponen, qué conocimiento no está validado y qué problemas
  siguen abiertos. Es lo que Claude consulta antes de trabajar; se rehace en
  cada revisión, con copia previa.

Y marca el inventario como revisado, para que el aviso de inicio solo vuelva
a hablar de skills cuando aparezca uno nuevo o cambie alguno.

## 6. Reconstruir

Después del montaje (SKILL.md, paso 9):

1. **Correcciones aprobadas.** Para cada problema con decisión `corregir`,
   muestra el cambio exacto (antes y después) y pide un sí por cada skill.
   Antes de editar, copia el archivo a `.espacio/respaldos/<fecha>/`. Una
   clave expuesta se saca del archivo, va a `credenciales/.env` y se le dice
   a la persona que la rote: si llegó a git, sigue en el historial.
2. **Orden.** `ordenar.py` propone a dónde va cada archivo según la
   arquitectura y los lineamientos; solo se mueve lo que la persona confirme.
3. **Verificar.** `auditar.py` otra vez: los problemas corregidos ya no deben
   aparecer, y los aceptados quedan explicados en la revisión.

Editar los skills de la persona es trabajo sobre el sistema, no sobre su rol:
no deja entrada en la bitácora ni nodo de memoria.
