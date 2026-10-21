param([ValidatePattern('^[0-9]{3}$')][string]$Attempt='001')
$ErrorActionPreference='Stop'
$candidateRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
if(Test-Path -LiteralPath (Join-Path $candidateRoot 'evidence/media3-android01-freeze.json')){throw 'FROZEN'}
$evidence=Join-Path $candidateRoot ('evidence/build-main-'+$Attempt)
if(Test-Path -LiteralPath $evidence){throw 'ATTEMPT_EXISTS'}
New-Item -ItemType Directory -Path $evidence | Out-Null
$env:JAVA_HOME='D:\Android\Android Studio\jbr'
$env:GRADLE_USER_HOME=Join-Path $candidateRoot 'build-tools-gradle-home'
$start=[DateTimeOffset]::UtcNow.ToString('o')
Push-Location -LiteralPath $candidateRoot
try {
 & 'C:\Users\benny\.gradle\wrapper\dists\gradle-9.5.0-bin\bvnork1r7n8i6kp5cnkibsc9q\gradle-9.5.0\bin\gradle.bat' --offline --no-daemon --rerun-tasks --dependency-verification strict --init-script tools/consumption.init.gradle "-Drender02.operations=$evidence/consumption.jsonl" :app:assembleDebug :app:assembleDebugAndroidTest *> (Join-Path $evidence 'gradle.log')
 $code=$LASTEXITCODE
 @{startUtc=$start;endUtc=[DateTimeOffset]::UtcNow.ToString('o');exitCode=$code;offline=$true;strictVerification=$true;verifyMetadata=$true;strictLockMode=$true;writeNewCandidateExactLocks=$false;tasks=@(':app:assembleDebug',':app:assembleDebugAndroidTest');deviceSdkFieldOperations=0;purpose='Exact empty app/test compile and packaging only; no installation'} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $evidence 'receipt.json') -Encoding utf8
 Get-Content -LiteralPath (Join-Path $evidence 'gradle.log') -Tail 30
 exit $code
} finally {Pop-Location}
