[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$CliDirectory
)

$ErrorActionPreference = 'Stop'
$resolvedCliDirectory = (Resolve-Path -LiteralPath $CliDirectory).Path
$candidates = [System.Collections.Generic.List[string]]::new()

$candidates.Add((Join-Path $resolvedCliDirectory 'node_modules\.bin\bun.exe'))

if ($env:BUN_INSTALL) {
    $candidates.Add((Join-Path $env:BUN_INSTALL 'bin\bun.exe'))
}

if ($env:USERPROFILE) {
    $candidates.Add((Join-Path $env:USERPROFILE '.bun\bin\bun.exe'))
}

$pathCommand = Get-Command bun -ErrorAction SilentlyContinue | Select-Object -First 1
if ($pathCommand -and $pathCommand.Source) {
    $candidates.Add($pathCommand.Source)
}

$coreSkillDirectory = Split-Path $PSScriptRoot -Parent
$skillsDirectory = Split-Path $coreSkillDirectory -Parent
$skillsContainer = Split-Path $skillsDirectory -Parent
$runtimeRoot = if ((Split-Path $skillsContainer -Leaf) -eq '.agents') {
    Split-Path $skillsContainer -Parent
}
else {
    $skillsContainer
}

$localToolsDirectory = Join-Path $runtimeRoot '.tools'
if (Test-Path -LiteralPath $localToolsDirectory -PathType Container) {
    Get-ChildItem -Path (Join-Path $localToolsDirectory 'bun-*\bun-windows-x64\bun.exe') -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTimeUtc -Descending |
        ForEach-Object { $candidates.Add($_.FullName) }
}

$seen = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
foreach ($candidate in $candidates) {
    if (-not $candidate -or -not $seen.Add($candidate)) { continue }
    if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) { continue }

    $resolvedCandidate = (Resolve-Path -LiteralPath $candidate).Path
    try {
        $null = & $resolvedCandidate --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            return $resolvedCandidate
        }
    }
    catch {
        continue
    }
}

throw "Bun executable not found for CLI directory: $resolvedCliDirectory"
