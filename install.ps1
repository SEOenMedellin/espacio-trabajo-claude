# Instala o actualiza el skill primeros-pasos en el repositorio de la carpeta actual.
#
#   irm https://raw.githubusercontent.com/davidortiz-ops/espacio-trabajo-claude/main/install.ps1 | iex
#
# $env:PRIMEROS_PASOS_ORIGEN = '<carpeta>' instala desde una copia local (lo usan las pruebas).
& {
    $ErrorActionPreference = 'Stop'
    $ProgressPreference = 'SilentlyContinue'

    $repo = 'davidortiz-ops/espacio-trabajo-claude'
    $rama = if ($env:PRIMEROS_PASOS_RAMA) { $env:PRIMEROS_PASOS_RAMA } else { 'main' }

    function Falla($texto) {
        Write-Host "No se pudo instalar: $texto" -ForegroundColor Red
        throw 'instalacion-cancelada'
    }

    try {
        $destinoRepo = (Get-Location).ProviderPath
        if ($destinoRepo.TrimEnd('\') -ieq $HOME.TrimEnd('\')) {
            Falla 'estás en tu carpeta personal. Entra primero a la carpeta del repositorio donde vas a trabajar (cd ruta\a\tu-repositorio) y vuelve a ejecutar el comando.'
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
                Write-Host 'Descargando primeros-pasos…'
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
                if (Test-Path $anterior) { Remove-Item -Recurse -Force $anterior }
                Move-Item $destino $anterior
                Move-Item (Join-Path $tmp 'skill') $destino
                Remove-Item -Recurse -Force $anterior
            } else {
                $accion = 'instalado'
                Move-Item (Join-Path $tmp 'skill') $destino
            }
        } finally {
            Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
        }

        Write-Host ''
        Write-Host "Listo: primeros-pasos quedó $accion en $destino" -ForegroundColor Green

        $py = $null
        foreach ($c in @('python', 'python3', 'py')) {
            if (Get-Command $c -ErrorAction SilentlyContinue) {
                & $c -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>$null
                if ($LASTEXITCODE -eq 0) { $py = $c; break }
            }
        }
        if (-not $py) {
            Write-Host ''
            Write-Host 'Ojo: falta Python 3.10 o superior. Instálalo desde https://www.python.org/downloads/ antes de empezar.' -ForegroundColor Yellow
        }
        if (-not (Test-Path (Join-Path $destinoRepo '.git'))) {
            Write-Host 'Ojo: esta carpeta no es un repositorio git. Funciona igual, pero te conviene versionarla (git init).' -ForegroundColor Yellow
        }

        Write-Host ''
        Write-Host 'Siguiente paso: abre Claude Code en esta carpeta y escribe «empezar».'
    } catch {
        if ($_.Exception.Message -ne 'instalacion-cancelada') {
            Write-Host "No se pudo instalar: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}
