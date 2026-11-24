[CmdletBinding()]
param(
    [switch]$RemoveSource
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$condaCommand = Get-Command conda -ErrorAction Stop
$targetRoot = 'D:\CondaData\envs'
$expectedTargetRoot = [System.IO.Path]::GetFullPath($targetRoot)

if ($expectedTargetRoot -ne $targetRoot) {
    throw "Unexpected target root: $expectedTargetRoot"
}

New-Item -ItemType Directory -Path $targetRoot -Force | Out-Null

$migrations = @(
    [pscustomobject]@{
        Name   = 'binizox-dev'
        Source = 'C:\Users\PC\.conda\envs\binizox-dev'
        Target = 'D:\CondaData\envs\binizox-dev'
    }
    [pscustomobject]@{
        Name   = 'railway-telemetry'
        Source = 'C:\Users\PC\.conda\envs\railway-telemetry'
        Target = 'D:\CondaData\envs\railway-telemetry'
    }
    [pscustomobject]@{
        Name   = 'binizox-parser'
        Source = 'C:\Users\PC\.conda\envs\binizox-parser'
        Target = 'D:\CondaData\envs\binizox-parser'
    }
    [pscustomobject]@{
        Name   = 'paddleocr-workspace'
        Source = 'D:\Download\PaddleOCR_Workspace\env'
        Target = 'D:\CondaData\envs\paddleocr-workspace'
    }
)

function Get-PackageSignature {
    param([Parameter(Mandatory)][string]$Prefix)

    $json = & $condaCommand.Source list --prefix $Prefix --json
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to read package list: $Prefix"
    }

    return @(
        $json |
            ConvertFrom-Json |
            ForEach-Object {
                '{0}|{1}|{2}|{3}' -f $_.name, $_.version, $_.build_string, $_.channel
            } |
            Sort-Object
    )
}

function Test-TargetEnvironment {
    param(
        [Parameter(Mandatory)][pscustomobject]$Migration,
        [Parameter(Mandatory)][string[]]$SourceSignature
    )

    $targetSignature = Get-PackageSignature -Prefix $Migration.Target
    $difference = @(Compare-Object -ReferenceObject $SourceSignature -DifferenceObject $targetSignature)
    if ($difference.Count -ne 0) {
        $difference | Format-Table | Out-String | Write-Host
        throw "Package verification failed: $($Migration.Name)"
    }

    & $condaCommand.Source run --prefix $Migration.Target python --version
    if ($LASTEXITCODE -ne 0) {
        throw "Python smoke test failed: $($Migration.Target)"
    }
}

Write-Host 'Using D:\CondaData for writable Conda environments and package cache.'

$verified = @()

foreach ($migration in $migrations) {
    if (-not (Test-Path -LiteralPath (Join-Path $migration.Source 'conda-meta'))) {
        if (Test-Path -LiteralPath (Join-Path $migration.Target 'conda-meta')) {
            Write-Host "Source already removed; smoke-testing existing target: $($migration.Target)"
            & $condaCommand.Source run --prefix $migration.Target python --version
            if ($LASTEXITCODE -ne 0) {
                throw "Existing target failed smoke test: $($migration.Target)"
            }
            $verified += $migration
            continue
        }
        throw "Neither source nor a valid target environment exists: $($migration.Name)"
    }

    $targetFullPath = [System.IO.Path]::GetFullPath($migration.Target)
    if (-not $targetFullPath.StartsWith($expectedTargetRoot + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Target escaped D:\CondaData\envs: $targetFullPath"
    }

    $sourceSignature = Get-PackageSignature -Prefix $migration.Source

    if (-not (Test-Path -LiteralPath $migration.Target)) {
        Write-Host "Cloning $($migration.Name): $($migration.Source) -> $($migration.Target)"
        & $condaCommand.Source create --prefix $migration.Target --clone $migration.Source --yes
        if ($LASTEXITCODE -ne 0) {
            throw "Clone failed: $($migration.Name)"
        }
    }
    else {
        Write-Host "Target already exists; verifying: $($migration.Target)"
    }

    Test-TargetEnvironment -Migration $migration -SourceSignature $sourceSignature
    $verified += $migration
    Write-Host "Verified: $($migration.Name)"
}

if ($verified.Count -ne $migrations.Count) {
    throw 'Not every environment was verified; source removal is disabled.'
}

if ($RemoveSource) {
    Write-Host 'All targets verified. Removing old source environments ...'
    foreach ($migration in $migrations) {
        if (-not (Test-Path -LiteralPath (Join-Path $migration.Source 'conda-meta'))) {
            Write-Host "Source already absent: $($migration.Source)"
            continue
        }
        & $condaCommand.Source env remove --prefix $migration.Source --yes
        if ($LASTEXITCODE -ne 0) {
            throw "Source removal failed: $($migration.Source)"
        }
        Write-Host "Removed source: $($migration.Source)"
    }
}
else {
    Write-Host 'Targets verified. No source removal was requested; any source environments still present were kept.'
}

Write-Host 'Final environment list:'
& $condaCommand.Source env list
