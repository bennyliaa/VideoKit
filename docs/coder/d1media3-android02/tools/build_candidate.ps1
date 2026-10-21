param()
$ErrorActionPreference='Stop'
$candidateRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
if(Test-Path -LiteralPath (Join-Path $candidateRoot 'evidence/media3-android02-freeze.json')){throw 'FROZEN'}
$buildEvidence=Join-Path $candidateRoot 'evidence/build-main-001'
if(Test-Path -LiteralPath $buildEvidence){throw 'ATTEMPT_EXISTS'}
New-Item -ItemType Directory -Path $buildEvidence | Out-Null
$env:JAVA_HOME='D:\Android\Android Studio\jbr'
$env:GRADLE_USER_HOME=Join-Path $candidateRoot 'build-tools-gradle-home'
$buildStart=[DateTimeOffset]::UtcNow.ToString('o')
Push-Location -LiteralPath $candidateRoot
try {
 & 'C:\Users\benny\.gradle\wrapper\dists\gradle-9.5.0-bin\bvnork1r7n8i6kp5cnkibsc9q\gradle-9.5.0\bin\gradle.bat' --offline --no-daemon --max-workers=2 --rerun-tasks --dependency-verification strict --init-script tools/consumption.init.gradle "-Drender02.operations=$buildEvidence/consumption.jsonl" :app:assembleDebug :app:assembleDebugAndroidTest *> (Join-Path $buildEvidence 'gradle.log')
 $buildExit=$LASTEXITCODE
 @{startUtc=$buildStart;endUtc=[DateTimeOffset]::UtcNow.ToString('o');exitCode=$buildExit;offline=$true;strictVerification=$true;verifyMetadata=$true;strictLockMode=$true;writeNewCandidateExactLocks=$false;tasks=@(':app:assembleDebug',':app:assembleDebugAndroidTest');deviceOperations=0;purpose='One concentrated Android02 app/test build; no install or media runtime'} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $buildEvidence 'receipt.json') -Encoding utf8
 Get-Content -LiteralPath (Join-Path $buildEvidence 'gradle.log') -Tail 22
 exit $buildExit
} finally {Pop-Location}
