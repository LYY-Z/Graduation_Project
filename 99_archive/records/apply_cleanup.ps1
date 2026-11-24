$ErrorActionPreference = 'Stop'
$cleanupRoot = (Get-Item -LiteralPath 'G:\毕设').FullName.TrimEnd('\')
$auditRoot = Join-Path $cleanupRoot '99_archive\workspace_cleanup_20261123'
$plan = Get-Content -LiteralPath (Join-Path $auditRoot 'plan.json') -Raw | ConvertFrom-Json
if (-not $plan.archive_verified) { throw 'Verified archives required.' }
$protected = @('03_code\diffusion_policy_ur7e', '03_code\diffusion_policy', '03_code\references', '03_code\locoformer')

function Workspace-Path([string]$relative) {
    $full = [System.IO.Path]::GetFullPath((Join-Path $cleanupRoot $relative))
    if (-not $full.StartsWith($cleanupRoot + '\', [System.StringComparison]::OrdinalIgnoreCase)) { throw "Outside workspace: $full" }
    return $full
}
function Assert-Removable([string]$full) {
    foreach ($relative in $protected) {
        $active = Workspace-Path $relative
        if ($full -eq $active -or $full.StartsWith($active + '\', [System.StringComparison]::OrdinalIgnoreCase)) { throw "Protected project: $full" }
    }
    if ($full -eq $auditRoot -or $full.StartsWith($auditRoot + '\', [System.StringComparison]::OrdinalIgnoreCase)) { throw 'Audit directory is protected.' }
}

foreach ($entry in $plan.archives.PSObject.Properties) {
    $archive = Join-Path $auditRoot $entry.Name
    $actual = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $entry.Value.sha256) { throw "Archive changed: $archive" }
}

$events = [System.Collections.Generic.List[object]]::new()
foreach ($entry in $plan.moves.PSObject.Properties) {
    $source = Workspace-Path $entry.Name
    $target = Workspace-Path ([string]$entry.Value)
    if (-not (Test-Path -LiteralPath $source) -and (Test-Path -LiteralPath $target)) { continue }
    if (-not (Test-Path -LiteralPath $source)) { throw "Source missing: $source" }
    if (Test-Path -LiteralPath $target) { throw "Destination already exists: $target" }
    $resolved = (Get-Item -LiteralPath $source -Force).FullName
    if (-not $resolved.StartsWith($cleanupRoot + '\', [System.StringComparison]::OrdinalIgnoreCase)) { throw "Invalid move source: $resolved" }
    New-Item -ItemType Directory -Path ([System.IO.Path]::GetDirectoryName($target)) -Force | Out-Null
    Move-Item -LiteralPath $resolved -Destination $target
    $events.Add([pscustomobject]@{action='move';source=$entry.Name;destination=$entry.Value})
    Write-Output "MOVED $($entry.Name)"
}

# Remove build-directory junctions themselves, never their shared runtime targets.
foreach ($relative in $plan.skipped_reparse) {
    $full = Workspace-Path $relative
    if (Test-Path -LiteralPath $full) {
        Assert-Removable $full
        $item = Get-Item -LiteralPath $full -Force
        if (-not ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) { throw "Expected junction: $full" }
        [System.IO.Directory]::Delete($full)
        $events.Add([pscustomobject]@{action='unlink-junction';source=$relative})
    }
}

foreach ($relative in $plan.delete_targets) {
    $full = Workspace-Path $relative
    Assert-Removable $full
    if (-not (Test-Path -LiteralPath $full)) { continue }
    $item = Get-Item -LiteralPath $full -Force
    $resolved = $item.FullName
    if (-not $resolved.StartsWith($cleanupRoot + '\', [System.StringComparison]::OrdinalIgnoreCase)) { throw "Invalid removal: $resolved" }
    if ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) { throw "Unexpected reparse root: $resolved" }
    Write-Output "REMOVING $resolved"
    Remove-Item -LiteralPath $resolved -Recurse -Force
    $events.Add([pscustomobject]@{action='remove';source=$relative})
    $events | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $auditRoot 'operations.json') -Encoding utf8
}
Write-Output 'Filesystem moves and verified cleanup completed.'
