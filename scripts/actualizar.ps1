# Actualiza desde GitHub y reinicia consola del CEO + oficina pixel 2D.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host '== 1/5 Actualizando codigo =='
git pull --ff-only
if ($LASTEXITCODE -ne 0) { Write-Host 'git pull fallo (cambios locales o ramas distintas). Revisa "git status".'; exit 1 }

Write-Host '== 2/5 Dependencias Python =='
python -m pip install -q -r requirements.txt

Write-Host '== 3/5 Parando procesos viejos (puertos 8420 y 5173) =='
foreach ($port in 8420, 5173) {
    Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue |
        ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
}

$envFile = Join-Path $root '.env'
if (-not (Test-Path $envFile)) { Copy-Item (Join-Path $root '.env.example') $envFile }

Write-Host '== 4/5 Arrancando consola del CEO =='
Start-Process powershell -WorkingDirectory $root -ArgumentList '-NoExit', '-Command', 'python run_ceo_console.py'
Start-Sleep -Seconds 5

# El backend genera CONSOLE_TOKEN en .env en el primer arranque; la oficina lo copia.
$tokenLine = Get-Content $envFile | Where-Object { $_ -match '^\s*CONSOLE_TOKEN=.+' } | Select-Object -First 1
if (-not $tokenLine) { Write-Host 'No encuentro CONSOLE_TOKEN en .env. Espera unos segundos y vuelve a ejecutar.'; exit 1 }
$token = ($tokenLine -split '=', 2)[1].Trim()
$front = Join-Path $root 'office-frontend'
[IO.File]::WriteAllText((Join-Path $front '.env.local'), "VITE_CONSOLE_TOKEN=$token`n", (New-Object Text.UTF8Encoding $false))

Write-Host '== 5/5 Arrancando oficina pixel 2D =='
if (-not (Test-Path (Join-Path $front 'node_modules'))) {
    Push-Location $front; npm install; Pop-Location
}
Start-Process powershell -WorkingDirectory $front -ArgumentList '-NoExit', '-Command', 'npm run dev'
Start-Sleep -Seconds 4
Start-Process 'http://localhost:5173'
Write-Host 'Listo. Consola: http://127.0.0.1:8420/  |  Oficina pixel: http://localhost:5173/'
