# Guía de uso

Esta guía explica cada parte de tu espacio de trabajo y cómo pedirla. No hace
falta saber programar: todo se pide escribiendo en Claude Code, con tus
palabras.

## Antes de empezar

Necesitas [Claude Code](https://claude.com/claude-code), con una cuenta Pro,
Max, Team o Enterprise, y una carpeta de trabajo, vacía o con tus archivos. Los
comandos exactos para instalar Claude Code y el skill están en la
[guía de instalación](instalacion.md). Git, Python, Node.js y Playwright los
revisa el instalador del skill; si falta alguno, te pregunta si lo instala.

Instálalo una vez por proyecto, desde la carpeta de ese proyecto. Cada
carpeta tiene su propio espacio.

## La primera sesión

Escribe «empezar» (también sirven «iniciar», «configurar» o «empecemos»).
Claude te hace dos rondas de preguntas cortas: primero con tus palabras
(cargo, proyecto, objetivo, tareas, herramientas) y luego unas de opción
múltiple.

Mientras tanto investiga tu rol en fuentes oficiales y, si tu carpeta ya
tenía habilidades instaladas, las revisa. Al final te muestra una propuesta
en lenguaje sencillo con tus carpetas, tus atajos, lo que encontró de tu
oficio y los programas que te faltan. Puedes pedir cambios. Nada se crea
hasta que dices que sí.

## Tus carpetas

La estructura depende de lo que produces. Quien entrega informes a clientes
recibe una carpeta por cliente; quien analiza datos separa los datos
originales de los procesados; quien escribe código lo mantiene intacto y
trabaja al lado.

Cada tarea guarda su entrega en su propia carpeta, con un número y la fecha:

```
reportes/
  informes/
    P-012-27-oct-2026/
      informe.html
      memoria.md
```

El archivo `memoria.md` resume qué se pidió, cómo se resolvió, qué se
aprendió y cuánto tiempo tomó. Si un archivo queda fuera de su lugar, Claude
te avisa y te propone dónde va. Solo lo mueve si apruebas.

## Tus atajos

Cada tarea habitual tiene un comando: escribe `/` y su nombre. La primera vez
que lo usas, Claude aprende cómo la haces y anota qué revisar antes de
entregarla. Desde la segunda vez sigue esos pasos sin preguntarte lo mismo.

Si una tarea ya la cubría una habilidad que tenías instalada, se sigue
haciendo con esa habilidad.

## El tiempo que ahorras

Al cerrar una tarea, Claude te pregunta si guarda lo aprendido y cuánto te
habría tomado hacerla a mano. Con eso te dice cuánto ahorraste. La siguiente
vez que hagas el mismo tipo de tarea te propone tu estimación anterior, así
que solo confirmas.

Configurar el espacio o crear atajos nunca cuenta como tarea. Solo se mide tu
trabajo.

## Tu resumen semanal

Una vez por semana, Claude te ofrece el resumen: tareas hechas, tiempo con
Claude frente al tiempo a mano, lo que aprendió, lo que le corregiste, lo
pendiente y lo que se repite tanto que podría volverse un atajo. También
puedes pedirlo cuando quieras («¿cómo me fue esta semana?») y guardarlo como
un documento para compartir.

## La lista de arranque

Después de instalar, cada sesión empieza diciéndote cuánto llevas, por
ejemplo «Arranque: 5 de 7 listo», y qué falta: la investigación de tu rol, un
programa, un acceso, los documentos del proyecto o tu primera tarea. Escribe
«sigamos» y Claude te ayuda con lo siguiente.

## Lo que Claude aprende

Cada corrección que le haces queda guardada y se aplica la próxima vez. Lo
que se resuelve se convierte en una nota de memoria que Claude consulta antes
de empezar algo parecido. Las notas se enlazan entre sí: qué requiere cada
una, qué resuelve y qué salió de ella. Puedes ver ese mapa completo en
`docs/espacio-de-trabajo/graph.md`.

Cuando algo no tiene antecedentes, Claude investiga con método: separa el
problema, busca en fuentes oficiales, marca lo que no pudo confirmar y deja
el resultado listo para reutilizarlo.

## Las habilidades que ya tenías

Si tu carpeta ya traía habilidades, Claude las revisa al instalar y cada vez
que agregas o cambias una. Te avisa si alguna guarda una contraseña a la
vista, envía información fuera de tu equipo, puede borrar trabajo, choca con
las reglas de otra o guarda archivos fuera de tus carpetas. También comprueba
si las normas, versiones y cifras que usan siguen vigentes.

Cada corrección te la propone en sencillo y solo la aplica si dices que sí,
con copia de seguridad antes. Puedes pedir una revisión cuando quieras con
«revisa mis skills».

## Tus accesos

Las contraseñas y claves que necesiten tus herramientas se guardan en
`credenciales/.env`, un archivo que no se sube a git. Nunca las escribas en el
chat. Cuando haga falta un acceso, Claude te dice cuál es y cómo guardarlo.

## Ampliar, ordenar y reparar

Si llega un proyecto nuevo, cambias de cargo o empiezas a hacer otro tipo de
tarea, díselo con tus palabras: «tengo un proyecto nuevo», «ahora también
hago…». El espacio se amplía sin quitar nada.

«Ordena mis carpetas» te muestra dónde debería ir cada archivo suelto, uno
por uno. «Repara mi espacio» repone lo que falte si otra herramienta borró
algo.

## Retirar el asistente

Cuando tu espacio queda listo, Claude te ofrece una sola vez tres caminos.
Mantenerlo te sirve si vas a sumar proyectos o instalar más habilidades.
Desactivarlo hace que deje de aparecer, y lo puedes reactivar. Eliminarlo lo
borra y deja sus herramientas en `.claude/espacio/`.

En los tres casos tus carpetas, atajos, memoria, bitácora y resumen semanal
siguen funcionando. Si lo eliminas y luego quieres ampliar el espacio, vuelve
a ejecutar la línea de instalación.

## Si algo no funciona

| Lo que ves | Qué hacer |
|---|---|
| El instalador dice que estás en tu carpeta personal | Entra a la carpeta del proyecto (`cd ruta/del/proyecto`) y repite |
| Falta Python, Node.js o Playwright | Acepta la instalación o pide «instala los programas que faltan» |
| Claude no reconoce «empezar» | Cierra y vuelve a abrir Claude Code en la carpeta del proyecto |
| Un aviso dice que faltan piezas | Escribe «repara mi espacio» |
