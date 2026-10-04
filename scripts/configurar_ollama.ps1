# Configura Ollama Cloud en .env sin dejar la clave en el historial de PowerShell.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$envFile = Join-Path $root '.env'
if (-not (Test-Path $envFile)) { Copy-Item (Join-Path $root '.env.example') $envFile }

$secure = Read-Host 'Pega tu clave de Ollama Cloud (no se muestra; Enter para dejar la actual)' -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
$key = [Runtime.InteropServices.Marshal]::PtrToStringAuto($ptr)
[Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)

function Set-EnvVar([string]$name, [string]$value) {
    $lines = @(Get-Content $envFile)
    $found = $false
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match "^\s*$name=") { $lines[$i] = "$name=$value"; $found = $true }
    }
    if (-not $found) { $lines += "$name=$value" }
    [IO.File]::WriteAllLines($envFile, $lines, (New-Object Text.UTF8Encoding $false))
}

Set-EnvVar 'OLLAMA_BASE_URL' 'https://ollama.com/v1'
Set-EnvVar 'OLLAMA_MODEL' 'gpt-oss:120b'
Set-EnvVar 'OLLAMA_TIMEOUT_SECONDS' '60'
Set-EnvVar 'OLLAMA_MAX_CALLS_PER_DAY' '500'
if ($key) { Set-EnvVar 'OLLAMA_API_KEY' $key; Write-Host 'Clave guardada en .env (ignorado por git).' }
else { Write-Host 'Clave sin cambios.' }
Write-Host 'Ollama Cloud configurado: modelo gpt-oss:120b, tope 500 llamadas/dia, timeout 60s.'
