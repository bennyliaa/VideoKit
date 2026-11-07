# 14 §9.3 package size: engine vs embedded release builds of sample-host, per ABI APK and AAB download size.
# Usage: powershell -File sample-host/measure/measure_size.ps1 [-SkipBuild]
# Needs the Flutter module AAR (build_embed_aar.ps1). Optional: $env:BUNDLETOOL_JAR for AAB download sizes.
param([switch] $SkipBuild)
. (Join-Path $PSScriptRoot 'common.ps1')

if (-not $SkipBuild) {
    Invoke-Gradle @(':sample-host:assembleEngineRelease', ':sample-host:assembleEmbeddedRelease',
        ':sample-host:bundleEngineRelease', ':sample-host:bundleEmbeddedRelease')
}

$outputs = Join-Path $script:Repo 'sample-host\build\outputs'
$abis = @('arm64-v8a', 'armeabi-v7a', 'x86_64')
$rows = @()
foreach ($abi in $abis) {
    $sizes = @{}
    foreach ($flavor in @('engine', 'embedded')) {
        $apk = Get-ChildItem (Join-Path $outputs "apk\$flavor\release") -Filter "*-$abi-release*.apk" | Select-Object -First 1
        $sizes[$flavor] = if ($apk) { $apk.Length } else { $null }
    }
    $delta = if ($sizes['engine'] -and $sizes['embedded']) { $sizes['embedded'] - $sizes['engine'] } else { $null }
    $rows += [pscustomobject]@{ artifact = "apk-$abi"; engine = $sizes['engine']; embedded = $sizes['embedded']; delta = $delta }
}

# AAB download size (bundletool get-size total: MIN/MAX bytes over the device specs).
$bundletool = $env:BUNDLETOOL_JAR
$aab = @{}
foreach ($flavor in @('engine', 'embedded')) {
    $bundle = Get-ChildItem (Join-Path $outputs "bundle\${flavor}Release") -Filter '*.aab' | Select-Object -First 1
    if ($bundletool -and $bundle) {
        $apks = Join-Path $script:Results "$flavor.apks"
        java -jar $bundletool build-apks --bundle $bundle.FullName --output $apks --overwrite | Out-Null
        $total = java -jar $bundletool get-size total --apks $apks
        # Output: "MIN,MAX" header then values.
        $aab[$flavor] = ($total | Select-Object -Last 1)
    } else {
        $aab[$flavor] = 'NOT_RUN'
    }
}
$rows += [pscustomobject]@{ artifact = 'aab-download(min,max)'; engine = $aab['engine']; embedded = $aab['embedded']; delta = '' }

$csv = Join-Path $script:Results 'size.csv'
$rows | Export-Csv -NoTypeInformation -Encoding UTF8 $csv
$rows | Format-Table -AutoSize
Write-Output "Written: $csv"
