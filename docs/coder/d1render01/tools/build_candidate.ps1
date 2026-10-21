param([ValidatePattern('^[0-9]{3}$')][string]$Attempt = '001')
$ErrorActionPreference = 'Stop'
$candidateRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$buildEvidence = Join-Path $candidateRoot ('evidence/build-main-' + $Attempt)
if (Test-Path -LiteralPath $buildEvidence) { throw 'BUILD_ATTEMPT_EXISTS_DO_NOT_OVERWRITE' }
New-Item -ItemType Directory -Path $buildEvidence | Out-Null
$env:JAVA_HOME = 'D:\Android\Android Studio\jbr'
$start = [DateTimeOffset]::UtcNow.ToString('o')
Push-Location -LiteralPath $candidateRoot
try {
    & .\gradlew.bat --offline --no-daemon --dependency-verification strict :app:assembleDebug :app:assembleDebugAndroidTest *> (Join-Path $buildEvidence 'gradle.log')
    $buildExit = $LASTEXITCODE
    @{startUtc=$start; endUtc=[DateTimeOffset]::UtcNow.ToString('o'); exitCode=$buildExit; deviceOperations=0; tasks=@(':app:assembleDebug',':app:assembleDebugAndroidTest'); offline=$true} |
        ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $buildEvidence 'receipt.json') -Encoding utf8
    Get-Content -LiteralPath (Join-Path $buildEvidence 'gradle.log') -Tail 22
    exit $buildExit
} finally { Pop-Location }
