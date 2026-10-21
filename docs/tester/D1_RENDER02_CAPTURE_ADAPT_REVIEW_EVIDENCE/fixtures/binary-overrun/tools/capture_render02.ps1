param([Parameter(Mandatory=$true)][string]$RequestPath,[string]$PredecessorProofSha='ABSENT')
$ErrorActionPreference='Stop'
# Minimal RENDER02 derivative. Same original Process/async pipes/files/lock; no concurrent child.
function ReadJsonExact([string]$Path,[string[]]$Keys,[int]$Max=8192){
 $raw=[IO.File]::ReadAllBytes($Path);if($raw.Length -gt $Max){throw 'JSON_BOUND'}
 $doc=[Text.Json.JsonDocument]::Parse([Text.Encoding]::UTF8.GetString($raw));$seen=[Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
 try{foreach($p in $doc.RootElement.EnumerateObject()){if(-not $seen.Add($p.Name)){throw 'DUPLICATE_JSON_FIELD'}}}finally{$doc.Dispose()}
 $o=[Text.Encoding]::UTF8.GetString($raw)|ConvertFrom-Json
 if($Keys.Count -gt 0 -and @(Compare-Object -CaseSensitive @($o.PSObject.Properties.Name|Sort-Object) @($Keys|Sort-Object)).Count -ne 0){throw 'EXACT_SCHEMA_REQUIRED'}
 return $o
}
function Digest([string]$Path){return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()}
function SameArgv($A,$B){if($A.Count -ne $B.Count){return $false};for($n=0;$n -lt $A.Count;$n++){if($A[$n] -isnot [string] -or $A[$n] -cne $B[$n]){return $false}};return $true}
function NoLinks([string]$Path){$p=if(Test-Path -LiteralPath $Path -PathType Container){[IO.DirectoryInfo]::new($Path)}else{[IO.FileInfo]::new($Path)};while($null -ne $p){if($p.Exists -and ($p.Attributes -band [IO.FileAttributes]::ReparsePoint)){throw 'NO_REPARSE_POINT'};$p=if($p -is [IO.FileInfo]){$p.Directory}else{$p.Parent}}}
$policyPath=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../release/capture-policy.json'))
$policy=ReadJsonExact $policyPath @() 65536
if($policy.mode -ceq 'PREPARATION_ONLY'){throw 'PREPARATION_ONLY_NO_EXECUTION_AUTHORIZATION'}
if($policy.schema -cne 'RENDER02_CAPTURE_POLICY_V1' -or $policy.entrySha256 -cne (Digest $PSCommandPath)){throw 'ENTRY_POLICY_PIN'}
if($policy.mode -cnotin @('PRODUCTION','OFFLINE_FIXTURE')){throw 'EXACT_POLICY_MODE'}
$request=ReadJsonExact $RequestPath @('schema','id','policySha256','scope','evidenceRoot','argv','maxTextBytes','maxBinaryBytes','qualificationSeconds')
foreach($key in @('schema','id','policySha256','scope','evidenceRoot')){if($request.$key -isnot [string]){throw 'EXACT_REQUEST_TYPES'}}
foreach($key in @('maxTextBytes','maxBinaryBytes')){if($request.$key -isnot [long] -and $request.$key -isnot [int]){throw 'EXACT_REQUEST_TYPES'}}
if($request.argv -isnot [array] -or $request.qualificationSeconds -isnot [ValueType] -or [double]::IsNaN([double]$request.qualificationSeconds) -or [double]::IsInfinity([double]$request.qualificationSeconds)){throw 'EXACT_REQUEST_TYPES'}
if($request.schema -cne 'RENDER02_CAPTURE_REQUEST_V1' -or $request.policySha256 -cne (Digest $policyPath)){throw 'REQUEST_POLICY_PIN'}
$root=[IO.Path]::GetFullPath([string]$policy.evidenceRoot);NoLinks $root
if($request.evidenceRoot -cne $policy.evidenceRoot -or $request.scope -cne $policy.scope -or $policy.scope -cnotmatch '^[a-f0-9]{64}$'){throw 'EXACT_SCOPE_ROOT'}
$fixture=$policy.mode -ceq 'OFFLINE_FIXTURE';$slot=$null;$previous=$null;$inputPin=$null;$payloadPin=$null
if($fixture){
 $prefix='D:\CodexProjects\VideoKit\docs\coder\d1render02-capture\selfchecks\work\'
 $reviewPrefix='D:\CodexProjects\VideoKit\docs\tester\D1_RENDER02_CAPTURE_ADAPT_REVIEW_EVIDENCE\fixtures\'
 if(-not $root.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase) -and -not $root.StartsWith($reviewPrefix,[StringComparison]::OrdinalIgnoreCase)){throw 'FIXTURE_ROOT_ONLY'}
 $slots=@($policy.slots);if($slots.Count -lt 1 -or $slots.Count -gt 2){throw 'FINITE_FIXTURE_SLOTS'}
 foreach($s in $slots){
  if($s.id -cnotin @('fixture_a','fixture_b') -or $s.argv.Count -ne 7 -or $s.argv[0] -cne 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -or $s.argv[1] -cne '-X' -or $s.argv[2] -cne 'utf8' -or $s.argv[3] -cne '-B' -or $s.argv[4] -cne 'D:/CodexProjects/VideoKit/docs/coder/d1render02-capture/selfchecks/capture_fixture.py' -or $s.argv[5] -cnotin @('success','binary','binary_stderr','stdin','stderr','overrun','late','nonzero') -or $s.argv[6] -cne (Join-Path $root 'fixture-gate')){throw 'EXACT_LOCAL_FIXTURE_ONLY'}
  if((Digest $s.argv[4]) -cne $policy.fixtureScriptSha256){throw 'FIXTURE_SCRIPT_PIN'}
 }
 $index=-1;for($i=0;$i -lt $slots.Count;$i++){if($slots[$i].id -ceq $request.id){if($index -ne -1){throw 'DUPLICATE_SLOT'};$index=$i}}
 if($index -lt 0){throw 'EXACT_REQUEST_SLOT'};$slot=$slots[$index];if($index -gt 0){$previous=$slots[$index-1].id}
 if($policy.fixtureFault -cnotin @('NONE','READ_FAULT_ONCE','WRITE_FAULT_ONCE','STDIN_WRITE_FAULT_ONCE','STDIN_CLOSE_GATE','CLOSE_GATE')){throw 'FIXED_FIXTURE_FAULT_ONLY'}
 if($policy.inputPin){$inputPin=$policy.inputPin;if([IO.Path]::GetFullPath($inputPin.path) -cne (Join-Path $root 'fixture-input.bin') -or $inputPin.bytes -ne 349102 -or $inputPin.sha256 -cnotmatch '^[a-f0-9]{64}$'){throw 'FIXED_FIXTURE_INPUT'}}
}else{
 $planPath=Join-Path $PSScriptRoot '../reference/exact-operation-and-accounting-plan.json'
 if((Digest $planPath) -cne '1db733cd14d51b47d41df3670a5d9d84b1f68f599aeb3d02b8d1d814236810d1'){throw 'FIXED_28_PLAN_PIN'}
 $plan=ReadJsonExact $planPath @() 32768
 if($policy.planId -cnotmatch '^[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{12}$' -or $policy.planId -ceq $plan.scopeId -or $policy.scope -ceq $plan.renderScopeSha256){throw 'FRESH_SCOPE_REQUIRED'}
 if($root -cne ('D:\CodexProjects\VideoKit\docs\tester\D1_RENDER02_CAPTURE_EXECUTION\'+$policy.planId+'\outputs')){throw 'NEW_EXACT_EXECUTION_ROOT'}
 foreach($k in @('authorization','independentReview')){if($policy.$k.sha256 -cnotmatch '^[a-f0-9]{64}$' -or (Digest $policy.$k.path) -cne $policy.$k.sha256){throw 'NEW_AUTHORIZATION_AND_REVIEW_REQUIRED'}}
 $activation=ReadJsonExact $policy.authorization.path @('schema','scope','planId','entrySha256','planSha256','candidateSealSha256','reviewSha256','toolSha256','evidenceRoot','approvedForExecution')
 if($activation.schema -cne 'RENDER02_CAPTURE_ACTIVATION_V1' -or $activation.approvedForExecution -isnot [bool] -or -not $activation.approvedForExecution -or $activation.scope -cne $policy.scope -or $activation.planId -cne $policy.planId -or $activation.entrySha256 -cne $policy.entrySha256 -or $activation.planSha256 -cne (Digest $planPath) -or $activation.reviewSha256 -cne $policy.independentReview.sha256 -or $activation.evidenceRoot -cne $root -or $activation.toolSha256 -cne $policy.toolSha256 -or $activation.candidateSealSha256 -cne 'a226b5fe0703d31c486ec2deaad1c2f2241169f4c8257701331cd5d9c1a83581'){throw 'EXACT_NEW_ACTIVATION_BINDING'}
 $slots=@();foreach($s in $plan.steps){$a=@($s.argv|ForEach-Object {if($_ -ceq $plan.renderScopeSha256){$policy.scope}else{$_}});$q=if($s.role -cin @('INSTALL','CASE')){45}else{15};$slots+=@{id=$s.id;argv=$a;maxTextBytes=$s.maxTextBytesQualification;maxBinaryBytes=$s.maxBinaryArchiveBytesQualification;qualificationSeconds=$q;dependency=$s.dependsOn;role=$s.role}}
 $index=-1;for($i=0;$i -lt $slots.Count;$i++){if($slots[$i].id -ceq $request.id){$index=$i}};if($index -lt 0){throw 'EXACT_28_REQUEST_ONLY'};$slot=$slots[$index]
 if($slot.role -ceq 'OPTIONAL_BINARY'){throw 'SCREENSHOT_NOT_RUN_LIVE_PARENT_ASSOCIATION_UNPROVEN'}
 for($i=$index-1;$i -ge 0;$i--){if($slots[$i].role -cne 'OPTIONAL_BINARY'){$previous=$slots[$i].id;break}}
 if($request.id -ceq 'private_fixture_copy'){$inputPin=$plan.fixtureSourcePin}
 if($request.id -ceq 'install_app'){$payloadPin=@{path=$slot.argv[4];bytes=10480388;sha256='2f6e1cf02d85d8b0bd32ca0c475aea9e182a8b3b55e17a6da066a6ddfc5e2d94'}}
 if($request.id -ceq 'install_test'){$payloadPin=@{path=$slot.argv[4];bytes=2695613;sha256='88241afd1cfe50fee41be95d788d76948bdee24cec14a26329040f69970e63cb'}}
}
if(-not (SameArgv @($request.argv) @($slot.argv)) -or $request.maxTextBytes -ne $slot.maxTextBytes -or $request.maxBinaryBytes -ne $slot.maxBinaryBytes -or $request.qualificationSeconds -ne $slot.qualificationSeconds){throw 'EXACT_ARGV_CAP_QUALIFIER'}
if($request.maxTextBytes -lt 1 -or $request.maxTextBytes -gt 524288 -or $request.maxBinaryBytes -lt 0 -or $request.maxBinaryBytes -gt 4194304 -or $request.qualificationSeconds -le 0 -or $request.qualificationSeconds -gt 45){throw 'FINITE_QUALIFICATION'}
if((Digest $request.argv[0]) -cne $policy.toolSha256){throw 'ORIGINAL_TOOL_PIN'}
if(-not (Test-Path -LiteralPath $root -PathType Container)){throw 'REVIEWED_OUTPUT_PARENT_REQUIRED'}
if($global:Render02CaptureCustody -and $global:Render02CaptureCustody.Count -ne 0){throw 'ORIGINAL_CONTEXT_STILL_OWNED'}
# Existing external original-controller return proof, plus the exact semantic dependency. Not a permit issuer.
$batchSdkBefore=0;$batchTextBefore=[long]0;$batchBinaryBefore=[long]0;$proofReadBytes=0
if($previous -or -not $fixture){
 $proofId=if($previous){$previous}else{'pre_sdk_local_gate'};$proofPath=Join-Path $root ($proofId+'-completion-proof.json')
 if($PredecessorProofSha -cnotmatch '^[a-f0-9]{64}$' -or (Digest $proofPath) -cne $PredecessorProofSha){throw 'ORIGINAL_PREDECESSOR_PROOF_REQUIRED'}
 $proof=ReadJsonExact $proofPath @('schema','id','nextId','scope','controllerPid','controllerExited','toolStreamsReturned','originalResourcesReturnedAtConsole','captureQualifiedAtConsole','approvedForNext','captureReceiptSha256','semanticDependency','dependencyAccepted','batchSdkChildrenEntered','batchTextChargedBytesKnown','batchBinaryArchiveBytesKnown','batchAmountUnknown') 1536
 $proofReadBytes=(Get-Item -LiteralPath $proofPath).Length
 if($proof.schema -cne 'RENDER02_CAPTURE_COMPLETION_PROOF_V1' -or $proof.id -cne $proofId -or $proof.nextId -cne $request.id -or $proof.scope -cne $policy.scope){throw 'ORIGINAL_PREDECESSOR_IDENTITY'}
 foreach($key in @('controllerExited','toolStreamsReturned','originalResourcesReturnedAtConsole','captureQualifiedAtConsole','approvedForNext','dependencyAccepted')){if($proof.$key -isnot [bool] -or -not $proof.$key){throw 'ORIGINAL_PREDECESSOR_UNRETURNED_OR_UNAPPROVED'}}
 foreach($key in @('batchSdkChildrenEntered','batchTextChargedBytesKnown','batchBinaryArchiveBytesKnown')){if(($proof.$key -isnot [long] -and $proof.$key -isnot [int]) -or $proof.$key -lt 0){throw 'EXACT_EXTERNAL_ACCOUNTING'}}
 if($proof.batchAmountUnknown -isnot [bool] -or $proof.batchAmountUnknown){throw 'BATCH_ACCOUNTING_UNKNOWN_STOP'}
 $batchSdkBefore=$proof.batchSdkChildrenEntered;$batchTextBefore=[long]$proof.batchTextChargedBytesKnown;$batchBinaryBefore=[long]$proof.batchBinaryArchiveBytesKnown
 if(-not $fixture){$expectedBefore=@($slots|Select-Object -First $index|Where-Object role -CNE 'OPTIONAL_BINARY').Count;if($batchSdkBefore -ne $expectedBefore){throw 'NO_SDK_CONSUMPTION_RESET'}}
 if(-not $fixture -and $proof.semanticDependency -cne $slot.dependency){throw 'EXACT_SEMANTIC_DEPENDENCY'}
 if($previous){$receiptPath=Join-Path $root ($previous+'-receipt.json');$prior=ReadJsonExact $receiptPath @() 8192;if($proof.captureReceiptSha256 -cne (Digest $receiptPath) -or $proof.controllerPid -ne $prior.controllerPid -or $prior.captureQualified -ne $true -or $prior.rawAmountUnknown){throw 'ORIGINAL_PREDECESSOR_RECEIPT'}}
}
if($batchSdkBefore+1 -gt 32 -or $batchTextBefore+$request.maxTextBytes+14000 -gt 4194304 -or $batchBinaryBefore+$request.maxBinaryBytes -gt 16777216){throw 'BATCH_REMAINING_QUALIFICATION_BUDGET'}
if(Test-Path -LiteralPath (Join-Path $root 'capture-halted.json')){throw 'BATCH_HALTED_NO_REENTRY'}
if(Test-Path -LiteralPath (Join-Path $root ($request.id+'-entered.json'))){throw 'REQUEST_ALREADY_ENTERED_NO_REPLAY'}
$lockPath=Join-Path $root '.capture.lock';NoLinks $lockPath

$c=@{id=$request.id;scope=$request.scope;owner=[Guid]::NewGuid().ToString();controllerPid=$PID;process=[Diagnostics.Process]::new();started=$false;startEntered=$false;startUnknown=$false;stdinReturned=$false;waitReturned=$false;processDisposed=$false;lock=$null;lockClosed=$false;lockCloseEntered=$false;readers=@();records=@();rawBytes=[long]0;textBytes=[long]0;binaryBytes=[long]0;rawUnknown=$false;firstFailure=$null;haltAttempted=$false;receiptAttempted=$false;recordBytes=0;writeFaultInjected=$false;qualified=$false}
if(-not $global:Render02CaptureCustody){$global:Render02CaptureCustody=@{}}
$global:Render02CaptureCustody[$c.owner]=$c
function Fail([string]$Code){if($null -eq $c.firstFailure){$c.firstFailure=$Code}}
function Snapshot {
 $prefixOnly=$c.started -and @($c.readers|Where-Object {-not $_.readTaskReturned}).Count -ne 0
 return @{id=$c.id;scope=$c.scope;owner=$c.owner;controllerPid=$c.controllerPid;processToken=[Runtime.CompilerServices.RuntimeHelpers]::GetHashCode($c.process);childPid=$c.childPid;started=$c.started;waitReturned=$c.waitReturned;processDisposed=$c.processDisposed;rawBytesKnown=$c.rawBytes;textBytesKnown=$c.textBytes;binaryBytesKnown=$c.binaryBytes;input=(InputFacts);rawKnownIsPrefix=$prefixOnly;rawAmountUnknown=($c.rawUnknown -or $prefixOnly);firstFailure=$c.firstFailure;readers=@($c.readers|ForEach-Object {@{role=$_.role;readerToken=$_.token;streamToken=$_.streamToken;kind=$_.kind;rawBytes=$_.raw;savedBytes=$_.saved;readCalls=$_.readCalls;writeCalls=$_.writeCalls;writeAttemptedBytes=$_.writeAttempted;savedAmountUnknown=[bool]$_.savedAmountUnknown;eof=$_.eof;readTaskReturned=$_.readTaskReturned;pipeCloseReturned=$_.pipeClosed;fileCloseReturned=$_.fileClosed;fileCloseEntered=$_.fileCloseEntered}});metadata=@($c.records|ForEach-Object {@{name=$_.name;writeRequestedBytes=$_.bytes;opened=$_.opened;openUnknown=$_.openUnknown;writeReturned=$_.writeReturned;writeFailed=$_.writeFailed;closeEntered=$_.closeEntered;closed=$_.closed}})}
}
# Attached to the SAME original context before source open/start. One source, one read, one write.
$c.input=@{source=$null;openEntered=$false;openReturned=$false;sourceCloseEntered=$false;sourceClosed=$true;pinReadBytes=[long]0;pinReadCalls=0;pinUnknown=$false;verified=$false;expectedBytes=[long]0;expectedSha='';payloadCommitted=[long]0;sourceRead=$null;sourceReadCalls=0;sourceReadBytes=[long]0;sourceReadReturned=$true;sourceEof=$false;sourceUnknown=$false;buffer=[byte[]]::new(4096);write=$null;writeCalls=0;writeAttempted=[long]0;writeReturnedBytes=[long]0;writeAmountUnknown=$false;writing=0;failed=$false;stdinCloseEntered=$false;stdinClosed=$false;closeGateObserved=$false}
function OpenPinnedSource {
 $pin=if($inputPin){$inputPin}else{$payloadPin};if(-not $pin){return}
 $i=$c.input;$i.expectedBytes=[long]$pin.bytes;$i.expectedSha=[string]$pin.sha256
 if($i.expectedBytes -lt 1 -or $i.expectedBytes -gt 10480388 -or $i.expectedSha -cnotmatch '^[a-f0-9]{64}$'){throw 'FINITE_SOURCE_PIN'}
 NoLinks $pin.path;$i.openEntered=$true;$i.sourceClosed=$false
 $i.source=[IO.FileStream]::new($pin.path,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read,4096,$true);$i.openReturned=$true
 if($i.source.Length -ne $i.expectedBytes){Fail 'SOURCE_LENGTH_MISMATCH';$i.failed=$true;return}
 $h=[Security.Cryptography.IncrementalHash]::CreateHash([Security.Cryptography.HashAlgorithmName]::SHA256)
 try{do{$i.pinReadCalls++;$n=$i.source.Read($i.buffer,0,4096);$i.pinReadBytes+=$n;if($n -gt 0){$h.AppendData($i.buffer,0,$n)}}while($n -gt 0);$actual=[Convert]::ToHexString($h.GetHashAndReset()).ToLowerInvariant();if($actual -cne $i.expectedSha){Fail 'SOURCE_HASH_MISMATCH';$i.failed=$true;return};$i.verified=$true;$i.source.Position=0;if($payloadPin){$i.payloadCommitted=$i.expectedBytes}}
 catch{$i.pinUnknown=$true;$i.failed=$true;Fail 'PIN_SOURCE_READ_UNKNOWN'}finally{$h.Dispose()}
}
function PumpInput {
 if(-not $c.started){return};$i=$c.input
 if($inputPin -and -not $i.failed){
  if($i.write -and $i.write.IsCompleted){try{[void]$i.write.GetAwaiter().GetResult();$i.writeReturnedBytes+=$i.writing}catch{$i.writeAmountUnknown=$true;$i.failed=$true;Fail 'ORIGINAL_STDIN_WRITE_FAULT_UNKNOWN_AMOUNT'};$i.write=$null}
  if($i.sourceRead -and $i.sourceRead.IsCompleted){
   try{$n=$i.sourceRead.GetAwaiter().GetResult();$i.sourceRead=$null;$i.sourceReadReturned=$true;$i.sourceReadBytes+=$n
    if($n -eq 0){$i.sourceEof=$true;if($i.sourceReadBytes -ne $i.expectedBytes -or $i.writeReturnedBytes -ne $i.expectedBytes){$i.failed=$true;Fail 'EXACT_STDIN_LENGTH_NOT_RETURNED'}}
    else{$i.writing=$n;$i.writeCalls++;$i.writeAttempted+=$n
     if($fixture -and $policy.fixtureFault -ceq 'STDIN_WRITE_FAULT_ONCE' -and $i.writeCalls -eq 1){$i.write=[Threading.Tasks.Task]::FromException([IO.IOException]::new('CONTROLLED_STDIN_WRITE_FAULT'))}
     else{try{$i.write=$c.process.StandardInput.BaseStream.WriteAsync($i.buffer,0,$n)}catch{$i.failed=$true;$i.writeStartUnknown=$true;$i.writeAmountUnknown=$true;Fail 'ORIGINAL_STDIN_WRITE_START_UNKNOWN'}}
    }
   }catch{$i.sourceRead=$null;$i.sourceReadReturned=$true;$i.sourceUnknown=$true;$i.failed=$true;Fail 'ORIGINAL_STDIN_SOURCE_READ_UNKNOWN'}
  }
  if(-not $i.write -and -not $i.sourceRead -and -not $i.failed -and -not $i.sourceEof){$i.sourceReadCalls++;$i.sourceReadReturned=$false;try{$i.sourceRead=$i.source.ReadAsync($i.buffer,0,4096)}catch{$i.sourceUnknown=$true;$i.readStartUnknown=$true;$i.failed=$true;Fail 'ORIGINAL_STDIN_SOURCE_READ_START_UNKNOWN'}}
 }
 # Faulted tasks must be observed once even after another failure; never close while one is pending.
 if($i.write -and $i.write.IsCompleted -and $i.failed){try{[void]$i.write.GetAwaiter().GetResult();$i.writeReturnedBytes+=$i.writing}catch{$i.writeAmountUnknown=$true;Fail 'ORIGINAL_STDIN_WRITE_FAULT_UNKNOWN_AMOUNT'};$i.write=$null}
 if($i.sourceRead -and $i.sourceRead.IsCompleted -and $i.failed){try{$n=$i.sourceRead.GetAwaiter().GetResult();$i.sourceReadBytes+=$n}catch{$i.sourceUnknown=$true};$i.sourceRead=$null;$i.sourceReadReturned=$true}
 $done=(-not $inputPin) -or (($i.sourceEof -or $i.failed) -and -not $i.write -and -not $i.sourceRead -and -not $i.writeStartUnknown -and -not $i.readStartUnknown)
 if($done -and -not $i.stdinCloseEntered){
  $gate=$fixture -and $policy.fixtureFault -ceq 'STDIN_CLOSE_GATE' -and -not (Test-Path -LiteralPath $policy.fixtureGatePath)
  if($gate){$i.closeGateObserved=$true;return}
  $i.stdinCloseEntered=$true;try{$c.process.StandardInput.Close();$i.stdinClosed=$true;$c.stdinReturned=$true}catch{Fail 'ORIGINAL_STDIN_CLOSE_UNKNOWN'}
 }
}
function PumpInputSourceClose {
 $i=$c.input
 if($i.openReturned -and -not $i.sourceCloseEntered -and ((-not $c.startEntered) -or ($c.waitReturned -and $c.stdinReturned)) -and -not $i.write -and -not $i.sourceRead){$i.sourceCloseEntered=$true;try{$i.source.Close();$i.sourceClosed=$true}catch{Fail 'ORIGINAL_INPUT_SOURCE_CLOSE_UNKNOWN'}}
}
function InputReturned {return $c.input.sourceClosed -and -not $c.input.write -and -not $c.input.sourceRead -and -not $c.input.writeStartUnknown -and -not $c.input.readStartUnknown}
function InputFacts {
 $i=$c.input;return @{sourceToken=if($i.source){[Runtime.CompilerServices.RuntimeHelpers]::GetHashCode($i.source)}else{0};sourceOpenReturned=$i.openReturned;sourceCloseReturned=$i.sourceClosed;verified=$i.verified;expectedBytes=$i.expectedBytes;expectedSha256=$i.expectedSha;pinReadCalls=$i.pinReadCalls;pinReadBytes=$i.pinReadBytes;pinAmountUnknown=$i.pinUnknown;transportSourceReadCalls=$i.sourceReadCalls;transportSourceReadBytes=$i.sourceReadBytes;sourceReadTaskReturned=$i.sourceReadReturned;sourceEof=$i.sourceEof;sourceAmountUnknown=($i.sourceUnknown -or [bool]$i.sourceRead);stdinWriteCalls=$i.writeCalls;stdinWriteAttemptedBytes=$i.writeAttempted;stdinWriteReturnedBytes=$i.writeReturnedBytes;stdinWriteTaskReturned=(-not $i.write);stdinWriteAmountUnknown=($i.writeAmountUnknown -or [bool]$i.write);stdinCloseReturned=$i.stdinClosed;closeGateObserved=$i.closeGateObserved;outboundApkPayloadCommittedBytes=$i.payloadCommitted;outboundSdkWireBytes='NOT_MEASURED_NOT_FREE_NOT_ARCHIVE';inputPinAndTransferReadsAreSeparate=$true}
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
     if($r.kind -ceq 'BINARY'){$c.binaryBytes+=$n;if($c.binaryBytes -gt $request.maxBinaryBytes){Fail 'BINARY_QUALIFIER_EXCEEDED';$r.recordFailed=$true}}else{$c.textBytes+=$n;if($c.textBytes -gt $request.maxTextBytes){Fail 'TEXT_QUALIFIER_EXCEEDED';$r.recordFailed=$true}}
     if($r.role -ceq 'stderr'){Fail 'STDERR_REQUIRES_STOP'}
     if(-not $r.recordFailed){if($r.queue.Count -ge 8){$r.recordFailed=$true;Fail 'RAW_WRITER_BACKLOG'}else{$b=[byte[]]::new($n);[Array]::Copy($r.buffer,$b,$n);$r.queue.Enqueue($b)}}
     try{$r.readCalls++;$r.read=$r.pipe.ReadAsync($r.buffer,0,4096)}catch{$r.read=$null;$r.readTaskReturned=$false;$c.rawUnknown=$true;Fail 'ORIGINAL_READ_START_UNKNOWN'}
    }
   }catch{$r.read=$null;$r.readTaskReturned=$true;$r.recordFailed=$true;$c.rawUnknown=$true;Fail 'ORIGINAL_READ_FAULT_UNKNOWN_AMOUNT'}
  }
  if($r.recordFailed){$r.queue.Clear()}
  if(-not $r.write -and $r.queue.Count -gt 0 -and -not $r.recordFailed){
   $b=$r.queue.Dequeue();$r.writingBytes=$b.Length;$r.writeCalls++;$r.writeAttempted+=$b.Length
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
 WriteRecord ($request.id+'-entered.json') @{schema='RENDER02_CAPTURE_INTENT_V1';request=$request;owner=$c.owner;controllerPid=$PID;policySha256=$request.policySha256} 8192
 while(-not (RecordsReturned)){PumpRecords;if($timer.Elapsed.TotalSeconds -gt $request.qualificationSeconds){Fail 'PRESTART_RECORD_TIMEOUT'};Start-Sleep -Milliseconds 2}
 if($null -eq $c.firstFailure){
  OpenPinnedSource
  if($c.firstFailure){throw 'SOURCE_PIN_REJECTED_BEFORE_CHILD'}
  foreach($role in @('stdout','stderr')){
   $r=@{role=$role;kind=if($role -ceq 'stdout' -and $request.maxBinaryBytes -gt 0){'BINARY'}else{'TEXT'};readCalls=0;writeCalls=0;writeAttempted=[long]0;token=[Guid]::NewGuid().ToString();file=$null;fileOpenUnknown=$false;fileCloseEntered=$false;fileClosed=$false;pipe=$null;pipeCloseEntered=$false;pipeClosed=$false;read=$null;write=$null;buffer=[byte[]]::new(4096);queue=[Collections.Generic.Queue[byte[]]]::new();raw=[long]0;saved=[long]0;eof=$false;readTaskReturned=$false;recordFailed=$false}
   $c.readers+=,$r
   try{$r.file=[IO.FileStream]::new((Join-Path $root ($request.id+'-'+$role+'.bin')),[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read,4096,$true)}catch{$r.fileOpenUnknown=$true;throw}
  }
  $info=[Diagnostics.ProcessStartInfo]::new();$info.FileName=$request.argv[0];$info.UseShellExecute=$false;$info.CreateNoWindow=$true;$info.RedirectStandardInput=$true;$info.RedirectStandardOutput=$true;$info.RedirectStandardError=$true
  for($i=1;$i -lt $request.argv.Count;$i++){$info.ArgumentList.Add([string]$request.argv[$i])}
  $c.process.StartInfo=$info;$c.startEntered=$true
  try{if(-not $c.process.Start()){$c.startUnknown=$true;throw 'START_UNPROVEN'};$c.started=$true;$c.childPid=$c.process.Id}catch{$c.startUnknown=$true;throw}
  foreach($r in $c.readers){
   $r.pipe=if($r.role -ceq 'stdout'){$c.process.StandardOutput.BaseStream}else{$c.process.StandardError.BaseStream};$r.streamToken=[Runtime.CompilerServices.RuntimeHelpers]::GetHashCode($r.pipe)
   if($fixture -and $policy.fixtureFault -ceq 'READ_FAULT_ONCE' -and $r.role -ceq 'stdout'){$tcs=[Threading.Tasks.TaskCompletionSource[int]]::new();$tcs.SetException([IO.IOException]::new('CONTROLLED_FIXTURE_READ_FAULT'));$r.read=$tcs.Task}else{$r.readCalls++;$r.read=$r.pipe.ReadAsync($r.buffer,0,4096)}
  }
  PumpInput
 }
}catch{Fail 'ORIGINAL_INITIALIZATION_OR_ADMISSION_FAILED'}
if($c.admissionRejected){if($c.lock){$c.lock.Close()};$c.process.Dispose();$global:Render02CaptureCustody.Remove($c.owner);throw 'ADMISSION_REJECTED_NO_CHILD_NO_NEW_RECORD'}
# This controller remains the strong owner while any original result is pending or unknown.
do{
 PumpRecords
 if($c.started -and -not $c.waitReturned -and -not $c.waitEntered){try{if($c.process.HasExited){$c.waitEntered=$true;$c.process.WaitForExit();$c.waitReturned=$true;$c.exitCode=$c.process.ExitCode;if($c.exitCode -ne 0){Fail 'CHILD_NONZERO_EXIT'}}}catch{$c.waitEntered=$true;Fail 'ORIGINAL_WAIT_UNKNOWN'}}
 PumpReaders
 PumpInput
 PumpInputSourceClose
 if($timer.Elapsed.TotalSeconds -gt $request.qualificationSeconds){Fail 'QUALIFICATION_TIMEOUT_NO_TERMINATION'}
 if($c.firstFailure -and -not $c.haltAttempted){$c.haltAttempted=$true;WriteRecord 'capture-halted.json' @{id=$c.id;scope=$c.scope;owner=$c.owner;controllerPid=$PID;childPid=$c.childPid;firstFailure=$c.firstFailure;rawKnownPrefix=$c.rawBytes;unknownOrPending=$true;noSuccessor=$true} 2048}
 $bodyReturned=$c.started -and $c.waitReturned -and $c.stdinReturned -and (InputReturned) -and (ReadersReturned)
 if(-not $c.startEntered -and $c.readers.Count -eq 0 -and (InputReturned)){$bodyReturned=$true}
 if($bodyReturned -and -not $c.processDisposeEntered){$c.processDisposeEntered=$true;try{$c.process.Dispose();$c.processDisposed=$true}catch{Fail 'ORIGINAL_PROCESS_DISPOSE_UNKNOWN'}}
 if($bodyReturned -and $c.processDisposed -and (RecordsReturned) -and -not $c.receiptAttempted){
  $c.receiptAttempted=$true;$c.qualified=($null -eq $c.firstFailure) -and @($c.readers|Where-Object {-not $_.eof -or $_.recordFailed}).Count -eq 0
  $facts=Snapshot;$facts.schema='RENDER02_CAPTURE_RECEIPT_V1';$facts.captureQualified=$c.qualified;$facts.receiptOwnCloseNotProvenByThisFile=$true;$facts.metadataFilesBeforeReceiptReturned=$true;$facts.rawAmountUnknown=$c.rawUnknown -or $c.input.pinUnknown -or $c.input.sourceUnknown -or $c.input.writeAmountUnknown
  WriteRecord ($request.id+'-receipt.json') $facts 8192
 }
 $allReturned=$bodyReturned -and $c.processDisposed -and $c.receiptAttempted -and (RecordsReturned)
 if(-not $allReturned){Start-Sleep -Milliseconds 5}
}while(-not $allReturned)
if($c.lock -and -not $c.lockCloseEntered){$c.lockCloseEntered=$true;try{$c.lock.Close();$c.lockClosed=$true}catch{Fail 'ORIGINAL_BATCH_LOCK_CLOSE_UNKNOWN'}}
if(-not $c.lockClosed){while($true){Start-Sleep -Milliseconds 500}}
$console=Snapshot;$console.schema='RENDER02_CAPTURE_CONSOLE_V1';$console.captureQualified=$c.qualified -and $null -eq $c.firstFailure;$console.allOriginalResourcesReturnedAtConsole=$true;$console.recordWriteBytesKnown=$c.recordBytes;$console.rawTextSavedBytesKnown=($c.readers|Where-Object kind -CEQ 'TEXT'|Measure-Object saved -Sum).Sum;$console.binaryArchiveSavedBytesKnown=($c.readers|Where-Object kind -CEQ 'BINARY'|Measure-Object saved -Sum).Sum;$console.recordWriteAmountUnknown=[bool]$c.recordAmountUnknown;$console.captureReceiptSha256=Digest (Join-Path $root ($request.id+'-receipt.json'));$console.externalControllerExitProofStillRequired=$true;$console.consoleBytes=0;$console.consoleForwardReserveBytes=4096;$console.proofReadBytes=$proofReadBytes;$console.batchSdkChildrenEntered=$batchSdkBefore+[int]$c.started;$console.batchTextChargedBytesKnown=[long]0;$console.batchBinaryArchiveBytesKnown=$batchBinaryBefore+[long]$console.binaryArchiveSavedBytesKnown;$console.batchAmountUnknown=[bool]($c.rawUnknown -or $c.recordAmountUnknown -or $c.input.pinUnknown -or $c.input.sourceUnknown -or $c.input.writeAmountUnknown -or @($c.readers|Where-Object savedAmountUnknown -EQ $true).Count -gt 0);$console.controlRecordAndConsoleKnown=0
for($sizing=0;$sizing -lt 8;$sizing++){
 $text=($console|ConvertTo-Json -Depth 12 -Compress)+"`n";$console.consoleBytes=[Text.UTF8Encoding]::new($false).GetByteCount($text)
 $console.controlRecordAndConsoleKnown=$c.recordBytes+$console.consoleBytes
 $console.batchTextChargedBytesKnown=$batchTextBefore+$c.textBytes+$c.recordBytes+2*$console.consoleBytes+$proofReadBytes
 if($c.recordBytes+2*$console.consoleBytes+$proofReadBytes -gt 14000 -or $console.batchTextChargedBytesKnown -gt 4194304 -or $console.batchBinaryArchiveBytesKnown -gt 16777216){Fail 'CONTROL_OR_BATCH_QUALIFIER_EXCEEDED';$console.firstFailure=$c.firstFailure;$console.captureQualified=$false}
}
$text=($console|ConvertTo-Json -Depth 12 -Compress)+"`n";$consoleBytes=[Text.UTF8Encoding]::new($false).GetByteCount($text)
if($consoleBytes -gt 8192 -or $consoleBytes -ne $console.consoleBytes){while($true){Start-Sleep -Milliseconds 500}}
[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false)
try{[Console]::Out.Write($text);[Console]::Out.Flush()}catch{while($true){Start-Sleep -Milliseconds 500}}
$global:Render02CaptureCustody.Remove($c.owner)
if($console.captureQualified){exit 0}else{exit 2}
