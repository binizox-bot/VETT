<#
.SYNOPSIS
    VETT-R28 pre-change baseline restore script.

.DESCRIPTION
    Restores the frozen R26.15 candidate and/or the code snapshot from
    _BACKUPS\VETT_R28_PRE_CHANGE_20261112\ back into the main project.

    Safety behaviour:
      * Every target absolute path is printed before anything is written.
      * Backup integrity is verified against PROTECTED_PATHS.json (frozen) and
        CODE_MANIFEST.json (code) before writing; any mismatch aborts (exit 1).
      * Interactive confirmation is required; the exact word RESTORE must be typed.
        Default answer (empty) aborts. -DryRun never writes and never prompts.
      * Extra files already present in a target but absent from the backup are
        reported and kept unless -DeleteExtras is given explicitly.

.PARAMETER Scope
    all (default) | frozen | code

.PARAMETER DryRun
    Print the plan (absolute targets, counts, bytes, integrity result) and exit
    without writing or prompting.

.PARAMETER DeleteExtras
    Also remove files in the target that do not exist in the backup snapshot.
    Off by default: restore only overwrites/creates files.

.EXAMPLE
    pwsh -NoProfile -File restore.ps1 -DryRun
    pwsh -NoProfile -File restore.ps1 -Scope frozen
    pwsh -NoProfile -File restore.ps1 -Scope all
#>
[CmdletBinding()]
param(
    [ValidateSet('all', 'frozen', 'code')]
    [string]$Scope = 'all',
    [switch]$DryRun,
    [switch]$DeleteExtras
)

$ErrorActionPreference = 'Stop'

function Fail([string]$message) {
    Write-Host "ABORT: $message" -ForegroundColor Red
    exit 1
}

# ---------------------------------------------------------------- path anchors
$BackupRoot = $PSScriptRoot
if (-not $BackupRoot) { Fail 'cannot determine script directory ($PSScriptRoot empty)' }

$BackupsParent = Split-Path -Parent $BackupRoot
$Workspace = Split-Path -Parent $BackupsParent
$Project = Join-Path $Workspace 'VETT_Cricket_v0.22_R16_Multisource_Dilemmas'
$CandRel = 'r26_15_content_dependency_candidate_v3'
$FrozenSrc = Join-Path (Join-Path $BackupRoot 'frozen') $CandRel
$FrozenDst = Join-Path $Project $CandRel
$CodeSrc = Join-Path $BackupRoot 'code'
$FullManifest = Join-Path $BackupRoot 'FULL_FILE_MANIFEST.json'
$CodeManifest = Join-Path $BackupRoot 'CODE_MANIFEST.json'
$Protected = Join-Path $BackupRoot 'PROTECTED_PATHS.json'

# Hard guards: the computed project root must look like the real project and the
# frozen target must be the exact candidate directory (no fuzzy resolution).
if (-not (Test-Path -LiteralPath $Project -PathType Container)) {
    Fail "project root not found: $Project"
}
if (-not (Test-Path -LiteralPath (Join-Path $Project 'src') -PathType Container)) {
    Fail "project root sanity check failed (missing src\): $Project"
}
if ([IO.Path]::GetFileName($FrozenDst) -ne $CandRel) {
    Fail "frozen target name mismatch: $FrozenDst"
}

$DoFrozen = $Scope -in @('all', 'frozen')
$DoCode = $Scope -in @('all', 'code')

Write-Host '=== VETT-R28 baseline restore ==='
Write-Host "Backup root : $BackupRoot"
Write-Host "Workspace   : $Workspace"
Write-Host "Project     : $Project"
Write-Host "Scope       : $Scope"
Write-Host "Mode        : $(if ($DryRun) { 'DRY-RUN (no writes)' } else { 'REAL RESTORE (prompts for confirmation)' })"

# ------------------------------------------------------------- backup presence
if ($DoFrozen) {
    if (-not (Test-Path -LiteralPath $FrozenSrc -PathType Container)) { Fail "missing frozen backup: $FrozenSrc" }
    if (-not (Test-Path -LiteralPath $Protected -PathType Leaf)) { Fail "missing PROTECTED_PATHS.json: $Protected" }
}
if ($DoCode) {
    if (-not (Test-Path -LiteralPath $CodeSrc -PathType Container)) { Fail "missing code backup: $CodeSrc" }
    if (-not (Test-Path -LiteralPath $CodeManifest -PathType Leaf)) { Fail "missing CODE_MANIFEST.json: $CodeManifest" }
}
if (-not (Test-Path -LiteralPath $FullManifest -PathType Leaf)) {
    Write-Host "WARN: FULL_FILE_MANIFEST.json not found (not required for restore): $FullManifest"
}

# --------------------------------------------------------- plan + integrity
$FrozenPlan = @()
$CodePlan = @()
$IntegrityErrors = New-Object System.Collections.Generic.List[string]

if ($DoFrozen) {
    $prot = Get-Content -LiteralPath $Protected -Raw | ConvertFrom-Json
    $group = $prot.groups | Where-Object { $_.id -eq 'r26_15_candidate' }
    if (-not $group) { Fail 'PROTECTED_PATHS.json has no r26_15_candidate group' }
    $expected = @{}
    foreach ($f in $group.files) { $expected[$f.path] = $f }
    $present = @{}
    $frozenFiles = Get-ChildItem -LiteralPath $FrozenSrc -Recurse -File -Force
    foreach ($f in $frozenFiles) {
        $rel = [IO.Path]::GetRelativePath($FrozenSrc, $f.FullName).Replace('\', '/')
        $key = "$CandRel/$rel"
        $present[$key] = $true
        if (-not $expected.ContainsKey($key)) {
            $IntegrityErrors.Add("frozen backup has unexpected file: $key")
            continue
        }
        $h = (Get-FileHash -LiteralPath $f.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        $want = $expected[$key]
        if ($h -ne $want.sha256 -or $f.Length -ne [int64]$want.bytes) {
            $IntegrityErrors.Add("frozen backup integrity mismatch: $key")
        }
        $FrozenPlan += [pscustomobject]@{
            BackupPath = $f.FullName
            TargetPath = (Join-Path $FrozenDst $rel.Replace('/', [IO.Path]::DirectorySeparatorChar))
            Bytes      = $f.Length
            Sha256     = $h
        }
    }
    foreach ($k in $expected.Keys) {
        if (-not $present.ContainsKey($k)) {
            $IntegrityErrors.Add("frozen backup missing expected file: $k")
        }
    }
    if ($group.file_count -ne $FrozenPlan.Count) {
        $IntegrityErrors.Add("frozen backup file count $($FrozenPlan.Count) != expected $($group.file_count)")
    }
}

if ($DoCode) {
    $cm = Get-Content -LiteralPath $CodeManifest -Raw | ConvertFrom-Json
    foreach ($entry in $cm.files) {
        $src = Join-Path $CodeSrc ($entry.path.Replace('/', [IO.Path]::DirectorySeparatorChar))
        if (-not (Test-Path -LiteralPath $src -PathType Leaf)) {
            $IntegrityErrors.Add("code backup missing: $($entry.path)")
            continue
        }
        $h = (Get-FileHash -LiteralPath $src -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($h -ne $entry.sha256) {
            $IntegrityErrors.Add("code backup integrity mismatch: $($entry.path)")
        }
        $CodePlan += [pscustomobject]@{
            BackupPath = $src
            TargetPath = (Join-Path $Project ($entry.path.Replace('/', [IO.Path]::DirectorySeparatorChar)))
            Bytes      = (Get-Item -LiteralPath $src).Length
            Sha256     = $h
        }
    }
    if ($cm.file_count -ne $CodePlan.Count) {
        $IntegrityErrors.Add("code backup file count $($CodePlan.Count) != expected $($cm.file_count)")
    }
}

Write-Host ''
Write-Host '--- target absolute paths (nothing written yet) ---'
if ($DoFrozen) {
    Write-Host ("TARGET: {0}  ({1} files)" -f $FrozenDst, $FrozenPlan.Count)
}
if ($DoCode) {
    Write-Host ("TARGET: {0}  (code snapshot root; {1} files)" -f $Project, $CodePlan.Count)
    $codeDirs = @('src', 'tests', 'design', 'eval_configs', 'analysis', 'eval_runs')
    foreach ($d in $codeDirs) {
        Write-Host ("TARGET: {0}" -f (Join-Path $Project $d))
    }
    foreach ($f in @('README.md', 'CHANGELOG.md', '.gitignore')) {
        Write-Host ("TARGET: {0}" -f (Join-Path $Project $f))
    }
}
Write-Host ''
Write-Host ("Plan: frozen={0} files / {1:N0} bytes ; code={2} files / {3:N0} bytes" -f `
    $FrozenPlan.Count, (($FrozenPlan | Measure-Object Bytes -Sum).Sum), `
    $CodePlan.Count, (($CodePlan | Measure-Object Bytes -Sum).Sum))

if ($IntegrityErrors.Count -gt 0) {
    Write-Host ''
    Write-Host '--- backup integrity FAILED ---' -ForegroundColor Red
    $IntegrityErrors | Select-Object -First 25 | ForEach-Object { Write-Host "  $_" }
    Fail ("backup integrity check failed with {0} error(s); refusing to restore" -f $IntegrityErrors.Count)
}
Write-Host 'Backup integrity: PASS (all files match PROTECTED_PATHS.json / CODE_MANIFEST.json)'

# ------------------------------------------------------------ extras (report)
$ExtraTargets = @()
if ($DoCode) {
    foreach ($dir in @('src', 'tests', 'design', 'eval_configs', 'analysis', 'eval_runs')) {
        $targetRoot = Join-Path $Project $dir
        if (-not (Test-Path -LiteralPath $targetRoot)) { continue }
        $have = @{}
        foreach ($p in $CodePlan) {
            if ($p.TargetPath.StartsWith($targetRoot, [StringComparison]::OrdinalIgnoreCase)) {
                $have[$p.TargetPath.ToLowerInvariant()] = $true
            }
        }
        foreach ($f in (Get-ChildItem -LiteralPath $targetRoot -Recurse -File -Force)) {
            if ($f.Extension -eq '.pyc') { continue }
            if ($f.FullName -match '[\\/]__pycache__[\\/]') { continue }
            if (-not $have.ContainsKey($f.FullName.ToLowerInvariant())) { $ExtraTargets += $f.FullName }
        }
    }
}
if ($ExtraTargets.Count -gt 0) {
    Write-Host ''
    Write-Host ("NOTE: {0} file(s) exist in the target but not in the backup; they are KEPT unless -DeleteExtras is passed." -f $ExtraTargets.Count)
    $ExtraTargets | Select-Object -First 10 | ForEach-Object { Write-Host "  keep: $_" }
}

# ---------------------------------------------------------------- dry-run exit
if ($DryRun) {
    Write-Host ''
    Write-Host 'DRY-RUN: no files were written, no confirmation was requested.'
    exit 0
}

# ------------------------------------------------------------- confirmation
Write-Host ''
Write-Host 'The restore will overwrite the paths listed above with the frozen backup.' -ForegroundColor Yellow
$answer = Read-Host 'Type RESTORE to proceed (anything else aborts)'
if ($answer -cne 'RESTORE') {
    Write-Host 'Aborted by operator; nothing was written.'
    exit 1
}

# ------------------------------------------------------------------- restore
$restored = 0
$failed = @()
foreach ($p in ($FrozenPlan + $CodePlan)) {
    try {
        $parent = Split-Path -Parent $p.TargetPath
        if (-not (Test-Path -LiteralPath $parent -PathType Container)) {
            New-Item -ItemType Directory -Path $parent -Force | Out-Null
        }
        Copy-Item -LiteralPath $p.BackupPath -Destination $p.TargetPath -Force
        $h = (Get-FileHash -LiteralPath $p.TargetPath -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($h -ne $p.Sha256) { throw "post-copy hash mismatch: $($p.TargetPath)" }
        $restored++
    }
    catch {
        $failed += "$($p.TargetPath) :: $($_.Exception.Message)"
    }
}

if ($DeleteExtras -and $ExtraTargets.Count -gt 0) {
    foreach ($f in $ExtraTargets) {
        try { Remove-Item -LiteralPath $f -Force; Write-Host "deleted extra: $f" }
        catch { $failed += "$f :: $($_.Exception.Message)" }
    }
}

Write-Host ''
Write-Host ("Restored {0} file(s); failures: {1}" -f $restored, $failed.Count)
if ($failed.Count -gt 0) {
    $failed | Select-Object -First 25 | ForEach-Object { Write-Host "  $_" }
    exit 1
}
Write-Host 'RESTORE OK'
exit 0
