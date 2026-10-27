# Crear skills a partir del trabajo

Un skill es un procedimiento empaquetado (`.claude/skills/<nombre>/SKILL.md`,
más scripts y referencias si hacen falta) que Claude invoca cuando la tarea
coincide con su descripción. Aquí nacen del trabajo real, no por adelantado.

## Cuándo proponerlo

- La tabla «Procesos candidatos» de `{{BITACORA}}` marca un proceso con
  2 o más repeticiones, o con una corrección de la persona.
- Una investigación profunda produjo un método que se va a repetir.
- La persona lo pide («quiero que esto quede como un paso fijo»).

Se le propone a la persona en una frase («Esta tarea ya la hicimos tres
veces; ¿la convierto en un procedimiento fijo para que salga igual siempre?»)
y se espera su sí. La decisión se anota en la columna «Decisión» de la tabla.

## Cómo crearlo

1. Si está instalado el skill `skill-creator`, invocarlo con la herramienta
   `Skill`: guía la redacción, crea pruebas y mide si se activa bien.
2. Si no, crear a mano `.claude/skills/<nombre-kebab>/SKILL.md`:

   ```markdown
   ---
   name: <nombre-kebab>
   description: >
     Qué hace y cuándo usarlo, con las frases con las que la persona lo pide.
     La descripción es lo único que Claude ve para decidir si lo activa.
   ---

   # <Nombre>

   ## Disparadores
   Cuándo se invoca (y cuándo no: qué skill vecino corresponde).

   ## Insumos
   Qué necesita, de qué carpeta del espacio (`{{CONTEXTO}}`, datos, credenciales).

   ## Pasos
   La secuencia exacta que se validó en las peticiones P-NNN que le dieron origen.

   ## Validaciones
   Cómo confirmar que el resultado está bien antes de entregarlo.

   ## Salida
   Dónde queda (`{{ENTREGABLES}}<categoria>/`) y en qué formato.
   ```
3. Partes deterministas (cálculos, transformaciones, llamadas a APIs) van como
   scripts dentro del skill (`scripts/`), en Python con biblioteca estándar si
   se puede, con su docstring (qué hace, de qué petición nació, cómo se corre).
4. **Nada de valores del proyecto dentro del skill**: dominios, IDs, nombres de
   cliente y claves se leen de `espacio.json`, `{{CONTEXTO}}` o `credenciales/.env`.
5. Probarlo con la próxima petición real del mismo tipo y ajustar.
6. `grafo.py --actualizar` para que el plan lo encuentre. Crear el skill es
   trabajo sobre el sistema: no se registra en la bitácora ni en la memoria
   (solo se anota `skill <nombre>` en la columna «Decisión» de la tabla).
