[CmdletBinding()]
param(
    [switch]$Build,
    [switch]$Repair,
    [switch]$RepairSourceFix,
    [string]$RepairReason = '',
    [ValidatePattern('^[a-z][a-z0-9-]{0,47}$')][string]$Attempt = 'main-001',
    [string]$ProjectRoot = '',
    [string]$JavaHome = 'D:\Android\Android Studio\jbr'
)
$ErrorActionPreference = 'Stop'
if (-not $ProjectRoot) { $ProjectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..\..\..')) }
$ProjectRoot = [IO.Path]::GetFullPath($ProjectRoot)
$candidateRoot = Join-Path $ProjectRoot 'docs\coder\d1e5c'
$evidenceRoot = Join-Path $candidateRoot 'evidence'
$mainGate = Join-Path $evidenceRoot 'build-main-reservation.json'
$finalResult = Join-Path $evidenceRoot 'build-results.json'
$attemptRoot = Join-Path (Join-Path $evidenceRoot 'build-attempts') $Attempt
$arguments = @('--offline', '--no-daemon', '--console=plain', ':app:assembleDebug', ':app:assembleDebugAndroidTest', ':app:dependencies', '--configuration', 'debugRuntimeClasspath', '--write-locks')
function Write-NewJson([string]$Path, $Value) {
    $parent = [IO.Path]::GetDirectoryName($Path)
    [IO.Directory]::CreateDirectory($parent) | Out-Null
    $data = [Text.UTF8Encoding]::new($false).GetBytes(($Value | ConvertTo-Json -Depth 20) + "`n")
    $stream = [IO.File]::Open($Path, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try { $stream.Write($data, 0, $data.Length); $stream.Flush($true) } finally { $stream.Dispose() }
}
if (Test-Path -LiteralPath (Join-Path $evidenceRoot 'e5c-freeze.json')) { throw 'E4_FROZEN_NO_BUILD_MUTATION' }
if (-not $Build) {
    [ordered]@{ schema=1; mode='INSPECT'; scope='E5C_LOCAL_GRADLE_ONLY'; offline=$true; arguments=$arguments; androidExecution='NOT_RUN'; nativeFaultExecution='NOT_RUN' } | ConvertTo-Json -Depth 8
    return
}
$inputFile = Join-Path $evidenceRoot 'final-build-inputs.json'
if (-not (Test-Path -LiteralPath $inputFile)) { throw 'E5_FINAL_BUILD_INPUT_SNAPSHOT_REQUIRED' }
$inputSnapshotHash = (Get-FileHash -LiteralPath $inputFile -Algorithm SHA256).Hash.ToLowerInvariant()
$inputSnapshot = Get-Content -LiteralPath $inputFile -Raw | ConvertFrom-Json
foreach ($inputRow in $inputSnapshot.files) {
    $inputPath = Join-Path $ProjectRoot $inputRow.path
    if ((Get-Item -LiteralPath $inputPath).Length -ne $inputRow.bytes -or (Get-FileHash -LiteralPath $inputPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $inputRow.sha256) { throw 'E5_FINAL_BUILD_INPUT_CHANGED' }
}
if (Test-Path -LiteralPath $finalResult) {
    if (-not $Repair -or -not $RepairSourceFix -or -not $RepairReason) { throw 'E4_FINAL_BUILD_EXISTS_NO_DUPLICATE_PASSING_BUILD' }
    $previousFinal = Get-Content -LiteralPath $finalResult -Raw | ConvertFrom-Json
    $previousPassing = @($previousFinal.attempts | Where-Object { $_.exitCode -eq 0 })[-1]
    if (-not $previousPassing.inputSnapshotSha256 -or $previousPassing.inputSnapshotSha256 -eq $inputSnapshotHash) { throw 'E5_SOURCE_FIX_REQUIRES_CHANGED_FINAL_INPUTS_NOT_IDENTICAL_REBUILD' }
    $preservedResult = [IO.Path]::GetFullPath((Join-Path $evidenceRoot ('build-results-before-' + $Attempt + '.json')))
    if (-not $preservedResult.StartsWith([IO.Path]::GetFullPath($evidenceRoot) + [IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase) -or (Test-Path -LiteralPath $preservedResult)) { throw 'E4_PRESERVED_RESULT_PATH_INVALID' }
    [IO.File]::Move($finalResult,$preservedResult)
}
if (Test-Path -LiteralPath $attemptRoot) { throw 'E4_BUILD_ATTEMPT_CONSUMED' }
if (-not $Repair) {
    if (Test-Path -LiteralPath $mainGate) { throw 'E4_MAIN_BUILD_ALREADY_RESERVED_REPAIRS_REQUIRE_REPAIR_FLAG' }
    Write-NewJson $mainGate ([ordered]@{schema=1; attempt=$Attempt; state='RESERVED'; scope='E5C_LOCAL_GRADLE_ONLY'})
} else {
    if (-not (Test-Path -LiteralPath $mainGate)) { throw 'E4_REPAIR_REQUIRES_PRESERVED_MAIN_ATTEMPT' }
    $priorResults = @(Get-ChildItem -LiteralPath (Join-Path $evidenceRoot 'build-attempts') -Filter 'attempt-result.json' -Recurse -File)
    if ($priorResults.Count -eq 0) { throw 'E4_REPAIR_REQUIRES_FAILED_ATTEMPT' }
    foreach ($resultFile in $priorResults) {
        $previous = Get-Content -LiteralPath $resultFile.FullName -Raw | ConvertFrom-Json
        if ($previous.exitCode -eq 0 -and -not $RepairSourceFix) { throw 'E4_REPAIR_AFTER_SUCCESS_FORBIDDEN' }
    }
}
[IO.Directory]::CreateDirectory($attemptRoot) | Out-Null
$wrapper = Join-Path $candidateRoot 'gradlew.bat'
$javaExecutable = Join-Path $JavaHome 'bin\java.exe'
if (-not (Test-Path -LiteralPath $wrapper) -or -not (Test-Path -LiteralPath $javaExecutable)) { throw 'E4_EXISTING_GRADLE_OR_JDK_UNAVAILABLE_NO_DOWNLOAD' }
$log = Join-Path $attemptRoot 'gradle.log'
if (Test-Path -LiteralPath $log) { throw 'E4_BUILD_LOG_ALREADY_EXISTS' }
$savedJavaHome = $env:JAVA_HOME
$started = [DateTime]::UtcNow.ToString('o')
$exitValue = -1
try {
    $env:JAVA_HOME = $JavaHome
    Push-Location -LiteralPath $candidateRoot
    try {
        & $wrapper @arguments 2>&1 | Out-File -LiteralPath $log -Encoding utf8
        $exitValue = $LASTEXITCODE
    } finally { Pop-Location }
} catch {
    if (-not (Test-Path -LiteralPath $log)) { [IO.File]::WriteAllText($log, $_.Exception.GetType().Name, [Text.UTF8Encoding]::new($false)) }
} finally { $env:JAVA_HOME = $savedJavaHome }
$relativeLog = [IO.Path]::GetRelativePath($ProjectRoot, $log).Replace('\','/')
$result = [ordered]@{
    schema=1; inputSnapshotSha256=$inputSnapshotHash; id=$Attempt; kind=$(if($Repair){'REPAIR'}else{'MAIN'}); exitCode=$exitValue;
    offline=$true; arguments=$arguments; log=$relativeLog; beganUtc=$started; endedUtc=[DateTime]::UtcNow.ToString('o');
    sourceFixAfterCompile=$RepairSourceFix.IsPresent; repairReason=$RepairReason;
    androidExecution='NOT_RUN'; nativeFaultExecution='NOT_RUN'
}
Write-NewJson (Join-Path $attemptRoot 'attempt-result.json') $result
if ($exitValue -eq 0) {
    $allAttempts = @(Get-ChildItem -LiteralPath (Join-Path $evidenceRoot 'build-attempts') -Filter 'attempt-result.json' -Recurse -File | ForEach-Object { Get-Content -LiteralPath $_.FullName -Raw | ConvertFrom-Json } | Sort-Object beganUtc)
    Write-NewJson $finalResult ([ordered]@{schema=1;status='PASS';offline=$true;scope='E5C_LOCAL_GRADLE_ONLY';attempts=$allAttempts;androidExecution='NOT_RUN';nativeFaultExecution='NOT_RUN'})
}
$result | ConvertTo-Json -Depth 10
if ($exitValue -ne 0) { exit 1 }
