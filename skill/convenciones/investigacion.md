# Protocolo de investigación profunda

Se aplica cuando una tarea **no tiene antecedentes**: el plan del grafo no
encontró skill, memoria, investigación previa ni documento de contexto que la
cubra, o la metodología no está validada. También cuando la persona lo pide
(«investiga», «a fondo», «con fuentes»).

## Pasos

1. **Desglose.** Separar el problema en preguntas concretas que, respondidas,
   resuelven la tarea. Decir cuáles son y qué se va a buscar para cada una.
2. **Antes de salir a internet**, revisar `{{CONTEXTO}}` y `{{INVESTIGACION}}`:
   la respuesta puede estar a medias en casa.
3. **Búsqueda.** `WebSearch` para ubicar, `WebFetch` (o `curl`) para leer la
   fuente. Preferir fuentes primarias y oficiales: documentación del
   fabricante, normas, organismos, artículos con datos. Cruzar al menos dos
   fuentes en lo que sostenga una decisión. Si hay un agente o skill de
   investigación instalado, usarlo.
4. **Supuestos explícitos.** Lo que no se pudo confirmar se escribe como
   supuesto, no como hecho.
5. **Ejecutar la tarea** con lo investigado.
6. **Guardar la investigación** para reusarla:
   `{{INVESTIGACION}}<DD-mmm-YYYY>-<tema>.md` con:

   ```markdown
   # <Tema>
   - **Pregunta:** qué se quería saber y para qué tarea.
   - **Respuesta corta:** 3-5 líneas.
   - **Hallazgos:** por pregunta del desglose, con la fuente de cada uno.
   - **Supuestos:** lo no verificado.
   - **Vigencia:** hasta cuándo es razonable confiar (precios, versiones, normas cambian).
   - **Fuentes:** URL, título, fecha de consulta.
   ```
7. **Evaluar recurrencia.** Si el procedimiento puede repetirse, se registra
   con un `proceso` claro en la bitácora y se considera un skill
   (`crear-skills.md`). Si se aprendió una regla, va a memoria.

## Reglas

- Siempre se pregunta antes de una investigación larga o con costo
  (muchas búsquedas, APIs de pago): qué se va a verificar y para qué le sirve
  a la persona. Si prefiere no hacerlo, el dato queda marcado *no verificado*.
- Nunca se inventa una fuente ni una cifra. Si no se encontró, se dice.
- Lo que la persona aporta y no se puede verificar se rotula como «dato de la
  persona».
