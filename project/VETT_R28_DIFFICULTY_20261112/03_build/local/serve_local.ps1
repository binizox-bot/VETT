<#
.SYNOPSIS
    R28 local-inference service control script (Qwen2.5-7B / Ollama).

.DESCRIPTION
    One entry point for preflight / capability matrix / routing card / verification /
    degradation self-test / report.  Uses $env:VETT_PYTHON when set, otherwise the
    bundled DSH python on this machine, otherwise `python`.

.EXAMPLE
    .\serve_local.ps1 -Action preflight
    .\serve_local.ps1 -Action matrix
    .\serve_local.ps1 -Action verify
    .\serve_local.ps1 -Action all
#>
[CmdletBinding()]
param(
    [ValidateSet('preflight', 'matrix', 'routing', 'verify', 'selftest', 'report', 'all', 'help')]
    [string]$Action = 'preflight',

    [string]$Python = '',

    [switch]$AllowLowVram,

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Rest
)

$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

if (-not $Python) {
    $Python = $env:VETT_PYTHON
}
if (-not $Python) {
    $bundled = 'C:\Users\PC\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe'
    if (Test-Path -LiteralPath $bundled) { $Python = $bundled } else { $Python = 'python' }
}
if (-not (Test-Path -LiteralPath $Python)) {
    throw "python not found: $Python (set VETT_PYTHON or -Python)"
}

$arguments = @('-m', 'local_inference', $Action) + $Rest
if ($AllowLowVram -and $Action -in @('preflight', 'matrix')) {
    $arguments += '--allow-low-vram'
}

Write-Host "[serve_local] $Python $($arguments -join ' ')" -ForegroundColor DarkCyan
Push-Location -LiteralPath $here
try {
    & $Python @arguments
    $code = $LASTEXITCODE
} finally {
    Pop-Location
}
exit $code
