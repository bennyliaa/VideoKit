# 14 §9.3 first frame of the embedded player: cold start, prewarmed vs not, N runs each; median and P90.
# Usage: powershell -File sample-host/measure/measure_first_frame.ps1 [-Runs 20] [-SkipInstall]
# M0: debug build (the Kotlin Fake is debug-only); see README "Limits in M0".
param([int] $Runs = 20, [switch] $SkipInstall)
. (Join-Path $PSScriptRoot 'common.ps1')

$package = 'com.videokit.samplehost'
if (-not $SkipInstall) {
    Invoke-Gradle @(':sample-host:assembleEmbeddedDebug')
    $apk = Get-ChildItem (Join-Path $script:Repo 'sample-host\build\outputs\apk\embedded\debug') -Filter '*arm64-v8a*.apk' | Select-Object -First 1
    adb install -r $apk.FullName
    if ($LASTEXITCODE -ne 0) { throw 'adb install failed' }
}

$rows = @()
foreach ($prewarm in @('true', 'false')) {
    $values = @()
    for ($i = 1; $i -le $Runs; $i++) {
        adb shell am force-stop $package | Out-Null
        adb logcat -c
        adb shell am start -n "$package/.MainActivity" --ez prewarm $prewarm --es open embed --el openDelayMs 3000 | Out-Null
        $metric = Wait-Metric 'first_frame' 60
        $ms = if ($metric) { [double]$metric['ms'] } else { [double]::NaN }
        $values += $ms
        $rows += [pscustomobject]@{ prewarm = $prewarm; run = $i; ms = $ms; prewarmedEngine = $metric.prewarmed }
        Write-Output "prewarm=$prewarm run=$i first_frame_ms=$ms"
    }
    $valid = $values | Where-Object { -not [double]::IsNaN($_) }
    $rows += [pscustomobject]@{ prewarm = $prewarm; run = 'median'; ms = (Get-Median $valid); prewarmedEngine = '' }
    $rows += [pscustomobject]@{ prewarm = $prewarm; run = 'p90'; ms = (Get-Percentile $valid 90); prewarmedEngine = '' }
}
adb shell am force-stop $package | Out-Null

$csv = Join-Path $script:Results 'first_frame.csv'
$rows | Export-Csv -NoTypeInformation -Encoding UTF8 $csv
$rows | Where-Object { $_.run -in @('median', 'p90') } | Format-Table -AutoSize
Write-Output "Written: $csv"
