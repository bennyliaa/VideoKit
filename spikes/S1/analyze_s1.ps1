# S1 analysis: P50 / P90 per file, condition and read-ahead size from s1_results.jsonl (15 §4 item 7 uses P90).
# Usage: powershell -File spikes/S1/analyze_s1.ps1 <s1_results.jsonl>
param([Parameter(Mandatory = $true)][string]$Results)

function Pct([double[]]$values, [double]$p) {
    if ($values.Count -eq 0) { return $null }
    $sorted = $values | Sort-Object
    # Nearest-rank percentile.
    $rank = [math]::Ceiling($p / 100.0 * $sorted.Count) - 1
    return $sorted[[math]::Max(0, [math]::Min($rank, $sorted.Count - 1))]
}

$rows = Get-Content $Results | Where-Object { $_.Trim() } | ForEach-Object { $_ | ConvertFrom-Json }
$runs = $rows | Where-Object { $_.event -eq 'playback' }
$errors = $rows | Where-Object { $_.event -eq 'error' }
"runs: $($runs.Count)  errors: $($errors.Count)"

$groups = $runs | Group-Object { "$($_.file)|$($_.condition)|$($_.prefetch)" }
foreach ($g in $groups) {
    $r = $g.Group
    $ok = $r | Where-Object { $_.bind -eq 'Executed' }
    $first = [double[]]($ok | Where-Object { $_.bindToFirstFrameMs -ge 0 } | ForEach-Object { $_.bindToFirstFrameMs })
    $bind = [double[]]($ok | ForEach-Object { $_.bindMs })
    $sync = [double[]]($ok | ForEach-Object { $_.seeks } | Where-Object { $_.mode -eq 'CLOSEST_SYNC' } | ForEach-Object { $_.seekMs })
    $exact = [double[]]($ok | ForEach-Object { $_.seeks } | Where-Object { $_.mode -eq 'EXACT' } | ForEach-Object { $_.seekMs })
    $cancel = [double[]]($r | ForEach-Object { $_.cancel.releaseMs })
    $block = [double[]]($r | ForEach-Object { $_.mainMaxBlockMs })
    $over16 = ($r | Measure-Object -Property mainBlocksOver16ms -Sum).Sum
    $handles = ($r | Measure-Object -Property handlesAfterRelease -Sum).Sum
    $cancelHandles = ($r | ForEach-Object { $_.cancel.openHandles } | Measure-Object -Sum).Sum
    $rebuffers = ($r | Measure-Object -Property rebuffers -Sum).Sum
    $pss = ($r | Measure-Object -Property pssKbPeak -Maximum).Maximum
    [pscustomobject]@{
        key               = $g.Name
        runs              = $r.Count
        bindOk            = $ok.Count
        bindP50           = Pct $bind 50
        bindP90           = Pct $bind 90
        firstFrameP50     = Pct $first 50
        firstFrameP90     = Pct $first 90
        syncSeekP50       = Pct $sync 50
        syncSeekP90       = Pct $sync 90
        exactSeekP50      = Pct $exact 50
        exactSeekP90      = Pct $exact 90
        cancelP90         = Pct $cancel 90
        cancelMax         = ($cancel | Measure-Object -Maximum).Maximum
        mainBlockMax      = ($block | Measure-Object -Maximum).Maximum
        mainBlocksOver16  = $over16
        handlesAfter      = $handles
        cancelOpenHandles = $cancelHandles
        rebuffers         = $rebuffers
        pssPeakKb         = $pss
    }
}
"thumbnails:"
$rows | Where-Object { $_.event -eq 'thumbnail' } | ForEach-Object { "  $($_.file) $($_.condition): $($_.ms) ms ok=$($_.ok) handles=$($_.openHandles)" }
