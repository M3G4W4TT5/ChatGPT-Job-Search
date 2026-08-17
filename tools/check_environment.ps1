[CmdletBinding()]
param(
    [switch]$Json,
    [switch]$RequireAll
)

$ErrorActionPreference = 'Stop'
$repositoryRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$upstreamConfig = Get-Content -LiteralPath (Join-Path $repositoryRoot 'config\upstream.json') -Raw | ConvertFrom-Json

function Get-FirstVersionLine {
    param(
        [Parameter(Mandatory)] [string]$Executable,
        [string[]]$Arguments = @('--version')
    )
    $previousPreference = $ErrorActionPreference
    try {
        # Several Windows-native tools print version banners to stderr.
        $ErrorActionPreference = 'Continue'
        $output = & $Executable @Arguments 2>&1
        if ($LASTEXITCODE -ne 0) { return $null }
        return (($output | Select-Object -First 1) -as [string]).Trim()
    }
    catch {
        return $null
    }
    finally {
        $ErrorActionPreference = $previousPreference
    }
}

function Find-Executable {
    param(
        [Parameter(Mandatory)] [string]$Name,
        [string[]]$Fallbacks = @()
    )
    foreach ($fallback in $Fallbacks) {
        if ($fallback -and (Test-Path -LiteralPath $fallback -PathType Leaf)) {
            return (Resolve-Path -LiteralPath $fallback).Path
        }
    }
    $command = Get-Command $Name -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($command) { return $command.Source }
    return $null
}

function Find-NewestLocalTool {
    param([Parameter(Mandatory)] [string]$Pattern)
    $match = Get-ChildItem -Path (Join-Path $repositoryRoot $Pattern) -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTimeUtc -Descending |
        Select-Object -First 1
    if ($match) { return $match.FullName }
    return $null
}

$popplerBase = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin'
$localBun = Find-NewestLocalTool -Pattern '.tools\bun-*\bun-windows-x64\bun.exe'
$localMiKTeX = Join-Path $repositoryRoot '.tools\miktex-portable\texmfs\install\miktex\bin\x64'
$localPdfInfo = Find-NewestLocalTool -Pattern '.tools\poppler-*\poppler-*\Library\bin\pdfinfo.exe'
$localPdfText = Find-NewestLocalTool -Pattern '.tools\poppler-*\poppler-*\Library\bin\pdftotext.exe'
$localPdfPpm = Find-NewestLocalTool -Pattern '.tools\poppler-*\poppler-*\Library\bin\pdftoppm.exe'
$pythonCommand = 'python'
$pythonArguments = @('--version')
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    $pyLauncher = Get-Command py -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($pyLauncher) {
        $pythonCommand = 'py'
        $pythonArguments = @('-3', '--version')
    }
}
$specs = @(
    @{ Name = 'git'; Command = 'git'; Args = @('--version'); Fallbacks = @() },
    @{ Name = 'python'; Command = $pythonCommand; Args = $pythonArguments; Fallbacks = @() },
    @{ Name = 'bun'; Command = 'bun'; Args = @('--version'); Fallbacks = @($localBun) },
    @{ Name = 'lualatex'; Command = 'lualatex'; Args = @('--version'); Fallbacks = @(Join-Path $localMiKTeX 'lualatex.exe') },
    @{ Name = 'xelatex'; Command = 'xelatex'; Args = @('--version'); Fallbacks = @(Join-Path $localMiKTeX 'xelatex.exe') },
    @{ Name = 'pdfinfo'; Command = 'pdfinfo'; Args = @('-v'); Fallbacks = @($localPdfInfo, (Join-Path $popplerBase 'pdfinfo.exe')) },
    @{ Name = 'pdftotext'; Command = 'pdftotext'; Args = @('-v'); Fallbacks = @($localPdfText, (Join-Path $popplerBase 'pdftotext.exe')) },
    @{ Name = 'pdftoppm'; Command = 'pdftoppm'; Args = @('-v'); Fallbacks = @($localPdfPpm, (Join-Path $popplerBase 'pdftoppm.exe')) }
)

$tools = foreach ($spec in $specs) {
    $path = Find-Executable -Name $spec.Command -Fallbacks $spec.Fallbacks
    $version = if ($path) { Get-FirstVersionLine -Executable $path -Arguments $spec.Args } else { $null }
    [pscustomobject]@{
        name = $spec.Name
        found = [bool]($path -and $version)
        path = $path
        version = $version
    }
}

$upstream = $null
try {
    $upstream = (& git -C $repositoryRoot remote get-url upstream 2>$null).Trim()
}
catch {
    $upstream = $null
}

$result = [pscustomobject]@{
    repository = $repositoryRoot
    upstream = $upstream
    expected_upstream = $upstreamConfig.url
    upstream_configured = ($upstream -eq $upstreamConfig.url)
    tools = @($tools)
    missing = @($tools | Where-Object { -not $_.found } | ForEach-Object name)
}

if ($Json) {
    $result | ConvertTo-Json -Depth 5
}
else {
    "Repository: $repositoryRoot"
    "Upstream: $(if ($upstream) { $upstream } else { '<missing>' })"
    "Expected: $($upstreamConfig.url)"
    foreach ($tool in $tools) {
        $status = if ($tool.found) { 'FOUND' } else { 'MISSING' }
        "{0,-10} {1,-7} {2}" -f $tool.name, $status, $(if ($tool.path) { $tool.path } else { '' })
        if ($tool.version) { "             $($tool.version)" }
    }
}

if ($RequireAll -and $result.missing.Count -gt 0) { exit 1 }
exit 0
