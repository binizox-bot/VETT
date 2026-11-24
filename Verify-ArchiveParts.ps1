[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repoRoot = $PSScriptRoot
$archiveDir = Join-Path $repoRoot 'archive'
$parts = @(Get-ChildItem -LiteralPath $archiveDir -Filter '*.part*' -File | Sort-Object Name)

if ($parts.Count -ne 2) {
    throw "Expected 2 archive parts, found $($parts.Count). Run 'git lfs pull' first."
}

$expectedPartHashes = @{}
foreach ($line in Get-Content -LiteralPath (Join-Path $archiveDir 'ARCHIVE_PARTS.sha256')) {
    if ($line -match '^([0-9a-fA-F]{64})\s{2}(.+)$') {
        $expectedPartHashes[$matches[2]] = $matches[1].ToLowerInvariant()
    }
}

$incremental = [Security.Cryptography.IncrementalHash]::CreateHash(
    [Security.Cryptography.HashAlgorithmName]::SHA256
)

try {
    foreach ($part in $parts) {
        $actualPartHash = (Get-FileHash -LiteralPath $part.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        $expectedPartHash = $expectedPartHashes[$part.Name]
        if ($actualPartHash -ne $expectedPartHash) {
            throw "Part hash mismatch: $($part.Name)"
        }

        $stream = [IO.File]::OpenRead($part.FullName)
        try {
            $buffer = New-Object byte[] (8MB)
            while (($read = $stream.Read($buffer, 0, $buffer.Length)) -gt 0) {
                $incremental.AppendData($buffer, 0, $read)
            }
        }
        finally {
            $stream.Dispose()
        }

        Write-Host "PASS part: $($part.Name)"
    }

    $combinedHash = [Convert]::ToHexString($incremental.GetHashAndReset()).ToLowerInvariant()
}
finally {
    $incremental.Dispose()
}

$sourceLine = (Get-Content -LiteralPath (Join-Path $archiveDir 'SOURCE_ARCHIVE.sha256') -Raw).Trim()
$expectedCombinedHash = ($sourceLine -split '\s+')[0].ToLowerInvariant()
if ($combinedHash -ne $expectedCombinedHash) {
    throw "Combined archive hash mismatch: expected $expectedCombinedHash, got $combinedHash"
}

Write-Host "PASS combined ZIP SHA-256: $combinedHash"
