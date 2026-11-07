# 14 §9.3 multi-instance memory: four embed engines (2×2) vs one engine with four sessions; TOTAL PSS median.
# Usage: powershell -File sample-host/measure/measure_memory.ps1 [-Runs 5] [-SkipInstall]
# M0: debug build (the Kotlin Fake is debug-only); see README "Limits in M0".
param([int] $Runs = 5, [switch] $SkipInstall)
. (Join-Path $PSScriptRoot 'common.ps1')

$package = 'com.videokit.samplehost'
if (-not $SkipInstall) {
    Invoke-Gradle @(':sample-host:assembleEmbeddedDebug')
    $apk = Get-ChildItem (Join-Path $script:Repo 'sample-host\build\outputs\apk\embedded\debug') -Filter '*arm64-v8a*.apk' | Select-Object -First 1
    adb install -r $apk.FullName
    if ($LASTEXITCODE -ne 0) { throw 'adb install failed' }
}

function Get-TotalPssKb([string] $Package) {
    $info = adb shell dumpsys meminfo $Package
    # "TOTAL PSS:   123456   TOTAL RSS: ..." (newer) or "TOTAL   123456 ..." (older) — first number after TOTAL.
    foreach ($line in $info) {
        if ($line -match '^\s*TOTAL(?: PSS:)?\s+(\d+)') { return [double]$Matches[1] }
    }
    return [double]::NaN
}

$rows = @()
foreach ($mode in @('multiview4', 'multiview1')) {
    $values = @()
    for ($i = 1; $i -le $Runs; $i++) {
        adb shell am force-stop $package | Out-Null
        adb logcat -c
        adb shell am start -n "$package/.MainActivity" --ez prewarm false --es open $mode | Out-Null
        $ready = Wait-Metric 'multiview_ready' 90
        Start-Sleep -Seconds 5
        $pss = if ($ready) { Get-TotalPssKb $package } else { [double]::NaN }
        $values += $pss
        $rows += [pscustomobject]@{ mode = $mode; run = $i; totalPssKb = $pss; engines = $ready.engines }
        Write-Output "mode=$mode run=$i total_pss_kb=$pss engines=$($ready.engines)"
    }
    $valid = $values | Where-Object { -not [double]::IsNaN($_) }
    $rows += [pscustomobject]@{ mode = $mode; run = 'median'; totalPssKb = (Get-Median $valid); engines = '' }
}
adb shell am force-stop $package | Out-Null

$csv = Join-Path $script:Results 'memory.csv'
$rows | Export-Csv -NoTypeInformation -Encoding UTF8 $csv
$rows | Where-Object { $_.run -eq 'median' } | Format-Table -AutoSize
Write-Output "Written: $csv"
