$ErrorActionPreference = 'Stop'
$root = (Get-Item -LiteralPath 'G:\毕设').FullName.TrimEnd('\')
$old = Join-Path $root '99_archive\workspace_cleanup_20261123'
$plan = Get-Content -LiteralPath (Join-Path $old 'refresh_plan.json') -Raw | ConvertFrom-Json
function Inside([string]$relative) {
    $p = [System.IO.Path]::GetFullPath((Join-Path $root $relative))
    if (-not $p.StartsWith($root+'\',[System.StringComparison]::OrdinalIgnoreCase)) {throw "Outside workspace: $p"}
    return $p
}
if ((Get-FileHash -LiteralPath (Inside $plan.history.path) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $plan.history.sha256) {throw 'History archive hash mismatch'}
if ((Get-FileHash -LiteralPath (Join-Path $old 'legacy_code.zip') -Algorithm SHA256).Hash.ToLowerInvariant() -ne $plan.code_sha256) {throw 'Code archive hash mismatch'}
foreach ($entry in $plan.moves.PSObject.Properties) {
    $src=Inside $entry.Name;$dst=Inside ([string]$entry.Value)
    if (Test-Path -LiteralPath $dst) {throw "Destination exists: $dst"}
    $resolved=(Get-Item -LiteralPath $src -Force).FullName
    if (-not $resolved.StartsWith($root+'\',[System.StringComparison]::OrdinalIgnoreCase)) {throw $resolved}
    New-Item -ItemType Directory -Path ([System.IO.Path]::GetDirectoryName($dst)) -Force | Out-Null
    Move-Item -LiteralPath $resolved -Destination $dst
    Write-Output "MOVED $($entry.Name)"
}
foreach ($relative in $plan.remove) {
    $target=Inside $relative
    if (-not (Test-Path -LiteralPath $target)) {continue}
    $item=Get-Item -LiteralPath $target -Force
    $resolved=$item.FullName
    if (-not $resolved.StartsWith($root+'\',[System.StringComparison]::OrdinalIgnoreCase)) {throw $resolved}
    if ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {throw "Unexpected link: $resolved"}
    if ($item.PSIsContainer -and $relative -notin @('02_learning/motion_control','02_learning/platform/vnc')) {throw "Unexpected directory: $resolved"}
    Write-Output "REMOVING $resolved"
    Remove-Item -LiteralPath $resolved -Recurse -Force
}
$recordSrc=Inside $plan.record_move.source;$recordDst=Inside $plan.record_move.target
if (Test-Path -LiteralPath $recordDst) {throw 'Record destination exists'}
$resolved=(Get-Item -LiteralPath $recordSrc -Force).FullName
if (-not $resolved.StartsWith($root+'\',[System.StringComparison]::OrdinalIgnoreCase)) {throw $resolved}
Move-Item -LiteralPath $resolved -Destination $recordDst
Write-Output 'Preserved raw audit records under 99_archive/records.'
