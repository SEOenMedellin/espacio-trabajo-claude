# Credenciales

```
credenciales/.env            valores reales — nunca se versiona
credenciales/.env.example    solo nombres y para qué sirve cada uno — sí se versiona
```

Cualquier archivo de clave (JSON de cuenta de servicio, certificados) también
va en `credenciales/` y queda fuera de git por la regla `credenciales/*`.

## Reglas

- **Nunca se piden ni se pegan secretos en el chat**, ni se imprimen en la
  terminal (filtrar la salida al revisar una configuración).
- Los scripts leen las claves de `credenciales/.env`; ninguna se escribe en un
  skill, un script o un documento.
- Si una credencial no encaja con lo que espera un script, no se le cambia el
  nombre ni la ruta para «hacerla funcionar»: se pregunta.
- Antes de concluir «no hay acceso», se prueban todas las credenciales
  disponibles en `credenciales/`.

## Si falta un acceso

No se detiene el trabajo: se sigue con el camino disponible (datos públicos,
versión gratuita) o se marca `n/d`, y al final se le dice a la persona en una
frase qué faltó, qué habría aportado y que puede pedir la explicación de cómo
conseguirlo. Cuando la pida, se le explica paso a paso; el valor lo pone ella
en `credenciales/.env`.

## Agregar un acceso nuevo

Agregar el nombre a `credenciales/.env.example` con un comentario de para qué
sirve, y a `espacio.json` → `credenciales` (o volver a correr `primeros-pasos`,
que los suma solo).
