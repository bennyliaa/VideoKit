param([string]$Attempt='002')
$ErrorActionPreference='Stop'
$candidateRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$env:JAVA_HOME='D:\Android\Android Studio\jbr'
$env:GRADLE_USER_HOME=Join-Path $candidateRoot 'evidence/build-main-003/fresh-gradle-home'
foreach($probeName in @('positive','negative')){
 $probeRoot=Join-Path $candidateRoot ('evidence/metadata-rejection-'+$Attempt+'/'+$probeName)
 Push-Location -LiteralPath $probeRoot
 try {
  $start=[DateTimeOffset]::UtcNow.ToString('o')
  & 'C:\Users\benny\.gradle\wrapper\dists\gradle-9.5.0-bin\bvnork1r7n8i6kp5cnkibsc9q\gradle-9.5.0\bin\gradle.bat' --offline --no-daemon --dependency-verification strict resolveProbe *> (Join-Path $probeRoot 'gradle.log')
  $probeExit=$LASTEXITCODE
  @{name=$probeName;startUtc=$start;endUtc=[DateTimeOffset]::UtcNow.ToString('o');exitCode=$probeExit;deviceOperations=0;offline=$true;metadataVerification=$true} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $probeRoot 'receipt.json') -Encoding utf8
  Get-Content -LiteralPath (Join-Path $probeRoot 'gradle.log') -Tail 18
 }finally{Pop-Location}
}
