param([Parameter(Mandatory=$true)][string]$RequestPath)
$ErrorActionPreference='Stop'
$batchRoot=Split-Path $PSScriptRoot -Parent
$request=Get-Content -LiteralPath $RequestPath -Raw | ConvertFrom-Json
foreach($inputPin in @($request.executionScope,$request.authority,$request.predecessorAudit)|Where-Object {$null -ne $_}){
 $inputFile=Join-Path 'D:/CodexProjects/VideoKit' $inputPin.path
 if((Get-FileHash -LiteralPath $inputFile -Algorithm SHA256).Hash.ToLower() -ne $inputPin.sha256){throw 'Immutable authority/scope pin changed'}
}
$intentPath=Join-Path $batchRoot ('evidence/'+$request.id+'-intent.json')
if(Test-Path -LiteralPath $intentPath){throw 'Original request already entered; no replay'}
$projectRoot='D:/CodexProjects/VideoKit/'
$scope=Get-Content -LiteralPath ($projectRoot+$request.executionScope.path) -Raw|ConvertFrom-Json
$operationRole=if($request.kind){$request.kind}else{'METADATA'}
$cap=65536;$charge=1;$nestedReservation=0;$metadataHash=$null
if($operationRole -eq 'METADATA'){
 $metadataPath=$projectRoot+'docs/coder/d1e13b/release/metadata/'+$request.metadataId+'.argv.json'
 $metadata=Get-Content -LiteralPath $metadataPath -Raw|ConvertFrom-Json
 $metadataHash=(Get-FileHash -LiteralPath $metadataPath -Algorithm SHA256).Hash.ToLower()
 if($metadataHash -ne $request.argvSha256){throw 'Exact argv pin mismatch'}
 $argv=@($metadata.argv)
 if($argv.Count -ne 7 -or $argv[0] -ne 'D:/Android/SDK/platform-tools/adb.exe' -or $argv[2] -ne 'HA1Q6WXR'){throw 'Exact direct metadata role required'}
}else{
 if(-not $request.predecessorAudit){throw 'Prior independent audit required'}
 $prior=Get-Content -LiteralPath ($projectRoot+$request.predecessorAudit.path) -Raw|ConvertFrom-Json
 if($prior.status -notlike 'PASS_*'){throw 'Prior stage not admitted'}
 foreach($productPin in @($scope.artifacts)+@($scope.config,$scope.release,$scope.runtimeScope)){
  if((Get-FileHash -LiteralPath ($projectRoot+$productPin.path) -Algorithm SHA256).Hash.ToLower() -ne $productPin.sha256){throw 'Reviewed dispatch input changed'}
 }
 $jarPath=$projectRoot+(@($scope.artifacts|Where-Object {-not $_.kind})[0].path)
 if($operationRole -eq 'DEPLOY'){
  if(Test-Path -LiteralPath $scope.oncePath){throw 'Deployment once already exists; no replay'}
  $argv=@('D:/Android/Android Studio/jbr/bin/java.exe','-cp',$jarPath,'com.videokit.spike.e4.E13HostActivationSession','--approved-e13-deploy',($projectRoot+$scope.config.path),$scope.config.sha256,($projectRoot+$scope.release.path),$scope.release.sha256)
  foreach($artifactKind in @('app','test','fixture')){$argv+=($projectRoot+(@($scope.artifacts|Where-Object kind -eq $artifactKind)[0].path))}
  $cap=32768;$charge=33;$nestedReservation=524288
 }elseif($operationRole -eq 'CASE'){
  if($request.method -notin $scope.methods){throw 'Exact method required'}
  $argv=@('D:/Android/Android Studio/jbr/bin/java.exe','-cp',$jarPath,'com.videokit.spike.e4.E13HostCase',($projectRoot+$scope.runtimeScope.path),$scope.runtimeScope.sha256,$request.method)
  $cap=81920;$charge=2;$nestedReservation=65536
 }else{throw 'Unapproved role'}
}
function WriteJson([string]$path,$value){[IO.File]::WriteAllText($path,($value|ConvertTo-Json -Depth 12),[Text.UTF8Encoding]::new($false))}
function Digest([byte[]]$raw){if($null -eq $raw){$raw=[byte[]]@()};[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($raw)).ToLower()}
$ledgerPath=Join-Path $batchRoot 'evidence/live-resource-ledger.json'
if(Test-Path -LiteralPath $ledgerPath){$liveLedger=Get-Content -LiteralPath $ledgerPath -Raw|ConvertFrom-Json}else{
 $liveLedger=[pscustomobject]@{scope=$scope.batchId;maxOriginalOperations=50;chargedOriginalOperations=0;maxTextBytes=2097152;originalTextBytes=0;hostReadOperations=0;startServerOperations=0;occupancyRetries=0;pcControlConnections=0;initialChargeExplanation='New independent E13C batch; no prior balance or ENV recovery inherited';events=@()}
}
if($liveLedger.chargedOriginalOperations+$charge -gt 50 -or $liveLedger.originalTextBytes+$cap+$nestedReservation -gt 2097152){throw 'Cumulative operation/text budget exhausted'}
$liveLedger.chargedOriginalOperations+=$charge
$liveLedger.events+=([pscustomobject]@{id=$request.id;role=$operationRole;charge=$charge;entered=$true;state='ENTERED_ORIGINAL';nestedTextReservation=$nestedReservation})
WriteJson $ledgerPath $liveLedger
$intent=[ordered]@{id=$request.id;atUtc=[DateTime]::UtcNow.ToString('o');argv=$argv;argvSha256=$metadataHash;executionScope=$request.executionScope;authoritySupplement=$request.authority;maxCombinedTextBytes=$cap;chargedOriginalAllocation=$charge;responseSeconds=55;toolHostPid=$PID;originalTargetCount=1;extraJavaPythonWrappers=0;noTerminateOrRetry=$true}
WriteJson $intentPath $intent
$original=[Diagnostics.Process]::new()
$info=[Diagnostics.ProcessStartInfo]::new()
$info.FileName=$argv[0];$info.UseShellExecute=$false;$info.CreateNoWindow=$true
$info.RedirectStandardInput=$true;$info.RedirectStandardOutput=$true;$info.RedirectStandardError=$true
for($argIndex=1;$argIndex -lt $argv.Count;$argIndex++){$info.ArgumentList.Add([string]$argv[$argIndex])}
$original.StartInfo=$info
$timer=[Diagnostics.Stopwatch]::StartNew()
if(-not $original.Start()){throw 'Original process start did not return true'}
$originalPid=$original.Id
$originalOut=$original.StandardOutput.BaseStream;$originalErr=$original.StandardError.BaseStream
$outMemory=[IO.MemoryStream]::new();$errMemory=[IO.MemoryStream]::new()
$outReader=$originalOut.CopyToAsync($outMemory);$errReader=$originalErr.CopyToAsync($errMemory)
$original.StandardInput.Close();$stdinReturned=$true;$pendingRecorded=$false
while(-not ($original.HasExited -and $outReader.IsCompleted -and $errReader.IsCompleted)){
 if($timer.Elapsed.TotalSeconds -ge 55 -and -not $pendingRecorded){
  WriteJson (Join-Path $batchRoot ('evidence/'+$request.id+'-pending.json')) ([ordered]@{state='PENDING_ORIGINAL_PROCESS_AND_READERS_RETAINED';pid=$originalPid;atUtc=[DateTime]::UtcNow.ToString('o');noKill=$true;noRetry=$true})
  $pendingRecorded=$true
 }
 Start-Sleep -Milliseconds 100
}
$original.WaitForExit();[void]$outReader.GetAwaiter().GetResult();[void]$errReader.GetAwaiter().GetResult()
$rawOut=$outMemory.ToArray();$rawErr=$errMemory.ToArray();$exitValue=$original.ExitCode
[IO.File]::WriteAllBytes((Join-Path $batchRoot ('evidence/'+$request.id+'-stdout.txt')),$rawOut)
[IO.File]::WriteAllBytes((Join-Path $batchRoot ('evidence/'+$request.id+'-stderr.txt')),$rawErr)
$originalOut.Close();$originalErr.Close();$original.Dispose()
$nestedTextActual=0;$nestedTextProven=$true
if($operationRole -eq 'DEPLOY'){
 $budgetMatch=[regex]::Match(([Text.Encoding]::UTF8.GetString($rawOut)+[Text.Encoding]::UTF8.GetString($rawErr)),'E13_DEPLOY_BUDGET operations=([0-9]+) textBytes=([0-9]+)')
 if($budgetMatch.Success){$nestedTextActual=[int]$budgetMatch.Groups[2].Value}else{$nestedTextActual=$nestedReservation;$nestedTextProven=$false}
}elseif($operationRole -eq 'CASE'){
 if($rawOut.Length -gt 0){$nestedTextActual=$rawOut.Length}else{$nestedTextActual=$nestedReservation;$nestedTextProven=$false}
}
$liveLedger.originalTextBytes+=($rawOut.Length+$rawErr.Length+$nestedTextActual)
$liveLedger.events[-1].state='ORIGINAL_RETURNED'
$receipt=[ordered]@{id=$request.id;atUtc=$intent.atUtc;endedAtUtc=[DateTime]::UtcNow.ToString('o');elapsedSeconds=$timer.Elapsed.TotalSeconds;pid=$originalPid;toolHostPid=$PID;exitCode=$exitValue;stdinClosed=$stdinReturned;originalWaitReturned=$true;stdoutReaderReturned=$true;stderrReaderReturned=$true;stdoutClosed=$true;stderrClosed=$true;originalProcessReturned=$true;bothOriginalPipesReturned=$true;stdoutBytes=$rawOut.Length;stderrBytes=$rawErr.Length;stdoutSha256=(Digest $rawOut);stderrSha256=(Digest $rawErr);responseTimedOut=$pendingRecorded;overflow=($rawOut.Length+$rawErr.Length -gt $cap);originalClientCount=1;extraJavaPythonWrappers=0;originalTargetDirect=$true;nestedTextCharged=$nestedTextActual;nestedTextAmountProven=$nestedTextProven;cumulativeOriginalAllocation=$liveLedger.chargedOriginalOperations;cumulativeOriginalTextBytes=$liveLedger.originalTextBytes}
WriteJson $ledgerPath $liveLedger
WriteJson (Join-Path $batchRoot ('evidence/'+$request.id+'-receipt.json')) $receipt
$receipt|ConvertTo-Json -Depth 6
