[CmdletBinding()]
param(
    [string]$OutputPath = (Join-Path $PSScriptRoot 'VETT_Cricket_Complete_Delivery_R19_20261017_FULL_20261124.zip'),
    [switch]$Extract,
    [string]$ExtractPath = (Join-Path $PSScriptRoot 'restored')
)

$ErrorActionPreference = 'Stop'
$archiveDir = Join-Path $PSScriptRoot 'archive'
$parts = @(Get-ChildItem -LiteralPath $archiveDir -Filter '*.part*' -File | Sort-Object Name)

if ($parts.Count -ne 2) {
    throw "Expected 2 archive parts, found $($parts.Count). Run 'git lfs pull' first."
}

$outputFullPath = [IO.Path]::GetFullPath($OutputPath)
$parent = Split-Path -Parent $outputFullPath
if (-not (Test-Path -LiteralPath $parent)) {
    New-Item -ItemType Directory -Path $parent | Out-Null
}

$output = [IO.File]::Create($outputFullPath)
try {
    foreach ($part in $parts) {
        $input = [IO.File]::OpenRead($part.FullName)
        try {
            $input.CopyTo($output)
        }
        finally {
            $input.Dispose()
        }
        Write-Host "Merged: $($part.Name)"
    }
}
finally {
    $output.Dispose()
}

$sourceLine = (Get-Content -LiteralPath (Join-Path $archiveDir 'SOURCE_ARCHIVE.sha256') -Raw).Trim()
$expectedHash = ($sourceLine -split '\s+')[0].ToLowerInvariant()
$actualHash = (Get-FileHash -LiteralPath $outputFullPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actualHash -ne $expectedHash) {
    throw "Restored ZIP hash mismatch: expected $expectedHash, got $actualHash"
}

Write-Host "PASS restored ZIP: $outputFullPath"
Write-Host "SHA-256: $actualHash"

if ($Extract) {
    if (Test-Path -LiteralPath $ExtractPath) {
        throw "ExtractPath already exists: $ExtractPath"
    }
    Expand-Archive -LiteralPath $outputFullPath -DestinationPath $ExtractPath
    Write-Host "Extracted to: $ExtractPath"
}
