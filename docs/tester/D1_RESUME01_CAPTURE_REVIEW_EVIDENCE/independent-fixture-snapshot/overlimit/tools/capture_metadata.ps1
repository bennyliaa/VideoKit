param([Parameter(Mandatory=$true)][string]$RequestPath,[string]$PredecessorProofSha='ABSENT',[string]$DeploymentProofSha='ABSENT')
$ErrorActionPreference='Stop'
# Narrow derivative of the reviewed observer: one original foreground controller, no kill/detach/second reader.
function ReadJsonExact([string]$Path,[string[]]$Keys,[int]$Max=8192){
 $raw=[IO.File]::ReadAllBytes($Path);if($raw.Length -gt $Max){throw 'JSON_BOUND'}
 $doc=[Text.Json.JsonDocument]::Parse([Text.Encoding]::UTF8.GetString($raw));$seen=[Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
 try{foreach($property in $doc.RootElement.EnumerateObject()){if(-not $seen.Add($property.Name)){throw 'DUPLICATE_JSON_FIELD'}}}finally{$doc.Dispose()}
 $o=[Text.Encoding]::UTF8.GetString($raw)|ConvertFrom-Json
 if($Keys.Count -gt 0 -and (@(Compare-Object -CaseSensitive @($o.PSObject.Properties.Name|Sort-Object) @($Keys|Sort-Object)).Count -ne 0)){throw 'EXACT_SCHEMA_REQUIRED'}
 return $o
}
function Digest([string]$Path){return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()}
function SameArgv($A,$B){if($A.Count -ne $B.Count){return $false};for($n=0;$n -lt $A.Count;$n++){if($A[$n] -isnot [string] -or $A[$n] -cne $B[$n]){return $false}};return $true}
function NoLinks([string]$Path){for($p=[IO.DirectoryInfo]::new($Path);$null -ne $p;$p=$p.Parent){if($p.Exists -and ($p.Attributes -band [IO.FileAttributes]::ReparsePoint)){throw 'NO_REPARSE_POINT'}}}
$policyPath=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../release/capture-policy.json'))
$request=ReadJsonExact $RequestPath @('schema','id','policySha256','scope','evidenceRoot','argv','maxTextBytes','qualificationSeconds')
foreach($key in @('schema','id','policySha256','scope','evidenceRoot')){if($request.$key -isnot [string]){throw 'EXACT_REQUEST_VALUE_TYPES'}}
if($request.argv -isnot [array] -or ($request.maxTextBytes -isnot [long] -and $request.maxTextBytes -isnot [int]) -or ($request.qualificationSeconds -isnot [long] -and $request.qualificationSeconds -isnot [int] -and $request.qualificationSeconds -isnot [double]) -or [double]::IsNaN([double]$request.qualificationSeconds) -or [double]::IsInfinity([double]$request.qualificationSeconds)){throw 'EXACT_REQUEST_VALUE_TYPES'}
if($request.schema -cne 'RESUME01_CAPTURE_REQUEST_V1' -or $request.policySha256 -cne (Digest $policyPath)){throw 'REQUEST_POLICY_PIN'}
$policy=ReadJsonExact $policyPath @() 65536
if($policy.schema -cne 'RESUME01_CAPTURE_POLICY_V1' -or $policy.entrySha256 -cne (Digest $PSCommandPath)){throw 'ENTRY_POLICY_PIN'}
if($policy.mode -ceq 'PREPARATION_ONLY'){throw 'PREPARATION_ONLY_NO_EXECUTION_AUTHORIZATION'}
if($policy.mode -cnotin @('PRODUCTION','OFFLINE_FIXTURE')){throw 'EXACT_POLICY_MODE'}
$root=[IO.Path]::GetFullPath([string]$policy.evidenceRoot);NoLinks $root
if($request.evidenceRoot -cne $policy.evidenceRoot -or $request.scope -cne $policy.scope -or $policy.scope -cnotmatch '^[a-f0-9]{64}$'){throw 'EXACT_SCOPE_ROOT'}
$slots=@($policy.slots);$index=-1
for($i=0;$i -lt $slots.Count;$i++){if($slots[$i].id -ceq $request.id){if($index -ne -1){throw 'DUPLICATE_SLOT'};$index=$i}}
if($index -lt 0 -or $request.id -cnotmatch '^[A-Za-z0-9_]{1,80}$'){throw 'EXACT_REQUEST_SLOT'}
$slot=$slots[$index]
if(-not (SameArgv @($request.argv) @($slot.argv)) -or $request.maxTextBytes -ne $slot.maxTextBytes -or $request.qualificationSeconds -ne $slot.qualificationSeconds){throw 'EXACT_ARGV_CAP_QUALIFIER'}
if($request.maxTextBytes -lt 1 -or $request.maxTextBytes -gt 524288 -or $request.qualificationSeconds -le 0 -or $request.qualificationSeconds -gt 15){throw 'FINITE_CAPTURE_QUALIFICATION'}
$fixture=$policy.mode -ceq 'OFFLINE_FIXTURE'
if($fixture){
 $prefix='D:\CodexProjects\VideoKit\docs\coder\d1resume01-capture\selfchecks\work\'
 if(-not $root.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase)){throw 'FIXTURE_ROOT_ONLY'}
 if($request.argv[0] -cne 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -or $request.argv[1] -cne '-X' -or $request.argv[2] -cne 'utf8' -or $request.argv[3] -cne '-B' -or $request.argv[4] -cne 'D:/CodexProjects/VideoKit/docs/coder/d1resume01-capture/selfchecks/capture_fixture.py'){throw 'EXACT_LOCAL_FIXTURE_ONLY'}
 if((Digest $request.argv[4]) -cne $policy.fixtureScriptSha256){throw 'FIXTURE_SCRIPT_PIN'}
}else{
 $expected='D:\CodexProjects\VideoKit\docs\tester\D1_RESUME01_CAPTURE_EXECUTION\'+$policy.planId+'\outputs'
 if($root -cne $expected -or $slots.Count -ne 5){throw 'NEW_EXACT_EXECUTION_ROOT'}
 foreach($key in @('executionAuthorization','independentCaptureReview','releaseBindingDigest')){if($policy.$key -cnotmatch '^[a-f0-9]{64}$' -or @($policy.executionPins|Where-Object sha256 -CEQ $policy.$key).Count -ne 1){throw 'REAL_RELEASE_PROOF_PIN_REQUIRED'}}
 $templates=ReadJsonExact (Join-Path $PSScriptRoot '../reference/frozen-metadata-argv.json') @() 32768
 $caps=@(65536,524288,65536,65536,524288)
 for($i=0;$i -lt 5;$i++){$phase=if($i -lt 3){'M1'}else{'M2'};if(-not (SameArgv @($slots[$i].argv) @($templates.commands[$i].argv)) -or $slots[$i].phase -cne $phase -or $slots[$i].maxTextBytes -ne $caps[$i] -or $slots[$i].qualificationSeconds -ne 15){throw 'FIVE_FIXED_SDK_REQUESTS_ONLY'}}
 if($request.argv[0] -cne 'D:/Android/SDK/platform-tools/adb.exe'){throw 'FIXED_SDK_ONLY'}
 foreach($pin in $policy.executionPins){if((Digest $pin.path) -cne $pin.sha256){throw 'EXECUTION_INPUT_PIN'}}
}
if((Digest $request.argv[0]) -cne $policy.toolSha256){throw 'ORIGINAL_TOOL_PIN'}
if(-not (Test-Path -LiteralPath $root -PathType Container)){throw 'REVIEWED_OUTPUT_PARENT_REQUIRED'}
if($global:Resume01CaptureCustody -and $global:Resume01CaptureCustody.Count -ne 0){throw 'ORIGINAL_CONTEXT_STILL_OWNED'}
# External predecessor proof is supplied by the trusted tester only after the SAME controller/tool naturally returns.
if($index -gt 0){
 $prev=$slots[$index-1].id;$proofPath=Join-Path $root ($prev+'-completion-proof.json')
 if($PredecessorProofSha -cnotmatch '^[a-f0-9]{64}$' -or (Digest $proofPath) -cne $PredecessorProofSha){throw 'ORIGINAL_PREDECESSOR_PROOF_REQUIRED'}
 $proof=ReadJsonExact $proofPath @('schema','id','scope','controllerPid','controllerExited','toolStreamsReturned','originalResourcesReturnedAtConsole','captureQualifiedAtConsole','approvedForNext','captureReceiptSha256') 2048
 $receiptPath=Join-Path $root ($prev+'-receipt.json');$prior=ReadJsonExact $receiptPath @() 8192
 if($proof.schema -cne 'RESUME01_CAPTURE_COMPLETION_PROOF_V1' -or $proof.id -cne $prev -or $proof.scope -cne $request.scope -or $proof.captureReceiptSha256 -cne (Digest $receiptPath) -or $proof.controllerPid -ne $prior.controllerPid -or $prior.captureQualified -ne $true){throw 'ORIGINAL_PREDECESSOR_IDENTITY'}
 foreach($key in @('controllerExited','toolStreamsReturned','originalResourcesReturnedAtConsole','captureQualifiedAtConsole','approvedForNext')){if($proof.$key -isnot [bool] -or $proof.$key -ne $true){throw 'ORIGINAL_PREDECESSOR_UNRETURNED_OR_UNAPPROVED'}}
}
if($slot.phase -ceq 'M2' -and $index -eq 3){
 $proofPath=Join-Path $root 'deployment-completion-proof.json'
 if($DeploymentProofSha -cnotmatch '^[a-f0-9]{64}$' -or (Digest $proofPath) -cne $DeploymentProofSha){throw 'DEPLOYMENT_PROOF_REQUIRED'}
 $proof=ReadJsonExact $proofPath @('scope','deploymentPassed','allOriginalResourcesReturned','releaseBindingDigest') 2048
 if($proof.scope -cne $request.scope -or $proof.releaseBindingDigest -cne $policy.releaseBindingDigest -or $proof.deploymentPassed -isnot [bool] -or $proof.allOriginalResourcesReturned -isnot [bool] -or $proof.deploymentPassed -ne $true -or $proof.allOriginalResourcesReturned -ne $true){throw 'DEPLOYMENT_UNPROVEN'}
}
if(Test-Path -LiteralPath (Join-Path $root 'capture-halted.json')){throw 'BATCH_HALTED_NO_REENTRY'}
if(Test-Path -LiteralPath (Join-Path $root ($request.id+'-entered.json'))){throw 'REQUEST_ALREADY_ENTERED_NO_REPLAY'}
$lockPath=Join-Path $root '.capture.lock'
if((Test-Path -LiteralPath $lockPath) -and ((Get-Item -LiteralPath $lockPath).Attributes -band [IO.FileAttributes]::ReparsePoint)){throw 'NO_REPARSE_POINT_LOCK'}
$c=@{id=$request.id;scope=$request.scope;owner=[Guid]::NewGuid().ToString();controllerPid=$PID;process=[Diagnostics.Process]::new();started=$false;startEntered=$false;startUnknown=$false;stdinReturned=$false;waitReturned=$false;processDisposed=$false;lock=$null;lockClosed=$false;lockCloseEntered=$false;readers=@();records=@();rawBytes=[long]0;rawUnknown=$false;firstFailure=$null;haltAttempted=$false;receiptAttempted=$false;recordBytes=0;writeFaultInjected=$false;qualified=$false}
if(-not $global:Resume01CaptureCustody){$global:Resume01CaptureCustody=@{}}
$global:Resume01CaptureCustody[$c.owner]=$c
function Fail([string]$Code){if($null -eq $c.firstFailure){$c.firstFailure=$Code}}
function Snapshot {
 $prefixOnly=$c.started -and @($c.readers|Where-Object {-not $_.readTaskReturned}).Count -ne 0
 return @{id=$c.id;scope=$c.scope;owner=$c.owner;controllerPid=$c.controllerPid;processToken=[Runtime.CompilerServices.RuntimeHelpers]::GetHashCode($c.process);childPid=$c.childPid;started=$c.started;waitReturned=$c.waitReturned;processDisposed=$c.processDisposed;rawBytesKnown=$c.rawBytes;rawKnownIsPrefix=$prefixOnly;rawAmountUnknown=($c.rawUnknown -or $prefixOnly);firstFailure=$c.firstFailure;readers=@($c.readers|ForEach-Object {@{role=$_.role;readerToken=$_.token;streamToken=$_.streamToken;rawBytes=$_.raw;savedBytes=$_.saved;savedAmountUnknown=[bool]$_.savedAmountUnknown;eof=$_.eof;readTaskReturned=$_.readTaskReturned;pipeCloseReturned=$_.pipeClosed;fileCloseReturned=$_.fileClosed;fileCloseEntered=$_.fileCloseEntered}});metadata=@($c.records|ForEach-Object {@{name=$_.name;opened=$_.opened;openUnknown=$_.openUnknown;writeReturned=$_.writeReturned;writeFailed=$_.writeFailed;closeEntered=$_.closeEntered;closed=$_.closed}})}
}
function WriteRecord([string]$Name,$Value,[int]$Cap){
 $r=@{name=$Name;stream=$null;task=$null;bytes=0;opened=$false;openUnknown=$false;writeStartUnknown=$false;writeReturned=$false;writeFailed=$false;closeEntered=$false;closed=$false}
 $c.records+=,$r
 $data=[Text.UTF8Encoding]::new($false).GetBytes(($Value|ConvertTo-Json -Depth 12 -Compress)+"`n")
 if($data.Length -gt $Cap){$r.writeFailed=$true;$r.closed=$true;Fail 'CONTROL_RECORD_BOUND';return}
 $r.bytes=$data.Length
 try{$r.stream=[IO.FileStream]::new((Join-Path $root $Name),[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read,4096,$true);$r.opened=$true;$r.task=$r.stream.WriteAsync($data,0,$data.Length)}catch{if(-not $r.opened){$r.openUnknown=$true}else{$r.writeStartUnknown=$true};$r.writeFailed=$true;$c.recordAmountUnknown=$true;Fail 'CONTROL_RECORD_IO_UNPROVEN'}
}
function PumpRecords {
 foreach($r in $c.records){
  if($r.task -and $r.task.IsCompleted -and -not $r.closeEntered){try{[void]$r.task.GetAwaiter().GetResult();$r.writeReturned=$true;$c.recordBytes+=$r.bytes}catch{$r.writeFailed=$true;$c.recordAmountUnknown=$true;Fail 'CONTROL_RECORD_WRITE_FAILED'};$r.closeEntered=$true;try{$r.stream.Close();$r.closed=$true}catch{Fail 'CONTROL_RECORD_CLOSE_UNKNOWN'}}
  elseif($r.opened -and -not $r.task -and -not $r.writeStartUnknown -and -not $r.closeEntered){$r.closeEntered=$true;try{$r.stream.Close();$r.closed=$true}catch{Fail 'CONTROL_RECORD_CLOSE_UNKNOWN'}}
 }
}
function RecordsReturned {return @($c.records|Where-Object {-not $_.closed}).Count -eq 0}
function ReadersReturned {return @($c.readers|Where-Object {-not $_.pipeClosed -or -not $_.fileClosed}).Count -eq 0}
function PumpReaders {
 foreach($r in $c.readers){
  if($r.write -and $r.write.IsCompleted){try{[void]$r.write.GetAwaiter().GetResult();$r.saved+=$r.writingBytes}catch{$r.recordFailed=$true;$r.savedAmountUnknown=$true;Fail 'RAW_FILE_WRITE_FAILED'};$r.write=$null}
  if($r.read -and $r.read.IsCompleted){
   try{$n=$r.read.GetAwaiter().GetResult();$r.read=$null
    if($n -eq 0){$r.eof=$true;$r.readTaskReturned=$true}
    else{
     # Charge BEFORE qualification, queue admission, serialization or any file write.
     $c.rawBytes+=$n;$r.raw+=$n
     if($c.rawBytes -gt $request.maxTextBytes){Fail 'RAW_QUALIFIER_EXCEEDED';$r.recordFailed=$true}
     if($r.role -ceq 'stderr'){Fail 'STDERR_REQUIRES_STOP'}
     if(-not $r.recordFailed){if($r.queue.Count -ge 8){$r.recordFailed=$true;Fail 'RAW_WRITER_BACKLOG'}else{$b=[byte[]]::new($n);[Array]::Copy($r.buffer,$b,$n);$r.queue.Enqueue($b)}}
     try{$r.read=$r.pipe.ReadAsync($r.buffer,0,4096)}catch{$r.read=$null;$r.readTaskReturned=$false;$c.rawUnknown=$true;Fail 'ORIGINAL_READ_START_UNKNOWN'}
    }
   }catch{$r.read=$null;$r.readTaskReturned=$true;$r.recordFailed=$true;$c.rawUnknown=$true;Fail 'ORIGINAL_READ_FAULT_UNKNOWN_AMOUNT'}
  }
  if($r.recordFailed){$r.queue.Clear()}
  if(-not $r.write -and $r.queue.Count -gt 0 -and -not $r.recordFailed){
   $b=$r.queue.Dequeue();$r.writingBytes=$b.Length
   try{if($fixture -and $policy.fixtureFault -ceq 'WRITE_FAULT_ONCE' -and -not $c.writeFaultInjected){$c.writeFaultInjected=$true;$r.write=[Threading.Tasks.Task]::FromException([IO.IOException]::new('CONTROLLED_FIXTURE_WRITE_FAULT'))}else{$r.write=$r.file.WriteAsync($b,0,$b.Length)}}catch{$r.recordFailed=$true;$r.writeStartUnknown=$true;$r.savedAmountUnknown=$true;Fail 'ORIGINAL_FILE_WRITE_START_UNKNOWN'}
  }
  if($c.waitReturned -and $r.readTaskReturned -and -not $r.write -and $r.queue.Count -eq 0){
   if(-not $r.pipeCloseEntered){$r.pipeCloseEntered=$true;try{$r.pipe.Close();$r.pipeClosed=$true}catch{Fail 'ORIGINAL_PIPE_CLOSE_UNKNOWN'}}
   $gate=$fixture -and $policy.fixtureFault -ceq 'CLOSE_GATE' -and -not (Test-Path -LiteralPath $policy.fixtureGatePath)
   if(-not $gate -and -not $r.writeStartUnknown -and -not $r.fileCloseEntered){$r.fileCloseEntered=$true;try{$r.file.Close();$r.fileClosed=$true}catch{Fail 'ORIGINAL_RAW_FILE_CLOSE_UNKNOWN'}}
  }
 }
}
$timer=[Diagnostics.Stopwatch]::StartNew()
try{
 try{$c.lock=[IO.FileStream]::new((Join-Path $root '.capture.lock'),[IO.FileMode]::OpenOrCreate,[IO.FileAccess]::ReadWrite,[IO.FileShare]::Read)}catch{
  $e=$_.Exception;while($e.InnerException){$e=$e.InnerException};if(($e.HResult -band 65535) -in @(32,33)){$c.admissionRejected=$true;throw 'ORIGINAL_CONTROLLER_EXCLUSIVE_NO_CHILD'};throw
 }
 # Repeat persistent admission under this SAME lock, without deleting/overwriting any record.
 if((Test-Path -LiteralPath (Join-Path $root 'capture-halted.json')) -or (Test-Path -LiteralPath (Join-Path $root ($request.id+'-entered.json')))){$c.admissionRejected=$true;throw 'PERSISTENT_REPLAY_OR_HALT_NO_CHILD'}
 foreach($role in @('stdout','stderr')){if(Test-Path -LiteralPath (Join-Path $root ($request.id+'-'+$role+'.bin'))){$c.admissionRejected=$true;throw 'EXISTING_OUTPUT_NO_CHILD'}}
 WriteRecord ($request.id+'-entered.json') @{schema='RESUME01_CAPTURE_INTENT_V1';request=$request;owner=$c.owner;controllerPid=$PID;policySha256=$request.policySha256} 8192
 while(-not (RecordsReturned)){PumpRecords;if($timer.Elapsed.TotalSeconds -gt $request.qualificationSeconds){Fail 'PRESTART_RECORD_TIMEOUT'};Start-Sleep -Milliseconds 2}
 if($null -eq $c.firstFailure){
  foreach($role in @('stdout','stderr')){
   $r=@{role=$role;token=[Guid]::NewGuid().ToString();file=$null;fileOpenUnknown=$false;fileCloseEntered=$false;fileClosed=$false;pipe=$null;pipeCloseEntered=$false;pipeClosed=$false;read=$null;write=$null;buffer=[byte[]]::new(4096);queue=[Collections.Generic.Queue[byte[]]]::new();raw=[long]0;saved=[long]0;eof=$false;readTaskReturned=$false;recordFailed=$false}
   $c.readers+=,$r
   try{$r.file=[IO.FileStream]::new((Join-Path $root ($request.id+'-'+$role+'.bin')),[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read,4096,$true)}catch{$r.fileOpenUnknown=$true;throw}
  }
  $info=[Diagnostics.ProcessStartInfo]::new();$info.FileName=$request.argv[0];$info.UseShellExecute=$false;$info.CreateNoWindow=$true;$info.RedirectStandardInput=$true;$info.RedirectStandardOutput=$true;$info.RedirectStandardError=$true
  for($i=1;$i -lt $request.argv.Count;$i++){$info.ArgumentList.Add([string]$request.argv[$i])}
  $c.process.StartInfo=$info;$c.startEntered=$true
  try{if(-not $c.process.Start()){$c.startUnknown=$true;throw 'START_UNPROVEN'};$c.started=$true;$c.childPid=$c.process.Id}catch{$c.startUnknown=$true;throw}
  foreach($r in $c.readers){
   $r.pipe=if($r.role -ceq 'stdout'){$c.process.StandardOutput.BaseStream}else{$c.process.StandardError.BaseStream};$r.streamToken=[Runtime.CompilerServices.RuntimeHelpers]::GetHashCode($r.pipe)
   if($fixture -and $policy.fixtureFault -ceq 'READ_FAULT_ONCE' -and $r.role -ceq 'stdout'){$tcs=[Threading.Tasks.TaskCompletionSource[int]]::new();$tcs.SetException([IO.IOException]::new('CONTROLLED_FIXTURE_READ_FAULT'));$r.read=$tcs.Task}else{$r.read=$r.pipe.ReadAsync($r.buffer,0,4096)}
  }
  $c.process.StandardInput.Close();$c.stdinReturned=$true
 }
}catch{Fail 'ORIGINAL_INITIALIZATION_OR_ADMISSION_FAILED'}
if($c.admissionRejected){if($c.lock){$c.lock.Close()};$c.process.Dispose();$global:Resume01CaptureCustody.Remove($c.owner);throw 'ADMISSION_REJECTED_NO_CHILD_NO_NEW_RECORD'}
# This controller remains the strong owner while any original result is pending or unknown.
do{
 PumpRecords
 if($c.started -and -not $c.waitReturned -and -not $c.waitEntered){try{if($c.process.HasExited){$c.waitEntered=$true;$c.process.WaitForExit();$c.waitReturned=$true;$c.exitCode=$c.process.ExitCode;if($c.exitCode -ne 0){Fail 'CHILD_NONZERO_EXIT'}}}catch{$c.waitEntered=$true;Fail 'ORIGINAL_WAIT_UNKNOWN'}}
 PumpReaders
 if($timer.Elapsed.TotalSeconds -gt $request.qualificationSeconds){Fail 'QUALIFICATION_TIMEOUT_NO_TERMINATION'}
 if($c.firstFailure -and -not $c.haltAttempted){$c.haltAttempted=$true;WriteRecord 'capture-halted.json' (Snapshot) 2048}
 $bodyReturned=$c.started -and $c.waitReturned -and $c.stdinReturned -and (ReadersReturned)
 if(-not $c.startEntered -and $c.readers.Count -eq 0){$bodyReturned=$true}
 if($bodyReturned -and -not $c.processDisposeEntered){$c.processDisposeEntered=$true;try{$c.process.Dispose();$c.processDisposed=$true}catch{Fail 'ORIGINAL_PROCESS_DISPOSE_UNKNOWN'}}
 if($bodyReturned -and $c.processDisposed -and (RecordsReturned) -and -not $c.receiptAttempted){
  $c.receiptAttempted=$true;$c.qualified=($null -eq $c.firstFailure) -and @($c.readers|Where-Object {-not $_.eof -or $_.recordFailed}).Count -eq 0
  $facts=Snapshot;$facts.schema='RESUME01_CAPTURE_RECEIPT_V1';$facts.captureQualified=$c.qualified;$facts.receiptOwnCloseNotProvenByThisFile=$true;$facts.metadataFilesBeforeReceiptReturned=$true;$facts.rawAmountUnknown=$c.rawUnknown
  WriteRecord ($request.id+'-receipt.json') $facts 8192
 }
 $allReturned=$bodyReturned -and $c.processDisposed -and $c.receiptAttempted -and (RecordsReturned)
 if(-not $allReturned){Start-Sleep -Milliseconds 5}
}while(-not $allReturned)
if($c.lock -and -not $c.lockCloseEntered){$c.lockCloseEntered=$true;try{$c.lock.Close();$c.lockClosed=$true}catch{Fail 'ORIGINAL_BATCH_LOCK_CLOSE_UNKNOWN'}}
if(-not $c.lockClosed){while($true){Start-Sleep -Milliseconds 500}}
$console=Snapshot;$console.schema='RESUME01_CAPTURE_CONSOLE_V1';$console.captureQualified=$c.qualified -and $null -eq $c.firstFailure;$console.allOriginalResourcesReturnedAtConsole=$true;$console.recordWriteBytesKnown=$c.recordBytes;$console.recordWriteAmountUnknown=[bool]$c.recordAmountUnknown;$console.captureReceiptSha256=Digest (Join-Path $root ($request.id+'-receipt.json'));$console.externalControllerExitProofStillRequired=$true
$text=($console|ConvertTo-Json -Depth 12 -Compress)+"`n";$consoleBytes=[Text.UTF8Encoding]::new($false).GetByteCount($text)
if($consoleBytes -gt 4096){while($true){Start-Sleep -Milliseconds 500}}
[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false)
try{[Console]::Out.Write($text);[Console]::Out.Flush()}catch{while($true){Start-Sleep -Milliseconds 500}}
$global:Resume01CaptureCustody.Remove($c.owner)
if($console.captureQualified){exit 0}else{exit 2}
