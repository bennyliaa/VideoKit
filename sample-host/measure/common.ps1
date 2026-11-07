# Shared helpers of the 14 §9.3 measurement scripts (dot-sourced).
$ErrorActionPreference = 'Stop'
$script:Repo = Resolve-Path (Join-Path $PSScriptRoot '..\..')
$script:Results = Join-Path $PSScriptRoot 'results'
New-Item -ItemType Directory -Force $script:Results | Out-Null

function Invoke-Gradle([string[]] $Tasks) {
    Push-Location $script:Repo
    try {
        & .\gradlew.bat '-Pvideokit.embedAar=true' @Tasks --console=plain
        if ($LASTEXITCODE -ne 0) { throw "gradlew $Tasks failed" }
    } finally {
        Pop-Location
        # The development machine is short on memory: never leave a daemon behind.
        Push-Location $script:Repo; & .\gradlew.bat --stop | Out-Null; Pop-Location
    }
}

# Waits for a VideoKitMetrics logcat line starting with $Event; returns the parsed key=value map or $null on timeout.
function Wait-Metric([string] $Event, [int] $TimeoutSeconds = 60) {
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        $lines = adb logcat -d -s 'VideoKitMetrics:I' 2>$null
        foreach ($line in $lines) {
            $at = $line.IndexOf("VideoKitMetrics: $Event")
            if ($at -ge 0) {
                $fields = @{}
                foreach ($pair in ($line.Substring($at + "VideoKitMetrics: $Event".Length).Trim() -split ' ')) {
                    $kv = $pair -split '=', 2
                    if ($kv.Count -eq 2) { $fields[$kv[0]] = $kv[1] }
                }
                return $fields
            }
        }
        Start-Sleep -Milliseconds 250
    }
    return $null
}

function Get-Median([double[]] $Values) {
    $sorted = $Values | Sort-Object
    $n = $sorted.Count
    if ($n -eq 0) { return [double]::NaN }
    if ($n % 2 -eq 1) { return $sorted[[int][math]::Floor($n / 2)] }
    return ($sorted[$n / 2 - 1] + $sorted[$n / 2]) / 2
}

# Nearest-rank percentile.
function Get-Percentile([double[]] $Values, [double] $P) {
    $sorted = $Values | Sort-Object
    if ($sorted.Count -eq 0) { return [double]::NaN }
    $rank = [int][math]::Ceiling($P / 100 * $sorted.Count)
    return $sorted[[math]::Max(0, $rank - 1)]
}
