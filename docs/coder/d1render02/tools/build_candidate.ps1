param([ValidatePattern('^[0-9]{3}$')][string]$Attempt='001',[string]$ReuseHome='')
$ErrorActionPreference='Stop'
$candidateRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
if(Test-Path -LiteralPath (Join-Path $candidateRoot 'evidence/render02-freeze.json')){throw 'FROZEN'}
$buildEvidence=Join-Path $candidateRoot ('evidence/build-main-'+$Attempt)
if(Test-Path -LiteralPath $buildEvidence){throw 'ATTEMPT_EXISTS'}
New-Item -ItemType Directory -Path $buildEvidence | Out-Null
$env:JAVA_HOME='D:\Android\Android Studio\jbr'
$env:GRADLE_USER_HOME=Join-Path $buildEvidence 'fresh-gradle-home'
if($ReuseHome){$env:GRADLE_USER_HOME=[IO.Path]::GetFullPath((Join-Path $candidateRoot ('evidence/build-main-'+$ReuseHome+'/fresh-gradle-home')))}
$start=[DateTimeOffset]::UtcNow.ToString('o')
Push-Location -LiteralPath $candidateRoot
try {
 & 'C:\Users\benny\.gradle\wrapper\dists\gradle-9.5.0-bin\bvnork1r7n8i6kp5cnkibsc9q\gradle-9.5.0\bin\gradle.bat' --offline --no-daemon --dependency-verification strict --init-script tools/consumption.init.gradle "-Drender02.operations=$buildEvidence/consumption.jsonl" :app:assembleDebug :app:assembleDebugAndroidTest *> (Join-Path $buildEvidence 'gradle.log')
 $buildExit=$LASTEXITCODE
 @{startUtc=$start;endUtc=[DateTimeOffset]::UtcNow.ToString('o');exitCode=$buildExit;deviceOperations=0;offline=$true;metadataVerification=$true;freshUserHome=$env:GRADLE_USER_HOME;tasks=@(':app:assembleDebug',':app:assembleDebugAndroidTest')} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $buildEvidence 'receipt.json') -Encoding utf8
 Get-Content -LiteralPath (Join-Path $buildEvidence 'gradle.log') -Tail 25
 exit $buildExit
} finally {Pop-Location}
