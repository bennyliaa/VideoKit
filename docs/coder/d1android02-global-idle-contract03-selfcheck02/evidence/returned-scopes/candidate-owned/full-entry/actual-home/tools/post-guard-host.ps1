$ErrorActionPreference='Stop'
# Narrow seven-role binding of the frozen RENDER02 capture. Original Process/pumps/lock retained.
$requestBodyReadBytes=[long]0;$requestBodyReadCalls=0
function ReadJsonExact([string]$Path,[string[]]$Keys,[int]$Max=8192){
 $raw=[IO.File]::ReadAllBytes($Path);$script:lastJsonBytes=$raw;if($Path -ceq $RequestPath){$script:requestBodyReadBytes+=[long]$raw.Length;$script:requestBodyReadCalls++};if($raw.Length -gt $Max){throw 'JSON_BOUND'}
 $doc=[Text.Json.JsonDocument]::Parse([Text.UTF8Encoding]::new($false,$true).GetString($raw));$seen=[Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
 try{CheckJsonTree $doc.RootElement 0}finally{$doc.Dispose()}
 $o=[Text.Encoding]::UTF8.GetString($raw)|ConvertFrom-Json -DateKind String
 if($Keys.Count -gt 0 -and @(Compare-Object -CaseSensitive @($o.PSObject.Properties.Name|Sort-Object) @($Keys|Sort-Object)).Count -ne 0){throw 'EXACT_SCHEMA_REQUIRED'};return $o
}
function CheckJsonTree($e,[int]$depth){
 if($depth -gt 16){throw 'JSON_DEPTH_BOUND'}
 if($e.ValueKind -eq [Text.Json.JsonValueKind]::Object){$names=[Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase);foreach($p in $e.EnumerateObject()){if(-not $names.Add($p.Name)){throw 'DUPLICATE_JSON_FIELD'};CheckJsonTree $p.Value ($depth+1)}}
 elseif($e.ValueKind -eq [Text.Json.JsonValueKind]::Array){foreach($item in $e.EnumerateArray()){CheckJsonTree $item ($depth+1)}}
}
function Digest([string]$Path){return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()}
function SameArgv($A,$B){if($A.Count -ne $B.Count){return $false};for($n=0;$n -lt $A.Count;$n++){if($A[$n] -isnot [string] -or $A[$n] -cne $B[$n]){return $false}};return $true}
function NoLinks([string]$Path){$p=if(Test-Path -LiteralPath $Path -PathType Container){[IO.DirectoryInfo]::new($Path)}else{[IO.FileInfo]::new($Path)};while($null -ne $p){if($p.Exists -and ($p.Attributes -band [IO.FileAttributes]::ReparsePoint)){throw 'NO_REPARSE_POINT'};$p=if($p -is [IO.FileInfo]){$p.Directory}else{$p.Parent}}}
function IntField($Object,[string]$Key,[long]$Max,[long]$Min=0){
 if($null -eq $Object -or $Object -isnot [pscustomobject]){return $false}
 $p=$Object.PSObject.Properties[$Key];return $null -ne $p -and ($p.Value -is [int] -or $p.Value -is [long]) -and $p.Value -ge $Min -and $p.Value -le $Max
}
function BoolField($Object,[string]$Key,[bool]$Expected){$p=$Object.PSObject.Properties[$Key];return $null -ne $p -and $p.Value -is [bool] -and $p.Value -eq $Expected}
function StringField($Object,[string]$Key){$p=$Object.PSObject.Properties[$Key];return $null -ne $p -and $p.Value -is [string]}
function StrictReceipt($p,[bool]$Fixture){
 if($p -isnot [pscustomobject]){return $false}
 if($null -eq $p.PSObject.Properties['firstFailure'] -or $null -ne $p.firstFailure){return $false}
 foreach($k in @('scopeEntry','candidate','status')){if(-not (StringField $p $k)){return $false}}
 foreach($k in @('originalResourcesReturned','workerActuallyJoined','timelyOriginalBody','lastControlledReturnSignalBeforeMarker')){if(-not (BoolField $p $k $true)){return $false}}
 foreach($k in @('completedCaseCount','expectedCaseCount')){if(-not (IntField $p $k 10 10)){return $false}}
 foreach($k in @('sourceKeepers','outputKeepers')){if(-not (IntField $p $k 0)){return $false}}
 if(-not (IntField $p 'runnerFinalizerOwnerAtReceipt' 1 1) -or -not (StringField $p 'runnerFinishReturn') -or $p.runnerFinishReturn -cne 'EXTERNAL_ORIGINAL_CAPTURE_REQUIRED'){return $false}
 if($Fixture){return (BoolField $p 'fixtureOnly' $true)}
 if(-not (StringField $p 'runId') -or -not (BoolField $p 'snapshotOverflow' $false) -or -not (BoolField $p 'scopeBudgetsSharedAcrossAllCases' $true)){return $false}
 if(-not (IntField $p 'startedNano' ([long]::MaxValue)) -or -not (IntField $p 'completedNano' ([long]::MaxValue)) -or $p.completedNano -lt $p.startedNano -or $p.completedNano-$p.startedNano -ge 60000000000){return $false}
 if($p.caseReceipts -isnot [array] -or $p.caseReceipts.Count -ne 10){return $false}
 foreach($c in $p.caseReceipts){if($c -isnot [pscustomobject] -or -not (StringField $c 'case') -or -not (BoolField $c 'caseOriginalResourcesReturned' $true)){return $false}}
 if($p.identity -isnot [pscustomobject] -or $p.meter -isnot [pscustomobject]){return $false}
 foreach($k in @('targetPackage','testPackage','processName')){if(-not (StringField $p.identity $k)){return $false}}
 foreach($pkg in @('com.videokit.d1media3.android02','com.videokit.d1media3.android02.test')){
  $x=$p.identity.PSObject.Properties[$pkg].Value
  if(-not (IntField $x 'versionCode' 1 1) -or -not (StringField $x 'versionName') -or -not (StringField $x 'signerSha256')){return $false}
 }
 if(-not (IntField $p.meter 'scopeInputReserved' 8388608) -or -not (IntField $p.meter 'scopeOutputRequested' 16777216) -or -not (IntField $p.meter 'scopeOutputAttempted' 16777216)){return $false}
 foreach($k in @('knownNativeFdActive','assetStreamActive','unknownAllocationOrClose')){if(-not (IntField $p.meter $k 0)){return $false}}
 $m=$p.caseReceipts[9]
 if($m.muxerKeeper -isnot [pscustomobject] -or $m.reopened -isnot [pscustomobject]){return $false}
 foreach($k in @('returned','eosReturned')){if(-not (BoolField $m.muxerKeeper $k $true)){return $false}}
 if(-not (IntField $m.muxerKeeper 'sampleWritesReturned' 6 6) -or -not (IntField $m 'muxReopenCalls' 1 1) -or -not (IntField $m 'muxReadyCalls' 0) -or -not (BoolField $m 'muxNativeSyncReturned' $true) -or -not (StringField $m.reopened 'actualExtractorClass')){return $false}
 return $true
}

function RuntimeSourcePreflight {
 $runtimeMeta='D:\CodexProjects\VideoKit\docs\coder\d1android02-global-idle-contract03-fix\reference\current-runtime-identity.json'
 $runtimeHelper='D:\CodexProjects\VideoKit\docs\coder\d1android02-global-idle-contract03-fix\tools\runtime_binding.py'
 if(-not (Test-Path -LiteralPath $runtimeMeta -PathType Leaf)){throw 'RUNTIME_METADATA_MISSING_PS'}
 if($policy.runtimeIdentitySha256 -cne '2593ddab8ed0a7cee369c13a145817c4365ce1847f18e0d7167db453060e5d48' -or (Digest $runtimeMeta) -cne '2593ddab8ed0a7cee369c13a145817c4365ce1847f18e0d7167db453060e5d48'){throw 'RUNTIME_METADATA_PIN_MISMATCH_PS'}
 if($policy.runtimeBindingSourceSha256 -cne '47f9d48af2d3106c6b04f67e079bd6b48b3befb4b0c25061f3a6508426e3c982' -or (Digest $runtimeHelper) -cne '47f9d48af2d3106c6b04f67e079bd6b48b3befb4b0c25061f3a6508426e3c982'){throw 'RUNTIME_BINDING_SOURCE_PIN_MISMATCH_PS'}
 $m=ReadJsonExact $runtimeMeta @() 16384
 $exe=@($m.files|Where-Object kind -CEQ 'interpreter-executable')[0]
 if($policy.outerPythonSha256 -cne $exe.sha256){throw 'RUNTIME_POLICY_PYTHON_PIN_MISMATCH_PS'}
 foreach($p in $m.files){NoLinks $p.path;if(-not (Test-Path -LiteralPath $p.path -PathType Leaf) -or (Get-Item -LiteralPath $p.path).Length -ne $p.bytes -or (Digest $p.path) -cne $p.sha256){throw ('RUNTIME_FILE_PIN_MISMATCH_PS:'+([IO.Path]::GetFileName($p.path)))}}
}

# Loaded inline in this exact candidate, before the existing SDK capture context.
$script:controllerHomeRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$script:expectedGateSourcesSha256='9cff279ddb9e60632b1422dca16af0dac4ab1922fb6b0b27c5a232055e439d72'
$admissionSource='D:/CodexProjects/VideoKit/docs/coder/d1android02-global-idle-contract03-fix/tools/admission_checks.ps1';NoLinks $admissionSource
if((Digest $admissionSource) -cne 'fc09218ed9094641a7c89b69ae4d06226f758b2909bde84dbd171c4f0edcbd8a'){throw 'ADMISSION_MODULE_SOURCE_PIN'}
. $admissionSource
function RoleSemantic([string]$Id,[string]$RawPath,[bool]$IsFixture) {
 $raw=[IO.File]::ReadAllBytes($RawPath);$text=[Text.UTF8Encoding]::new($false,$true).GetString($raw);$lines=@($text.Trim().Split("`n")|ForEach-Object {$_.TrimEnd("`r")})
 if($Id -ceq 'identity'){
  if($lines.Count -ne 7 -or $lines[0] -cne 'ANDROID02_ID_BEGIN' -or $lines[6] -cne 'ANDROID02_ID_COMPLETE' -or $lines[1] -cne 'TB138FC' -or $lines[2] -cne '31' -or $lines[3].Length -lt 8 -or $lines[4] -cne '0' -or $lines[5] -notmatch '(^|,)arm64-v8a(,|$)'){return 'IDENTITY_UNPROVEN'}
  if($lines[3] -cne $policy.globalIdleQualification.fingerprint){return 'FACT_IDENTITY_FIRMWARE_DISAGREEMENT'}
  if(-not $IsFixture -and $lines[3] -ceq 'LOCAL_FAKE_FINGERPRINT_NOT_DEVICE'){return 'FIXTURE_NOT_PRODUCTION'};return 'PASS'
 }
 if($Id -ceq 'global_idle'){
  # Invoked only after original WaitForExit, EOF/saved readers and input return;
  # current controller return remains the unchanged outer owner's obligation.
  $bodyReturnedForSemantic=if($request.id -ceq 'global_idle'){$c.waitReturned -and (ReadersReturned) -and (InputReturned) -and $null -eq $c.firstFailure}else{$true}
  $ctx=[pscustomobject]@{scope=$policy.scope;runId=$policy.runId;mode=if($IsFixture){'OFFLINE_FIXTURE'}else{'LIVE'};rawSha256=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($raw)).ToLowerInvariant();rawBytes=$raw.Length;captureBodyReturned=[bool]$bodyReturnedForSemantic;sourceSealSha256=$policy.toolCandidateSeal.sha256;planSha256=$policy.planSha256;reviewEvidenceSha256=$policy.independentReview.sha256;nowUtc=[DateTimeOffset]::UtcNow.ToString('o')}
  $decision=Get-GlobalIdleDecision $text $policy.globalIdleQualification $ctx
  if($decision.qualified -and $decision.status -ceq 'PASS'){return 'PASS'};return $decision.reason
 }
 if($Id -cin @('app_absence','test_absence')){
  $kind=if($Id -ceq 'app_absence'){'APP'}else{'TEST'}
  if($lines[0] -cne ('ANDROID02_'+$kind+'_BEGIN') -or $lines[-1] -cne ('ANDROID02_'+$kind+'_COMPLETE')){return 'PACKAGE_ABSENCE_UNPROVEN'}
  if($lines.Count -ne 2){return 'EXISTING_PACKAGE_OR_ABSENCE_UNPROVEN'};return 'PASS'
 }
 if($Id -cin @('install_app','install_test')){
  if($IsFixture){if(-not $text.StartsWith('LOCAL_PAYLOAD ')){return 'LOCAL_PAYLOAD_UNPROVEN'};$p=$text.Substring(14)|ConvertFrom-Json;$expectedPin=@($slots|Where-Object id -CEQ $Id)[0].payloadPin;if($p.fixtureOnly -ne $true -or $p.bytes -ne $expectedPin.bytes -or $p.sha256 -cne $expectedPin.sha256){return 'LOCAL_PAYLOAD_MISMATCH'};return 'PASS'}
  if($lines.Count -ne 1 -or $lines[0] -cne 'Success'){return 'INSTALL_SUCCESS_UNPROVEN'};return 'PASS'
 }
 if($Id -ceq 'scope_all'){
  $receiptMatches=[regex]::Matches($text,'(?m)^INSTRUMENTATION_RESULT: receipt=(.+)\r?$');if($receiptMatches.Count -ne 1 -or $text -cnotmatch '(?m)^INSTRUMENTATION_CODE: -1\s*$'){return 'FINAL_INSTRUMENTATION_RESULT_UNPROVEN'}
  $encoded=$receiptMatches[0].Groups[1].Value.TrimEnd("`r");if([Text.Encoding]::UTF8.GetByteCount($encoded) -gt 262144){return 'APP_RECEIPT_BOUND'};$p=$encoded|ConvertFrom-Json;if(-not (StrictReceipt $p $IsFixture)){return 'APP_REQUIRED_TYPES_BOUNDS_OR_FIRST_FAILURE'}
  if($IsFixture -and $p.fixtureOnly -ne $true){return 'FIXTURE_RECEIPT_REQUIRED'};if(-not $IsFixture -and $p.fixtureOnly){return 'FIXTURE_NOT_PRODUCTION'}
  if($p.scopeEntry -cne 'scopeAll' -or $p.candidate -cne 'D1-MEDIA3-ANDROID02-FIX02' -or $p.status -cne 'OBSERVED_ALL_SCOPE_HOST_STRUCTURE_ONLY' -or $p.completedCaseCount -ne 10 -or $p.expectedCaseCount -ne 10 -or $p.sourceKeepers -ne 0 -or $p.outputKeepers -ne 0){return 'APP_SCOPE_RESULT_UNPROVEN'}
  foreach($k in @('originalResourcesReturned','workerActuallyJoined','timelyOriginalBody','lastControlledReturnSignalBeforeMarker')){if($p.$k -isnot [bool] -or -not $p.$k){return 'APP_ORIGINAL_RETURN_OR_DEADLINE_UNPROVEN'}}
  if(-not $IsFixture){if($p.runId -cne $policy.runId -or $p.snapshotOverflow -ne $false -or @($p.caseReceipts).Count -ne 10){return 'APP_SCOPE_HISTORY_UNPROVEN'}}
  if(-not $IsFixture){
   for($i=0;$i -lt 10;$i++){if($p.caseReceipts[$i].case -cne $plan.product.caseOrder[$i] -or $p.caseReceipts[$i].caseOriginalResourcesReturned -ne $true){return 'APP_ORDERED_HISTORY_UNPROVEN'}}
   if($p.identity.targetPackage -cne 'com.videokit.d1media3.android02' -or $p.identity.testPackage -cne 'com.videokit.d1media3.android02.test' -or $p.identity.processName -cne 'com.videokit.d1media3.android02:media3'){return 'APP_REPORTED_IDENTITY_UNPROVEN'}
   foreach($pkg in @('com.videokit.d1media3.android02','com.videokit.d1media3.android02.test')){$identity=$p.identity.PSObject.Properties[$pkg].Value;if($identity.versionName -cne $plan.product.version -or $identity.signerSha256 -cne $plan.product.signerCertificateSha256){return 'APP_REPORTED_VERSION_SIGNER_UNPROVEN'}}
   if($p.meter.scopeInputReserved -gt 8388608 -or $p.meter.scopeOutputRequested -gt 16777216 -or $p.meter.scopeOutputAttempted -gt 16777216 -or $p.meter.knownNativeFdActive -ne 0 -or $p.meter.assetStreamActive -ne 0 -or $p.meter.unknownAllocationOrClose -ne 0){return 'APP_REPORTED_ACCOUNTING_UNPROVEN'}
   $mux=$p.caseReceipts[9];if($mux.muxerKeeper.returned -ne $true -or $mux.muxerKeeper.eosReturned -ne $true -or $mux.muxerKeeper.sampleWritesReturned -ne 6 -or $mux.muxReopenCalls -ne 1 -or $mux.muxReadyCalls -ne 0 -or $mux.muxNativeSyncReturned -ne $true -or $mux.reopened.actualExtractorClass -cne 'androidx.media3.extractor.mp4.FragmentedMp4Extractor'){return 'APP_REPORTED_MUX_CHAIN_UNPROVEN'}
  }
  # SDK/watcher return and app-reported originals are observations; they do NOT prove
  # the app finisher's own OS/Binder-return tail. Never issue READY/COMMIT here.
  return 'PASS_LIMITED_APP_RECEIPT_INTERNAL_FINISH_UNPROVEN'
 }
 return 'ROLE_NOT_WHITELISTED'
}


$root='D:\CodexProjects\VideoKit\docs\coder\d1android02-global-idle-contract03-fix\selfchecks\work\selfcheck02-ce9fcb60366a\full-entry\actual-home\outputs';$policyPath='D:\CodexProjects\VideoKit\docs\coder\d1android02-global-idle-contract03-fix\selfchecks\work\selfcheck02-ce9fcb60366a\full-entry\actual-home\release\capture-policy.json';$policy=ReadJsonExact $policyPath @() 65536;$script:policyBodyBytes=$script:lastJsonBytes.Length;$script:activationStartupBytes=0;$slots=@($policy.slots);$fixture=$true;$proof=ReadJsonExact 'D:\CodexProjects\VideoKit\docs\coder\d1android02-global-idle-contract03-fix\selfchecks\work\selfcheck02-ce9fcb60366a\full-entry\actual-home\outputs\pre_sdk_local_gate-completion-proof.json' @() 4096;$PredecessorProofSha=Digest 'D:\CodexProjects\VideoKit\docs\coder\d1android02-global-idle-contract03-fix\selfchecks\work\selfcheck02-ce9fcb60366a\full-entry\actual-home\outputs\pre_sdk_local_gate-completion-proof.json';$script:initialGateReceipt=ReadJsonExact 'D:\CodexProjects\VideoKit\docs\coder\d1android02-global-idle-contract03-fix\selfchecks\work\selfcheck02-ce9fcb60366a\full-entry\actual-home\outputs\gate-original-return.json' @() 16384
$cases='[{"name":"good","path":"D:\\CodexProjects\\VideoKit\\docs\\coder\\d1android02-global-idle-contract03-fix\\selfchecks\\work\\selfcheck02-ce9fcb60366a\\full-entry\\good-admission.json"},{"name":"post-reset","path":"D:\\CodexProjects\\VideoKit\\docs\\coder\\d1android02-global-idle-contract03-fix\\selfchecks\\work\\selfcheck02-ce9fcb60366a\\full-entry\\post-reset-admission.json"},{"name":"post-duplicate","path":"D:\\CodexProjects\\VideoKit\\docs\\coder\\d1android02-global-idle-contract03-fix\\selfchecks\\work\\selfcheck02-ce9fcb60366a\\full-entry\\post-duplicate-admission.json"},{"name":"receiver-reset","path":"D:\\CodexProjects\\VideoKit\\docs\\coder\\d1android02-global-idle-contract03-fix\\selfchecks\\work\\selfcheck02-ce9fcb60366a\\full-entry\\receiver-reset-admission.json"},{"name":"wrong-event","path":"D:\\CodexProjects\\VideoKit\\docs\\coder\\d1android02-global-idle-contract03-fix\\selfchecks\\work\\selfcheck02-ce9fcb60366a\\full-entry\\wrong-event-admission.json"},{"name":"wrong-source","path":"D:\\CodexProjects\\VideoKit\\docs\\coder\\d1android02-global-idle-contract03-fix\\selfchecks\\work\\selfcheck02-ce9fcb60366a\\full-entry\\wrong-source-admission.json"},{"name":"wrong-holder","path":"D:\\CodexProjects\\VideoKit\\docs\\coder\\d1android02-global-idle-contract03-fix\\selfchecks\\work\\selfcheck02-ce9fcb60366a\\full-entry\\wrong-holder-admission.json"},{"name":"wrong-mode","path":"D:\\CodexProjects\\VideoKit\\docs\\coder\\d1android02-global-idle-contract03-fix\\selfchecks\\work\\selfcheck02-ce9fcb60366a\\full-entry\\wrong-mode-admission.json"},{"name":"bool-post","path":"D:\\CodexProjects\\VideoKit\\docs\\coder\\d1android02-global-idle-contract03-fix\\selfchecks\\work\\selfcheck02-ce9fcb60366a\\full-entry\\bool-post-admission.json"},{"name":"extra","path":"D:\\CodexProjects\\VideoKit\\docs\\coder\\d1android02-global-idle-contract03-fix\\selfchecks\\work\\selfcheck02-ce9fcb60366a\\full-entry\\extra-admission.json"}]'|ConvertFrom-Json;$all=@();foreach($case in $cases){$ad=ReadJsonExact $case.path @() 8192;try{$n=CheckRunnerMaterialization $ad $policy $proof $true;$all+=@{name=$case.name;accepted=$true;readBytes=$n}}catch{$all+=@{name=$case.name;accepted=$false;error=$_.Exception.Message}}}
$final=@();foreach($name in @('good','proof-window','gate-window','whole-window','expired','future-proof','bool-tick')){$ad=ReadJsonExact 'D:\CodexProjects\VideoKit\docs\coder\d1android02-global-idle-contract03-fix\selfchecks\work\selfcheck02-ce9fcb60366a\full-entry\actual-home\outputs\identity-owner-admission.json' @() 8192;$now=[Environment]::TickCount64;$ad.runnerHandoff.scopeStartTick=$now-1000;$ad.runnerHandoff.initialProofStartTick=$now-500;$ad.runnerHandoff.permitExpiresUtc=[DateTimeOffset]::UtcNow.AddSeconds(10).ToString('o');$idx=0;switch($name){'proof-window'{$ad.runnerHandoff.scopeStartTick=$now-15000;$ad.runnerHandoff.initialProofStartTick=$now-10100};'gate-window'{$ad.runnerHandoff.scopeStartTick=$now-30100};'whole-window'{$ad.runnerHandoff.scopeStartTick=$now-600100;$idx=6};'expired'{$ad.runnerHandoff.permitExpiresUtc=[DateTimeOffset]::UtcNow.AddSeconds(-1).ToString('o')};'future-proof'{$ad.runnerHandoff.initialProofStartTick=$now+1000};'bool-tick'{$ad.runnerHandoff.initialProofStartTick=$true}};try{RunnerFinalStartGate $ad $policy $ad.runnerHandoff.scopeStartTick $idx $true;$final+=@{name=$name;accepted=$true}}catch{$final+=@{name=$name;accepted=$false;error=$_.Exception.Message}}};@{post=$all;finalStart=$final}|ConvertTo-Json -Depth 8 -Compress
