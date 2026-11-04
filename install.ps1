# Instala o actualiza el skill Primer Paso (primeros-pasos) en la carpeta actual, sea cual sea su ruta.
#
#   irm https://raw.githubusercontent.com/SEOenMedellin/espacio-trabajo-claude/main/install.ps1 | iex
#
# $env:PRIMEROS_PASOS_ORIGEN = '<carpeta>' instala desde una copia local (lo usan las pruebas).
& {
    $ErrorActionPreference = 'Stop'
    $ProgressPreference = 'SilentlyContinue'

    $repo = 'SEOenMedellin/espacio-trabajo-claude'
    $rama = if ($env:PRIMEROS_PASOS_RAMA) { $env:PRIMEROS_PASOS_RAMA } else { 'main' }

    function Falla($texto) {
        Write-Host "No se pudo instalar: $texto" -ForegroundColor Red
        Write-Host 'Si no sabes cómo seguir, copia este mensaje y envíaselo a quien te compartió el enlace.'
        throw 'instalacion-cancelada'
    }

    try {
        # La carpeta personal, la raíz de un disco o la de Windows no son una carpeta de trabajo
        # (PowerShell como administrador abre en C:\Windows\System32).
        function No-Sirve($ruta) {
            $r = $ruta.TrimEnd('\')
            return ($r -ieq $HOME.TrimEnd('\')) -or ($r -match '^[A-Za-z]:$') -or
                   ($env:SystemRoot -and $r.StartsWith($env:SystemRoot, [StringComparison]::OrdinalIgnoreCase))
        }

        $destinoRepo = (Get-Location).ProviderPath
        if (No-Sirve $destinoRepo) {
            if ($env:PRIMEROS_PASOS_SIN_PROGRAMAS) {
                Falla 'no estás en una carpeta de trabajo. Entra primero a la carpeta donde vas a trabajar y vuelve a ejecutar el comando.'
            }
            Write-Host "Estás en $destinoRepo, que no es una carpeta de trabajo."
            $ruta = Read-Host 'Escribe la ruta de la carpeta donde vas a trabajar (o arrástrala aquí desde el Explorador) y presiona Enter'
            $ruta = "$ruta".Trim()
            if ($ruta.StartsWith('& ')) { $ruta = $ruta.Substring(2).Trim() }
            $ruta = $ruta.Trim('"').Trim("'")
            if ($ruta -eq '~' -or $ruta.StartsWith('~\') -or $ruta.StartsWith('~/')) { $ruta = $HOME + $ruta.Substring(1) }
            if (-not $ruta) { Falla 'no se recibió ninguna carpeta.' }
            if (-not (Test-Path -LiteralPath $ruta -PathType Container)) {
                $r = Read-Host "La carpeta $ruta no existe. ¿La creo? [S/n]"
                if ($r -match '^(n|no)$') { Falla "la carpeta $ruta no existe." }
                New-Item -ItemType Directory -Force -Path $ruta | Out-Null
            }
            $destinoRepo = (Resolve-Path -LiteralPath $ruta).ProviderPath
            if (No-Sirve $destinoRepo) { Falla 'esa no es una carpeta de trabajo: elige o crea una carpeta para tu proyecto.' }
            Set-Location -LiteralPath $destinoRepo
        }

        $tmp = Join-Path ([IO.Path]::GetTempPath()) ('primeros-pasos-' + [guid]::NewGuid().ToString('N'))
        New-Item -ItemType Directory -Path $tmp | Out-Null
        try {
            if ($env:PRIMEROS_PASOS_ORIGEN) {
                if (-not (Test-Path (Join-Path $env:PRIMEROS_PASOS_ORIGEN 'skill\SKILL.md'))) {
                    Falla "$env:PRIMEROS_PASOS_ORIGEN no contiene skill\SKILL.md."
                }
                Copy-Item -Recurse (Join-Path $env:PRIMEROS_PASOS_ORIGEN 'skill') (Join-Path $tmp 'skill')
            } else {
                Write-Host 'Descargando Primer Paso…'
                [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
                $zip = Join-Path $tmp 'skill.zip'
                try {
                    Invoke-WebRequest -UseBasicParsing -Uri "https://codeload.github.com/$repo/zip/refs/heads/$rama" -OutFile $zip
                } catch {
                    Falla 'no se pudo descargar de GitHub. Revisa tu conexión.'
                }
                Expand-Archive -Path $zip -DestinationPath (Join-Path $tmp 'zip')
                $carpeta = Get-ChildItem (Join-Path $tmp 'zip') -Directory | Select-Object -First 1
                if (-not $carpeta -or -not (Test-Path (Join-Path $carpeta.FullName 'skill\SKILL.md'))) {
                    Falla 'la descarga no trae la carpeta skill.'
                }
                Move-Item (Join-Path $carpeta.FullName 'skill') (Join-Path $tmp 'skill')
            }
            Get-ChildItem (Join-Path $tmp 'skill') -Recurse -Directory -Filter '__pycache__' |
                Remove-Item -Recurse -Force

            $skills = Join-Path $destinoRepo '.claude\skills'
            $destino = Join-Path $skills 'primeros-pasos'
            New-Item -ItemType Directory -Force -Path $skills | Out-Null
            if (Test-Path $destino) {
                $accion = 'actualizado'
                $anterior = "$destino.anterior"
                try {
                    if (Test-Path $anterior) { Remove-Item -Recurse -Force $anterior }
                    Move-Item $destino $anterior
                } catch {
                    Falla 'algún archivo del skill está en uso. Cierra Claude Code (y los editores abiertos en esta carpeta) y vuelve a ejecutar el comando.'
                }
                Move-Item (Join-Path $tmp 'skill') $destino
                Remove-Item -Recurse -Force $anterior -ErrorAction SilentlyContinue
            } else {
                $accion = 'instalado'
                Move-Item (Join-Path $tmp 'skill') $destino
            }
        } finally {
            Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
        }

        Write-Host ''
        Write-Host "Listo: Primer Paso quedó $accion en tu carpeta $destinoRepo" -ForegroundColor Green

        # ---- Programas para trabajar: Git, Python, Node.js y Playwright
        function Refrescar-Path {
            $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' +
                        [Environment]::GetEnvironmentVariable('Path', 'User')
        }
        # Ejecuta un programa sin que su salida de error tumbe el instalador: en
        # PowerShell 5.1, con ErrorActionPreference = Stop, cualquier línea en
        # stderr de un programa externo se vuelve una excepción.
        function Ejecutar([string]$exe, [string[]]$argumentos) {
            $previo = $ErrorActionPreference
            $ErrorActionPreference = 'Continue'
            try {
                $salida = & $exe @argumentos 2>&1 | ForEach-Object { "$_" }
                return @{ ok = ($LASTEXITCODE -eq 0); salida = ($salida -join "`n") }
            } catch {
                return @{ ok = $false; salida = '' }
            } finally {
                $ErrorActionPreference = $previo
            }
        }
        # El primer Python 3.10+ real: no el acceso directo de la Microsoft Store.
        function Buscar-Python {
            foreach ($c in @(@('python'), @('python3'), @('py', '-3'))) {
                $cmd = Get-Command $c[0] -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
                if ($cmd -and $cmd.Source -notlike '*WindowsApps*') {
                    $previos = @($c | Select-Object -Skip 1)
                    $r = Ejecutar $cmd.Source ($previos + @('-c', 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'))
                    if ($r.ok) { return @{ exe = $cmd.Source; previos = $previos } }
                }
            }
            return $null
        }
        function Tiene-Python { return [bool](Buscar-Python) }
        function Tiene-Node {
            if (-not (Get-Command node -ErrorAction SilentlyContinue)) { return $false }
            $r = Ejecutar 'node' @('--version')
            if (-not $r.ok -or $r.salida -notmatch 'v(\d+)') { return $false }
            return ([int]$Matches[1] -ge 18)
        }
        function Tiene-Playwright { return [bool](Get-Command playwright -ErrorAction SilentlyContinue) }

        $hayWinget = [bool](Get-Command winget -ErrorAction SilentlyContinue)
        $programas = @(
            @{ nombre = 'git'; prueba = { [bool](Get-Command git -ErrorAction SilentlyContinue) }; descarga = 'https://git-scm.com/downloads'
               orden = $(if ($hayWinget) { 'winget install -e --id Git.Git --accept-package-agreements --accept-source-agreements' }) },
            @{ nombre = 'python'; prueba = { Tiene-Python }; descarga = 'https://www.python.org/downloads/'
               orden = $(if ($hayWinget) { 'winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements' }) },
            @{ nombre = 'node'; prueba = { Tiene-Node }; descarga = 'https://nodejs.org/'
               orden = $(if ($hayWinget) { 'winget install -e --id OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements' }) },
            @{ nombre = 'playwright'; prueba = { Tiene-Playwright }; descarga = 'https://playwright.dev/docs/intro'
               # npm.cmd y no npm: npm.ps1 lo bloquea la política de scripts que Windows trae por defecto.
               orden = 'npm.cmd install -g playwright; if ($?) { npx.cmd playwright install chromium }' }
        )
        $interactivo = (-not $env:PRIMEROS_PASOS_SIN_PROGRAMAS) -and (-not [Console]::IsInputRedirected) -and
                       [Environment]::UserInteractive

        $titulos = @{ git = 'Git'; python = 'Python'; node = 'Node.js'; playwright = 'Playwright' }
        $paraQue = @{ git = 'guarda el historial de tus archivos'; python = 'hace funcionar tu espacio de trabajo'
                      node = 'lo necesitan algunas herramientas'; playwright = 'permite a Claude revisar páginas web' }

        Write-Host ''
        Write-Host 'Programas para trabajar (revisando que tengas lo necesario):'
        $pendientes = @()
        foreach ($p in $programas) {
            $nombre = $titulos[$p.nombre]
            if (& $p.prueba) { Write-Host "  [listo]  $nombre" -ForegroundColor Green; continue }
            Write-Host "  [falta]  $nombre, $($paraQue[$p.nombre])" -ForegroundColor Yellow
            $orden = $p.orden
            if ($p.nombre -eq 'playwright' -and -not (Tiene-Node)) { $orden = $null }
            if ($orden -and $interactivo) {
                $r = Read-Host "           ¿Lo instalo ahora? Escribe S y presiona Enter (o N para dejarlo para después)"
                if ($r -notmatch '^\s*(n|no)\s*$') {
                    Write-Host '           Instalando… puede tardar unos minutos. Si Windows pregunta si permites cambios, responde Sí.'
                    try { Invoke-Expression $orden | Out-Null } catch { }
                    Refrescar-Path
                    if (& $p.prueba) { Write-Host "  [listo]  $nombre" -ForegroundColor Green; continue }
                }
            }
            $pendientes += $nombre
        }

        # ---- Que «empezar», «iniciar» o «configurar» activen el skill
        # (también repara los ajustes de una instalación anterior)
        $py = Buscar-Python
        $activado = $false
        if ($py) {
            $r = Ejecutar $py.exe ($py.previos + @((Join-Path $destino 'scripts\activar.py'), '--registrar', '--raiz', $destinoRepo))
            $activado = $r.ok
        }

        Write-Host ''
        if (-not $py) {
            Write-Host 'Falta un paso: Python no quedó instalado y sin él tu espacio no puede prepararse.' -ForegroundColor Yellow
            Write-Host 'Instálalo desde https://www.python.org/downloads/ (marca la casilla «Add python.exe to PATH»),'
            Write-Host 'cierra esta ventana, ábrela de nuevo y vuelve a pegar el mismo comando de instalación.'
            return
        }
        if (-not $activado) {
            Write-Host 'Casi listo: no pude activar la palabra «empezar», pero puedes escribir /primeros-pasos en Claude.' -ForegroundColor Yellow
        }
        if ($pendientes.Count -gt 0) {
            Write-Host ("Quedó pendiente: " + ($pendientes -join ', ') + '. No te preocupes: Claude te ayuda a instalarlo cuando escribas «empezar».')
            Write-Host ''
        }
        Write-Host 'Siguiente paso: escribe la palabra claude y presiona Enter.' -ForegroundColor Green
        Write-Host 'Cuando Claude se abra, escribe empezar y presiona Enter. Claude te guía desde ahí.'
        Write-Host ''
        Write-Host '(Otro día, para volver, abre PowerShell en esta misma carpeta y escribe claude:'
        Write-Host "  cd `"$destinoRepo`""
        Write-Host '  claude )'
    } catch {
        if ($_.Exception.Message -ne 'instalacion-cancelada') {
            Write-Host 'No se pudo instalar. Vuelve a pegar el mismo comando; si se repite, copia este mensaje y envíaselo a quien te compartió el enlace:' -ForegroundColor Red
            Write-Host "  $($_.Exception.Message)"
        }
    }
}
