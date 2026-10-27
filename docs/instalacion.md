# Instalación paso a paso

Sigue los pasos en orden. Cada comando se copia completo, se pega en la
terminal y se ejecuta con Enter. Toma unos 15 minutos la primera vez.

## Antes de empezar

Necesitas tres cosas:

1. Un computador con Windows 10 o más reciente, o una Mac con macOS 13 o más
   reciente.
2. Conexión a internet.
3. Una cuenta de Claude de pago: Pro, Max, Team o Enterprise. El plan gratuito
   no incluye Claude Code.

## Paso 1. Abre la terminal

La terminal es una ventana donde se escriben comandos.

**En Windows:** presiona la tecla Windows, escribe `PowerShell` y presiona
Enter. Sabes que estás en el lugar correcto si la línea empieza con `PS`, por
ejemplo `PS C:\Users\TuNombre>`.

**En Mac:** presiona Cmd + Espacio, escribe `Terminal` y presiona Enter.

## Paso 2. Instala Claude Code

Solo la primera vez. Si ya lo tienes, salta al paso 3.

**En Windows**, pega estos dos comandos, uno por uno:

```powershell
irm https://claude.ai/install.ps1 | iex
```

```powershell
winget install -e --id Git.Git
```

El segundo instala Git, que tu espacio de trabajo necesita en Windows. Si
Windows te pide permiso, acepta.

**En Mac:**

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

La instalación no muestra avances mientras descarga; espera a que termine.
Después **cierra la terminal y abre una nueva** (paso 1) y comprueba que
quedó bien:

```
claude --version
```

Si aparece un número de versión, sigue. Si dice que `claude` no se reconoce,
mira la sección «Si algo falla» al final.

## Paso 3. Crea tu carpeta de trabajo y entra en ella

Cambia `mi-proyecto` por el nombre de tu proyecto, sin espacios ni tildes
(por ejemplo `informes-ventas`).

**En Windows:**

```powershell
mkdir C:\trabajo\mi-proyecto -Force; cd C:\trabajo\mi-proyecto
```

**En Mac:**

```bash
mkdir -p ~/trabajo/mi-proyecto && cd ~/trabajo/mi-proyecto
```

Si ya tienes una carpeta con tus archivos, usa esa: escribe `cd` seguido de
su ruta. Tus archivos se respetan.

## Paso 4. Instala primeros-pasos

En la misma terminal, dentro de tu carpeta:

**En Windows:**

```powershell
irm https://raw.githubusercontent.com/davidortiz-ops/espacio-trabajo-claude/main/install.ps1 | iex
```

**En Mac:**

```bash
curl -fsSL https://raw.githubusercontent.com/davidortiz-ops/espacio-trabajo-claude/main/install.sh | bash
```

El instalador revisa si tienes Git, Python, Node.js y Playwright. Si falta
alguno, te pregunta «¿Instalo … ahora?»: responde `S` y Enter. Al final verás
«Listo: primeros-pasos quedó instalado».

## Paso 5. Abre Claude Code

En la misma terminal:

```
claude
```

La primera vez se abre el navegador para que inicies sesión con tu cuenta de
Claude. Después, Claude Code te pregunta si confías en la carpeta: elige la
opción que dice que sí.

## Paso 6. Escribe «empezar»

Escribe `empezar` y presiona Enter. Claude te hace unas preguntas: tu cargo,
tu proyecto, qué quieres lograr, tus tareas habituales y las herramientas que
usas. Responde con tus palabras; no hace falta que sea largo.

Mientras tanto investiga tu rol y al final te muestra una propuesta. Léela y
responde «Sí, prepáralo» o pide los cambios que quieras.

## Paso 7. Termina tu arranque

Claude te dice cuánto te falta para quedar al 100 %. Escribe `sigamos` y te
acompaña en lo siguiente. La primera tarea real la hacen juntos y, al
terminarla, te pregunta cuánto te habría tomado a mano.

## Cada día, para volver a trabajar

Abre la terminal (paso 1), entra a tu carpeta y abre Claude:

**En Windows:**

```powershell
cd C:\trabajo\mi-proyecto; claude
```

**En Mac:**

```bash
cd ~/trabajo/mi-proyecto && claude
```

Claude te recuerda dónde quedaste. Para una tarea habitual escribe `/` y el
nombre de su atajo.

## Si algo falla

| Lo que ves | Qué hacer |
|---|---|
| `claude` no se reconoce o no se encuentra | Cierra la terminal, abre una nueva y vuelve a probar |
| `'irm' is not recognized` | Estás en CMD, no en PowerShell. Vuelve al paso 1 y abre PowerShell |
| `The token '&&' is not a valid statement separator` | Estás en PowerShell usando el comando de Mac. Usa el de Windows |
| El instalador dice que estás en tu carpeta personal | Te faltó el paso 3: entra a tu carpeta de trabajo y repite el paso 4 |
| Claude dice que tu plan no incluye Claude Code | Necesitas un plan Pro, Max, Team o Enterprise |
| Claude no responde a «empezar» | Escribe `/primeros-pasos` o cierra y vuelve a abrir Claude en tu carpeta |
| Falta un programa después de instalarlo | Cierra y vuelve a abrir la terminal |

Si nada de esto lo resuelve, copia el mensaje exacto que ves y compártelo con
quien te está acompañando.
