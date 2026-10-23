[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$RequestPath,[string]$PredecessorProofSha='ABSENT',[string]$OwnerAdmissionSha='ABSENT')
if(@($PSBoundParameters.Keys|Where-Object {$_ -cnotin @('RequestPath','PredecessorProofSha','OwnerAdmissionSha')}).Count -ne 0){throw 'EXTRA_ENTRY_ARGUMENT_REJECTED'}
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

$policyPath=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../release/capture-policy.json'));$policy=ReadJsonExact $policyPath @() 65536;$script:policyBodyBytes=$script:lastJsonBytes.Length;$script:activationStartupBytes=0
# PREPARATION returns before request/product/tool/5037/claim access or any capture context.
if($policy.mode -ceq 'PREPARATION_ONLY'){throw 'PREPARATION_ONLY_NO_EXECUTION_AUTHORIZATION'}
$localAdmissionTimer=[Diagnostics.Stopwatch]::StartNew()
if($policy.schema -cne 'ANDROID02_CAPTURE_POLICY_V1' -or $policy.entrySha256 -cne (Digest $PSCommandPath)){throw 'ENTRY_POLICY_PIN'}
if($policy.mode -cnotin @('PRODUCTION','OFFLINE_FIXTURE')){throw 'EXACT_POLICY_MODE'}
RuntimeSourcePreflight
$planPath=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../reference/exact-seven-role-plan.json'))
if((Digest $planPath) -cne 'b2802b659ef1b7d1f99938b36248373da41dc0e0faffffc9da001d45a4de26c8' -or $policy.planSha256 -cne 'b2802b659ef1b7d1f99938b36248373da41dc0e0faffffc9da001d45a4de26c8'){throw 'EXACT_SEVEN_PLAN_PIN'}
$plan=ReadJsonExact $planPath @() 32768
if($policy.productSealSha256 -cne $plan.product.sealSha256 -or (Digest $plan.product.sealPath) -cne $plan.product.sealSha256){throw 'FIX02_PRODUCT_SEAL_PIN'}
$snapshotRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))+[IO.Path]::DirectorySeparatorChar;$requestFull=[IO.Path]::GetFullPath($RequestPath);if(-not $requestFull.StartsWith($snapshotRoot,[StringComparison]::OrdinalIgnoreCase) -or [IO.Path]::GetExtension($requestFull) -cne '.json'){throw 'EXACT_SNAPSHOT_REQUEST_PATH'};NoLinks $requestFull
$request=ReadJsonExact $RequestPath @('schema','id','policySha256','scope','evidenceRoot','argv','maxTextBytes','maxBinaryBytes','qualificationSeconds')
foreach($k in @('schema','id','policySha256','scope','evidenceRoot')){if($request.$k -isnot [string]){throw 'EXACT_REQUEST_TYPES'}}
foreach($k in @('maxTextBytes','maxBinaryBytes')){if($request.$k -isnot [long] -and $request.$k -isnot [int]){throw 'EXACT_REQUEST_TYPES'}}
if($request.argv -isnot [array] -or ($request.qualificationSeconds -isnot [long] -and $request.qualificationSeconds -isnot [int] -and $request.qualificationSeconds -isnot [double]) -or [double]::IsNaN([double]$request.qualificationSeconds) -or [double]::IsInfinity([double]$request.qualificationSeconds)){throw 'EXACT_REQUEST_TYPES'}
if($request.schema -cne 'ANDROID02_CAPTURE_REQUEST_V1' -or $request.policySha256 -cne (Digest $policyPath)){throw 'REQUEST_POLICY_PIN'}
$root=[IO.Path]::GetFullPath([string]$policy.evidenceRoot);NoLinks $root
if($request.evidenceRoot -cne $policy.evidenceRoot -or $request.scope -cne $policy.scope -or $policy.scope -cnotmatch '^[a-f0-9]{64}$'){throw 'EXACT_SCOPE_ROOT'}
$fixture=$policy.mode -ceq 'OFFLINE_FIXTURE';$inputPin=$null;$payloadPin=$null;$slots=@();$previous=$null
if($fixture){
 $prefix='D:\CodexProjects\VideoKit\docs\coder\d1android02-global-idle-contract03-fix\selfchecks\work\';$review='D:\CodexProjects\VideoKit\docs\tester\D1_GLOBAL_IDLE_CONTRACT03_FIX_REVIEW_EVIDENCE\fixtures\'
 if(-not $root.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase) -and -not $root.StartsWith($review,[StringComparison]::OrdinalIgnoreCase)){throw 'FIXTURE_ROOT_ONLY'}
 $slots=@($policy.slots);if($slots.Count -lt 1 -or $slots.Count -gt 7){throw 'EXACT_SEVEN_ROLES_MAX'}
 for($i=0;$i -lt $slots.Count;$i++){
  $s=$slots[$i];if($s.id -cne $plan.steps[$i].id -or $s.argv.Count -ne 8 -or $s.argv[0] -cne 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -or -not (SameArgv @($s.argv[1..4]) @('-I','-X','utf8','-B')) -or $s.argv[5] -cne 'D:/CodexProjects/VideoKit/docs/coder/d1android02-global-idle-contract03-fix/selfchecks/capture_fixture.py' -or $s.argv[6] -cnotin @('identity','global_idle','global_busy','global_unknown','app_absence','test_absence','app_present','payload_app','payload_test','instrument','late','overrun','stderr','invalid_utf8','nonzero') -or $s.argv[7] -cne (Join-Path $root 'fixture-gate')){throw 'EXACT_LOCAL_PRODUCER_ONLY'}
  if($s.maxTextBytes -lt 1 -or $s.maxTextBytes -gt $plan.steps[$i].maxTextBytes -or $s.maxBinaryBytes -ne 0 -or $s.qualificationSeconds -le 0 -or $s.qualificationSeconds -gt $plan.steps[$i].qualificationSeconds){throw 'FIXTURE_ROLE_BOUND_ONLY'}
  if((Digest $s.argv[5]) -cne 'e3cca23ab4f1584da7bc411282751f75d14d225e0dfdedeb739f92eda5cf5311' -or $policy.fixtureScriptSha256 -cne 'e3cca23ab4f1584da7bc411282751f75d14d225e0dfdedeb739f92eda5cf5311'){throw 'FIXTURE_SCRIPT_PIN'}
 }
 if($policy.fixtureFault -cnotin @('NONE','READ_FAULT_ONCE','WRITE_FAULT_ONCE','STDIN_WRITE_FAULT_ONCE','STDIN_CLOSE_GATE','CLOSE_GATE','PRESTART_KNOWN_REJECT')){throw 'EXACT_FIXTURE_FAULT'}
}else{
 if($policy.planId -cnotmatch '^[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{12}$' -or $policy.planId -cin @($plan.forbiddenOldPlanIds) -or $policy.runId -cnotmatch '^D1MA02-[A-Z0-9_-]{1,32}$'){throw 'FRESH_SCOPE_REQUIRED'}
 if($root -cne ('D:\CodexProjects\VideoKit\docs\tester\D1_ANDROID02_CAPTURE_EXECUTION\'+$policy.planId+'\outputs')){throw 'NEW_EXACT_EXECUTION_ROOT'}
 foreach($k in @('authorization','independentReview','toolCandidateSeal','freshRouteProof')){if($null -eq $policy.$k -or $policy.$k.sha256 -cnotmatch '^[a-f0-9]{64}$' -or (Digest $policy.$k.path) -cne $policy.$k.sha256){throw 'NEW_ACTIVATION_REVIEW_ROUTE_REQUIRED'}}
 $activation=ReadJsonExact $policy.authorization.path @('schema','scope','planId','runId','entrySha256','planSha256','toolCandidateSealSha256','productSealSha256','reviewSha256','toolSha256','evidenceRoot','wholeWallSeconds','localProofSeconds','outerSeconds','freshRouteProofSha256','initialPredecessorProofSha256','outerOwnerSha256','outerPythonSha256','runtimeIdentitySha256','runtimeBindingSourceSha256','approvedForExecution','runnerPermitSha256','runnerSourceSha256','runnerApprovalSha256','routeBackend');$script:activationStartupBytes=$script:lastJsonBytes.Length
 if($activation.routeBackend -cne 'WIN32_OWNER_PID_V1' -or $policy.routeBackend -cne $activation.routeBackend){throw 'ACTIVATION_BACKEND_BINDING'}
 if($activation.runtimeIdentitySha256 -cne $policy.runtimeIdentitySha256 -or $activation.runtimeBindingSourceSha256 -cne $policy.runtimeBindingSourceSha256){throw 'ACTIVATION_RUNTIME_BINDING_PIN'}
 if($activation.outerOwnerSha256 -cne $policy.outerOwnerSha256 -or $activation.outerPythonSha256 -cne $policy.outerPythonSha256){throw 'ACTIVATION_OWNER_SOURCE_PIN'}
 if($activation.schema -cne 'ANDROID02_CAPTURE_ACTIVATION_V1' -or $activation.approvedForExecution -isnot [bool] -or -not $activation.approvedForExecution -or $activation.scope -cne $policy.scope -or $activation.planId -cne $policy.planId -or $activation.runId -cne $policy.runId -or $activation.entrySha256 -cne $policy.entrySha256 -or $activation.planSha256 -cne (Digest $planPath) -or $activation.toolCandidateSealSha256 -cne $policy.toolCandidateSeal.sha256 -or $activation.productSealSha256 -cne $plan.product.sealSha256 -or $activation.reviewSha256 -cne $policy.independentReview.sha256 -or $activation.toolSha256 -cne $plan.sdkFiles[0].sha256 -or $activation.evidenceRoot -cne $root){throw 'EXACT_NEW_ACTIVATION_BINDING'}
 # These are approved NEW scope/outer/local-proof ceilings, not the 240s sum or a kill permit.
 if(-not (IntField $activation 'wholeWallSeconds' 600 1) -or -not (IntField $activation 'localProofSeconds' 30 1) -or -not (IntField $activation 'outerSeconds' 600 1)){throw 'STRICT_ACTIVATION_WALL_TYPES'}
 if($activation.wholeWallSeconds -lt 1 -or $activation.wholeWallSeconds -gt 600 -or $activation.localProofSeconds -lt 1 -or $activation.localProofSeconds -gt 30 -or $activation.outerSeconds -lt 1 -or $activation.outerSeconds -gt 600){throw 'REVIEWED_WALL_BOUNDS_REQUIRED'}
 if($activation.wholeWallSeconds -ne 600 -or $activation.outerSeconds -ne 120 -or $activation.localProofSeconds -ne 10){throw 'EXACT_PRODUCTION_600_120_10'}
 if($activation.freshRouteProofSha256 -cne $policy.freshRouteProof.sha256){throw 'FRESH_ROUTE_AUTHORIZATION_BINDING'}
 $route=ReadJsonExact $policy.freshRouteProof.path @('scope','planId','checkedAtUtc','serverPid','serverCreationUtc','serverImage','serverFileSha256','routingOverrides','toolSha256','sourceContractSha256','claimHeldExclusive','claimScope','originalCheckerReturned','gateGeneration','kind','sourceSha256','routeBackend','queryStats') 16384;
 if($route.routeBackend -cne $policy.routeBackend){throw 'FRESH_ROUTE_BACKEND'};CheckRouteStats $route.queryStats $false
 $contract=Join-Path $PSScriptRoot '../reference/route-backend-contract.json'
 if($route.scope -cne $policy.scope -or $route.planId -cne $policy.planId -or $route.sourceContractSha256 -cne (Digest $contract) -or $route.toolSha256 -cne $plan.sdkFiles[0].sha256 -or $route.serverFileSha256 -cne $plan.sdkFiles[0].sha256 -or [IO.Path]::GetFullPath($route.serverImage) -cne [IO.Path]::GetFullPath($plan.sdkFiles[0].path) -or $route.serverPid -le 0 -or $route.claimHeldExclusive -ne $true -or $route.claimScope -cne $policy.scope -or $route.originalCheckerReturned -ne $true -or @($route.routingOverrides.PSObject.Properties).Count -ne 0){throw 'EXISTING_FRESH_ROUTE_CLAIM_UNPROVEN'}
 $checked=[DateTimeOffset]::Parse($route.checkedAtUtc);$created=[DateTimeOffset]::Parse($route.serverCreationUtc);$age=([DateTimeOffset]::UtcNow-$checked).TotalSeconds;if($age -lt 0 -or $age -ge $activation.wholeWallSeconds -or $created -gt $checked){throw 'FRESH_ROUTE_TIME_UNPROVEN'}
 foreach($key in @('ADB_SERVER_SOCKET','ANDROID_ADB_SERVER_PORT','ADB_SERVER_PORT','ANDROID_ADB_SERVER_ADDRESS','ADB_VENDOR_KEYS','ANDROID_SERIAL','ADB_SERVER_ADDRESS')){if($null -ne [Environment]::GetEnvironmentVariable($key)){throw 'SDK_ROUTING_OVERRIDE_REJECTED'}}
 foreach($pin in $plan.sdkFiles){NoLinks $pin.path;if((Digest $pin.path) -cne $pin.sha256){throw 'EXACT_EXISTING_SDK_FILE_PIN'}}
 $scopeData=$policy.planId+'|'+$policy.entrySha256+'|'+$plan.product.sealSha256+'|'+(Digest $planPath)+'|'+$policy.runId
 $scopeHash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($scopeData))).ToLowerInvariant();if($policy.scope -cne $scopeHash){throw 'SCOPE_SOURCE_BINDING'}
 foreach($s in $plan.steps){$roleArgv=@($s.argv|ForEach-Object {if($_ -ceq '@RUN_ID@'){$policy.runId}else{$_}});$slots+=@{id=$s.id;argv=$roleArgv;maxTextBytes=$s.maxTextBytes;maxBinaryBytes=0;qualificationSeconds=$s.qualificationSeconds}}
}
$index=-1;for($i=0;$i -lt $slots.Count;$i++){if($slots[$i].id -ceq $request.id){if($index -ge 0){throw 'DUPLICATE_SLOT'};$index=$i}}
if($index -lt 0){throw 'EXACT_SEVEN_REQUEST_ONLY'};$slot=$slots[$index];if($index -gt 0){$previous=$slots[$index-1].id}
if(-not (SameArgv @($request.argv) @($slot.argv)) -or $request.maxTextBytes -ne $slot.maxTextBytes -or $request.maxBinaryBytes -ne 0 -or $request.qualificationSeconds -ne $slot.qualificationSeconds){throw 'EXACT_ARGV_CAP_TIME'}
if($request.maxTextBytes -lt 1 -or $request.maxTextBytes -gt 1048576 -or $request.qualificationSeconds -le 0 -or $request.qualificationSeconds -gt 90){throw 'FINITE_QUALIFICATION'}
if((Digest $request.argv[0]) -cne $policy.toolSha256){throw 'ORIGINAL_TOOL_PIN'}
$commandBytes=[Text.Encoding]::UTF8.GetByteCount(($request.argv|ConvertTo-Json -Compress));if($commandBytes -gt 4096){throw 'COMMAND_BOUND'}
if($fixture -and $slot.payloadPin){$payloadPin=$slot.payloadPin;$inputPin=$payloadPin;if([IO.Path]::GetFullPath($payloadPin.path) -cne (Join-Path $root ($request.id+'-fixture-input.bin')) -or $payloadPin.bytes -lt 1 -or $payloadPin.bytes -gt 65536 -or $payloadPin.sha256 -cnotmatch '^[a-f0-9]{64}$'){throw 'EXACT_BOUNDED_FIXTURE_PAYLOAD'}}
if(-not $fixture -and $request.id -ceq 'install_app'){$payloadPin=$plan.product.app};if(-not $fixture -and $request.id -ceq 'install_test'){$payloadPin=$plan.product.test}
if(-not (Test-Path -LiteralPath $root -PathType Container)){throw 'REVIEWED_OUTPUT_PARENT_REQUIRED'}
if($global:Android02CaptureCustody -and $global:Android02CaptureCustody.Count -ne 0){throw 'ORIGINAL_CONTEXT_STILL_OWNED'}
# The pinned original outer owner writes and CLOSES this admission before Popen.
# It vouches for the previous proof writer AFTER join; proof files alone never do.
$ownerPath='D:\CodexProjects\VideoKit\docs\coder\d1android02-global-idle-contract03-fix\tools\outer_owner.py'
if((Digest $ownerPath) -cne '89a9e323262875677b0008cc01ebe7f91b5c340d35e64790c740834b6474ffba' -or $policy.outerOwnerSha256 -cne '89a9e323262875677b0008cc01ebe7f91b5c340d35e64790c740834b6474ffba' -or (Digest 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe') -cne $policy.outerPythonSha256){throw 'EXACT_OUTER_OWNER_SOURCE_PIN'}
$admissionPath=Join-Path $root ($request.id+'-owner-admission.json');NoLinks $admissionPath
if($OwnerAdmissionSha -cnotmatch '^[a-f0-9]{64}$' -or (Digest $admissionPath) -cne $OwnerAdmissionSha){throw 'EXACT_OWNER_ADMISSION_REQUIRED'}
$ad=ReadJsonExact $admissionPath @('schema','id','scope','entrySha256','ownerSha256','requestSha256','predecessorProofSha256','previousProofWriterReturned','previousProofWriterTimely','requestWriteBytes','admissionWriteBytes','ownerPid','proofSeconds','outerSeconds','gateHandoff','runnerHandoff') 4096
if($ad.schema -cne 'ANDROID02_OWNER_ADMISSION_V1' -or $ad.id -cne $request.id -or $ad.scope -cne $policy.scope -or $ad.entrySha256 -cne $policy.entrySha256 -or $ad.ownerSha256 -cne '89a9e323262875677b0008cc01ebe7f91b5c340d35e64790c740834b6474ffba' -or $ad.requestSha256 -cne (Digest $RequestPath) -or $ad.predecessorProofSha256 -cne $PredecessorProofSha -or -not (BoolField $ad 'previousProofWriterReturned' $true) -or -not (BoolField $ad 'previousProofWriterTimely' $true) -or -not (IntField $ad 'ownerPid' ([int]::MaxValue) 1) -or -not (IntField $ad 'requestWriteBytes' 8192 1) -or -not (IntField $ad 'admissionWriteBytes' 4096 1) -or $ad.requestWriteBytes -ne (Get-Item -LiteralPath $RequestPath).Length -or $ad.admissionWriteBytes -ne (Get-Item -LiteralPath $admissionPath).Length){throw 'OWNER_REQUEST_WRITER_BINDING'}
if(-not $fixture -and ($ad.proofSeconds -ne $activation.localProofSeconds -or $ad.outerSeconds -ne $activation.outerSeconds)){throw 'OWNER_ACTUAL_WALL_BINDING'}
$ownerCurrentWriteCost=[long]$ad.requestWriteBytes+[long]$ad.admissionWriteBytes
$ownerCurrentReadCost=[long]$ad.admissionWriteBytes+[long]$requestBodyReadBytes

$batchSdkBefore=0;$batchTextBefore=[long]0;$batchBinaryBefore=[long]0;$proofReadBytes=0
$groups=@{preflight=[long]0;install=[long]0;instrument=[long]0;control=[long]0;payload=[long]0;command=[long]0};$scopeStartTick=[Environment]::TickCount64
if($true){
 $proofId=if($previous){$previous}else{'pre_sdk_local_gate'};$proofPath=Join-Path $root ($proofId+'-completion-proof.json')
 if($PredecessorProofSha -cnotmatch '^[a-f0-9]{64}$' -or (Digest $proofPath) -cne $PredecessorProofSha){throw 'ORIGINAL_PREDECESSOR_PROOF_REQUIRED'}
 $proof=ReadJsonExact $proofPath @('schema','id','nextId','scope','controllerPid','controllerExited','toolStreamsReturned','originalResourcesReturnedAtConsole','captureQualifiedAtConsole','approvedForNext','captureReceiptSha256','semanticDependency','dependencyAccepted','batchSdkChildrenEntered','batchTextChargedBytesKnown','batchBinaryArchiveBytesKnown','batchAmountUnknown','batchGroups','outerReturnSha256','scopeStartTick','outerDelta','proofWriteBytes','candidateOnlyWriterCloseNotProven') 4096;$proofReadBytes=(Get-Item -LiteralPath $proofPath).Length
 if($proof.schema -cne 'ANDROID02_CAPTURE_COMPLETION_PROOF_V1' -or $proof.id -cne $proofId -or $proof.nextId -cne $request.id -or $proof.scope -cne $policy.scope){throw 'ORIGINAL_PREDECESSOR_IDENTITY'}
 foreach($k in @('controllerExited','toolStreamsReturned','originalResourcesReturnedAtConsole','captureQualifiedAtConsole','approvedForNext','dependencyAccepted')){if($proof.$k -isnot [bool] -or -not $proof.$k){throw 'ORIGINAL_PREDECESSOR_UNRETURNED_OR_UNAPPROVED'}}
 foreach($k in @('batchSdkChildrenEntered','batchTextChargedBytesKnown','batchBinaryArchiveBytesKnown','scopeStartTick')){if(($proof.$k -isnot [long] -and $proof.$k -isnot [int]) -or $proof.$k -lt 0){throw 'EXACT_EXTERNAL_ACCOUNTING'}}
 if($proof.batchAmountUnknown -isnot [bool] -or $proof.batchAmountUnknown -or $proof.batchSdkChildrenEntered -ne $index -or $proof.batchBinaryArchiveBytesKnown -ne 0){throw 'NO_SCOPE_CONSUMPTION_RESET'}
 foreach($k in @('preflight','install','instrument','control','payload','command')){if(($proof.batchGroups.$k -isnot [long] -and $proof.batchGroups.$k -isnot [int]) -or $proof.batchGroups.$k -lt 0){throw 'EXACT_GROUP_ACCOUNTING'};$groups[$k]=[long]$proof.batchGroups.$k}
 if([long]$groups.preflight+[long]$groups.install+[long]$groups.instrument+[long]$groups.control -ne [long]$proof.batchTextChargedBytesKnown){throw 'EXACT_AGGREGATE_GROUP_SUM'}
 if(-not $previous){$proofReadBytes+=CheckInitialGate $proof $proofPath $ad $policy $fixture;$ownerCurrentWriteCost+=[long]$ad.gateHandoff.receiverControlBytes;$proofReadBytes+=CheckRunnerMaterialization $ad $policy $proof $fixture;$ownerCurrentWriteCost+=$script:runnerPostControl}
 if($ad.gateHandoff.scopeStartTick -ne $proof.scopeStartTick -or $ad.gateHandoff.ownerPid -ne $ad.ownerPid){throw 'GATE_CLOCK_OR_HOLDER_RESET'}
 $batchSdkBefore=$proof.batchSdkChildrenEntered;$batchTextBefore=[long]$proof.batchTextChargedBytesKnown;$scopeStartTick=[long]$proof.scopeStartTick
 if($previous){
  $receiptPath=Join-Path $root ($previous+'-receipt.json');$prior=ReadJsonExact $receiptPath @() 16384;$nativePath=Join-Path $root ($previous+'-outer-return.json');$native=ReadJsonExact $nativePath @() 16384;$proofReadBytes+=(Get-Item -LiteralPath $nativePath).Length
  if($proof.captureReceiptSha256 -cne (Digest $receiptPath) -or $proof.controllerPid -ne $prior.controllerPid -or $prior.captureQualified -ne $true -or $prior.rawAmountUnknown -or $prior.bindings.entrySha256 -cne $policy.entrySha256 -or $prior.bindings.planSha256 -cne (Digest $planPath) -or $prior.bindings.productSealSha256 -cne $plan.product.sealSha256){throw 'ORIGINAL_PREDECESSOR_RECEIPT_BINDING'}
  if($proof.semanticDependency -cne ($previous+'_ACTUAL_RETURN_AND_SEMANTIC_PASS')){throw 'EXACT_SEMANTIC_DEPENDENCY'}
  foreach($k in @('originalControllerWaitReturned','sameOriginalPipeReadersJoined','outerStreamsClosed','originalWindowsProcessHandleCloseReturned')){if($native.$k -isnot [bool] -or -not $native.$k){throw 'EXACT_OUTER_RETURN_TYPES'}}
  if((Digest $nativePath) -cne $proof.outerReturnSha256 -or $native.controllerPid -ne $prior.controllerPid -or $native.exitCode -ne 0 -or $native.originalControllerWaitReturned -ne $true -or $native.sameOriginalPipeReadersJoined -ne $true -or $native.outerStreamsClosed -ne $true -or $native.originalWindowsProcessHandleCloseReturned -ne $true -or $native.amountUnknown -or $native.scope -cne $policy.scope -or $native.id -cne $previous -or $native.sourceEntrySha256 -cne $policy.entrySha256 -or $native.requestSha256 -cne $prior.bindings.requestSha256){throw 'EXACT_OUTER_ORIGINAL_RETURN_REQUIRED'}
  if((Digest (Join-Path $root ($previous+'-console.bin'))) -cne $native.stdoutSha256 -or (Digest (Join-Path $root ($previous+'-controller-stderr.bin'))) -cne $native.stderrSha256){throw 'OUTER_CAPTURE_DIGEST_BINDING'}
  $co=ReadJsonExact (Join-Path $root ($previous+'-console.bin')) @() 16384;if($co.controllerPid -ne $prior.controllerPid -or $co.captureReceiptSha256 -cne $proof.captureReceiptSha256 -or $co.allOriginalResourcesReturnedAtConsole -ne $true -or $co.captureQualified -ne $true -or $co.batchAmountUnknown -or $co.batchSdkChildrenEntered -ne $batchSdkBefore -or $co.scopeStartTick -ne $scopeStartTick){throw 'OUTER_CONSOLE_ORIGINAL_BINDING'}
  # Early console remains the immutable BASE, never the complete later ledger.
  $d=$proof.outerDelta
  if(-not (BoolField $proof 'candidateOnlyWriterCloseNotProven' $true) -or -not (BoolField $native 'amountUnknown' $false)){throw 'OUTER_DELTA_UNKNOWN_OR_SELF_CERTIFIED'}
  foreach($k in @('nativeWriteBytes','proofWriteBytes','additionalForwardBytes')){if(-not (IntField $d $k 1048576)){throw 'EXACT_OUTER_DELTA_INTEGER'}}
  if(-not (IntField $proof 'proofWriteBytes' 4096 1) -or $proof.proofWriteBytes -ne (Get-Item -LiteralPath $proofPath).Length -or $d.proofWriteBytes -ne $proof.proofWriteBytes -or $d.nativeWriteBytes -ne (Get-Item -LiteralPath $nativePath).Length -or $d.additionalForwardBytes -ne 0 -or $d.sourceOwnerSha256 -cne '89a9e323262875677b0008cc01ebe7f91b5c340d35e64790c740834b6474ffba' -or $native.sourceOwnerSha256 -cne '89a9e323262875677b0008cc01ebe7f91b5c340d35e64790c740834b6474ffba' -or $d.baseConsoleSha256 -cne (Digest (Join-Path $root ($previous+'-console.bin'))) -or $native.ownerPid -ne $ad.ownerPid -or -not (BoolField $native 'outerTimely' $true)){throw 'ORIGINAL_OUTER_DELTA_SOURCE_BYTES'}
  $eventData=$policy.scope+'|'+$previous+'|'+$prior.bindings.requestSha256+'|'+$proof.captureReceiptSha256+'|'+$proof.outerReturnSha256
  $eventHash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($eventData))).ToLowerInvariant()
  if($d.eventId -cne $eventHash){throw 'EXACT_ONCE_DELTA_EVENT_BINDING'}
  $delta=[long]$d.nativeWriteBytes+[long]$d.proofWriteBytes
  if($co.batchTextChargedBytesKnown+$delta -ne $batchTextBefore){throw 'OUTER_DELTA_RESET_OR_DUPLICATE'}
  foreach($k in @('preflight','install','instrument','control','payload','command')){
   $expected=[long]$co.batchGroups.$k;if($k -ceq 'control'){$expected+=$delta}
   if($expected -ne $groups[$k]){throw 'EXACT_BASE_PLUS_DELTA_REQUIRED'}
  }

  foreach($reader in $prior.readers){if($reader.sha256 -cnotmatch '^[a-f0-9]{64}$' -or (Digest (Join-Path $root ($previous+'-'+$reader.role+'.bin'))) -cne $reader.sha256 -or $reader.rawBytes -ne $reader.savedBytes -or -not $reader.eof -or -not $reader.fileCloseReturned -or -not $reader.pipeCloseReturned){throw 'PREDECESSOR_FULL_RAW_DIGEST_AND_RETURN_REQUIRED'}}
  $expectedOuter=@('C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe','-NoProfile','-NonInteractive','-File',[string]$prior.bindings.entryPath,'-RequestPath',[string]$prior.bindings.requestPath,'-PredecessorProofSha',[string]$prior.bindings.predecessorProofSha,'-OwnerAdmissionSha',[string]$prior.bindings.ownerAdmissionSha)
  if(-not (SameArgv @($native.argv) $expectedOuter)){throw 'EXACT_ORIGINAL_OUTER_ARGV_REQUIRED'}
  $sem=RoleSemantic $previous (Join-Path $root ($previous+'-stdout.bin')) $fixture;if($sem -cne 'PASS'){throw 'PREDECESSOR_RAW_SEMANTIC_NOT_PASS'}
 }
}
if(-not $fixture -and $index -eq 0 -and $PredecessorProofSha -cne $activation.initialPredecessorProofSha256){throw 'INITIAL_ORIGINAL_GATE_AUTHORIZATION_BINDING'}
$wholeCap=if($fixture){600}else{$activation.wholeWallSeconds};if($true){$age=[Environment]::TickCount64-$scopeStartTick;if($age -lt 0 -or $age -ge 1000*$wholeCap){throw 'SCOPE_WALL_NOT_FRESH_STOP_BEFORE_CHILD'}}
$groups.control+=$ownerCurrentWriteCost;$batchTextBefore+=$ownerCurrentWriteCost;$proofReadBytes+=$ownerCurrentReadCost
$group=[string]$plan.steps[$index].group;$groupCap=if($group -ceq 'preflight'){1048576}elseif($group -ceq 'install'){131072}else{1048576}
$payloadCost=if($payloadPin){[long]$payloadPin.bytes}else{[long]0}
if($batchSdkBefore+1 -gt 7 -or $groups[$group]+$request.maxTextBytes -gt $groupCap -or $groups.control+65536 -gt 1048576 -or $groups.payload+$payloadCost -gt 7629605 -or $groups.command+$commandBytes -gt 28672 -or $batchTextBefore+$request.maxTextBytes+65536 -gt 3276800){throw 'WHOLE_SEVEN_ROLE_BUDGET_BEFORE_CHILD'}
if(Test-Path -LiteralPath (Join-Path $root 'capture-halted.json')){throw 'BATCH_HALTED_NO_REENTRY'}
if(Test-Path -LiteralPath (Join-Path $root ($request.id+'-entered.json'))){throw 'REQUEST_ALREADY_ENTERED_NO_REPLAY'}
$lockPath=Join-Path $root '.capture.lock';NoLinks $lockPath

$c=@{id=$request.id;semanticChecked=$false;semantic='NOT_OBSERVED';scopeStartTick=$scopeStartTick;bindings=@{entrySha256=$policy.entrySha256;planSha256=(Digest $planPath);policySha256=$request.policySha256;productSealSha256=$plan.product.sealSha256;requestSha256=(Digest $RequestPath);entryPath=$PSCommandPath;requestPath=[IO.Path]::GetFullPath($RequestPath);predecessorProofSha=$PredecessorProofSha;ownerAdmissionSha=$OwnerAdmissionSha;outerOwnerSha256=$policy.outerOwnerSha256;runtimeIdentitySha256=$policy.runtimeIdentitySha256;runtimeBindingSourceSha256=$policy.runtimeBindingSourceSha256;producerKind=if($fixture){'OFFLINE_PYTHON_NOT_SDK'}else{'EXACT_ADB'}};scope=$request.scope;owner=[Guid]::NewGuid().ToString();controllerPid=$PID;process=$null;processCreateEntered=$false;processCreateReturned=$false;processNeverCreated=$false;processDisposeCalls=0;startReturned=$false;startReturnedValue=$null;lockOpenEntered=$false;lockOpenReturned=$false;lockOpenUnknown=$false;lockNeverCreated=$false;noStartResourcesReturned=$false;stdinNeverCreated=$false;started=$false;startEntered=$false;startUnknown=$false;stdinReturned=$false;waitReturned=$false;processDisposed=$false;lock=$null;lockClosed=$false;lockCloseEntered=$false;readers=@();records=@();rawBytes=[long]0;textBytes=[long]0;binaryBytes=[long]0;rawUnknown=$false;firstFailure=$null;haltAttempted=$false;receiptAttempted=$false;recordBytes=0;writeFaultInjected=$false;qualified=$false}
if(-not $global:Android02CaptureCustody){$global:Android02CaptureCustody=@{}}
$global:Android02CaptureCustody[$c.owner]=$c
function Fail([string]$Code){if($null -eq $c.firstFailure){$c.firstFailure=$Code}}
function Snapshot {
 $prefixOnly=$c.started -and @($c.readers|Where-Object {-not $_.readTaskReturned}).Count -ne 0
 return @{id=$c.id;bindings=$c.bindings;semantic=$c.semantic;scopeStartTick=$c.scopeStartTick;scope=$c.scope;owner=$c.owner;controllerPid=$c.controllerPid;processToken=if($c.process){[Runtime.CompilerServices.RuntimeHelpers]::GetHashCode($c.process)}else{0};processCreateEntered=[bool]$c.processCreateEntered;processCreateReturned=[bool]$c.processCreateReturned;processDisposeEntered=[bool]$c.processDisposeEntered;processDisposeCalls=$c.processDisposeCalls;startEntered=[bool]$c.startEntered;startReturned=[bool]$c.startReturned;startReturnedValue=$c.startReturnedValue;startUnknown=[bool]$c.startUnknown;prestartDisposition=$c.prestartDisposition;noStartResourcesReturned=[bool]$c.noStartResourcesReturned;stdinNeverCreated=[bool]$c.stdinNeverCreated;lockOpenEntered=[bool]$c.lockOpenEntered;lockOpenReturned=[bool]$c.lockOpenReturned;lockOpenUnknown=[bool]$c.lockOpenUnknown;childPid=$c.childPid;started=$c.started;waitReturned=$c.waitReturned;processDisposed=$c.processDisposed;rawBytesKnown=$c.rawBytes;textBytesKnown=$c.textBytes;binaryBytesKnown=$c.binaryBytes;input=(InputFacts);rawKnownIsPrefix=$prefixOnly;rawAmountUnknown=($c.rawUnknown -or $prefixOnly);firstFailure=$c.firstFailure;initializationFailure=$c.initializationFailure;readers=@($c.readers|ForEach-Object {@{role=$_.role;readerToken=$_.token;streamToken=$_.streamToken;kind=$_.kind;sha256=$_.rawSha;rawBytes=$_.raw;savedBytes=$_.saved;readCalls=$_.readCalls;writeCalls=$_.writeCalls;writeAttemptedBytes=$_.writeAttempted;savedAmountUnknown=[bool]$_.savedAmountUnknown;eof=$_.eof;readTaskReturned=$_.readTaskReturned;pipeOpenEntered=[bool]$_.pipeOpenEntered;pipeOpenReturned=[bool]$_.pipeOpenReturned;pipeNeverCreated=[bool]$_.pipeNeverCreated;pipeCloseReturned=$_.pipeClosed;fileOpenEntered=[bool]$_.fileOpenEntered;fileOpenReturned=[bool]$_.fileOpenReturned;fileOpenUnknown=[bool]$_.fileOpenUnknown;fileCloseCalls=$_.fileCloseCalls;fileCloseReturned=$_.fileClosed;fileCloseEntered=$_.fileCloseEntered}});metadata=@($c.records|ForEach-Object {@{name=$_.name;writeRequestedBytes=$_.bytes;opened=$_.opened;openUnknown=$_.openUnknown;writeReturned=$_.writeReturned;writeFailed=$_.writeFailed;closeEntered=$_.closeEntered;closed=$_.closed}})}
}
# Attached to the SAME original context before source open/start. One source, one read, one write.
$c.input=@{source=$null;openEntered=$false;openReturned=$false;sourceCloseEntered=$false;sourceClosed=$true;pinReadBytes=[long]0;pinReadCalls=0;pinUnknown=$false;pinHashCreateEntered=$false;pinHashCreateReturned=$false;pinHashDisposeEntered=$false;pinHashDisposed=$false;pinHash=$null;verified=$false;expectedBytes=[long]0;expectedSha='';payloadCommitted=[long]0;sourceRead=$null;sourceReadCalls=0;sourceReadBytes=[long]0;sourceReadReturned=$true;sourceEof=$false;sourceUnknown=$false;buffer=[byte[]]::new(4096);write=$null;writeCalls=0;writeAttempted=[long]0;writeReturnedBytes=[long]0;writeAmountUnknown=$false;writing=0;failed=$false;stdinCloseEntered=$false;stdinClosed=$false;closeGateObserved=$false}
function OpenPinnedSource {
 $pin=if($inputPin){$inputPin}else{$payloadPin};if(-not $pin){return}
 $i=$c.input;$i.expectedBytes=[long]$pin.bytes;$i.expectedSha=[string]$pin.sha256
 if($i.expectedBytes -lt 1 -or $i.expectedBytes -gt 7151481 -or $i.expectedSha -cnotmatch '^[a-f0-9]{64}$'){throw 'FINITE_SOURCE_PIN'}
 NoLinks $pin.path;$i.openEntered=$true;$i.sourceClosed=$false
 $i.source=[IO.FileStream]::new($pin.path,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read,4096,$true);$i.openReturned=$true
 if($i.source.Length -ne $i.expectedBytes){Fail 'SOURCE_LENGTH_MISMATCH';$i.failed=$true;return}
 $i.pinHashCreateEntered=$true;$h=[Security.Cryptography.IncrementalHash]::CreateHash([Security.Cryptography.HashAlgorithmName]::SHA256);$i.pinHash=$h;$i.pinHashCreateReturned=$true
 try{do{$i.pinReadCalls++;$n=$i.source.Read($i.buffer,0,4096);$i.pinReadBytes+=$n;if($n -gt 0){$h.AppendData($i.buffer,0,$n)}}while($n -gt 0);$actual=[Convert]::ToHexString($h.GetHashAndReset()).ToLowerInvariant();if($actual -cne $i.expectedSha){Fail 'SOURCE_HASH_MISMATCH';$i.failed=$true;return};$i.verified=$true;$i.source.Position=0;if($payloadPin){$i.payloadCommitted=$i.expectedBytes}}
 catch{$i.pinUnknown=$true;$i.failed=$true;Fail 'PIN_SOURCE_READ_UNKNOWN'}finally{$i.pinHashDisposeEntered=$true;$h.Dispose();$i.pinHashDisposed=$true}
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
function InputReturned {return (-not $c.input.pinHashCreateEntered -or ($c.input.pinHashCreateReturned -and $c.input.pinHashDisposed)) -and $c.input.sourceClosed -and -not $c.input.write -and -not $c.input.sourceRead -and -not $c.input.writeStartUnknown -and -not $c.input.readStartUnknown}
function InputFacts {
 $i=$c.input;return @{sourceToken=if($i.source){[Runtime.CompilerServices.RuntimeHelpers]::GetHashCode($i.source)}else{0};sourceOpenReturned=$i.openReturned;sourceCloseReturned=$i.sourceClosed;verified=$i.verified;expectedBytes=$i.expectedBytes;expectedSha256=$i.expectedSha;pinReadCalls=$i.pinReadCalls;pinReadBytes=$i.pinReadBytes;pinAmountUnknown=$i.pinUnknown;pinHashCreateEntered=[bool]$i.pinHashCreateEntered;pinHashCreateReturned=[bool]$i.pinHashCreateReturned;pinHashDisposeEntered=[bool]$i.pinHashDisposeEntered;pinHashDisposed=[bool]$i.pinHashDisposed;transportSourceReadCalls=$i.sourceReadCalls;transportSourceReadBytes=$i.sourceReadBytes;sourceReadTaskReturned=$i.sourceReadReturned;sourceEof=$i.sourceEof;sourceAmountUnknown=($i.sourceUnknown -or [bool]$i.sourceRead);stdinWriteCalls=$i.writeCalls;stdinWriteAttemptedBytes=$i.writeAttempted;stdinWriteReturnedBytes=$i.writeReturnedBytes;stdinWriteTaskReturned=(-not $i.write);stdinWriteAmountUnknown=($i.writeAmountUnknown -or [bool]$i.write);stdinCloseReturned=$i.stdinClosed;closeGateObserved=$i.closeGateObserved;outboundApkPayloadCommittedBytes=$i.payloadCommitted;outboundSdkWireBytes='NOT_MEASURED_NOT_FREE_NOT_ARCHIVE';inputPinAndTransferReadsAreSeparate=$true}
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
function ReadersReturned {return @($c.readers|Where-Object {(-not $_.pipeClosed -and -not $_.pipeNeverCreated) -or $_.fileOpenUnknown -or ($_.fileOpenReturned -and -not $_.fileClosed)}).Count -eq 0}
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
   if(-not $gate -and -not $r.writeStartUnknown -and -not $r.fileCloseEntered){$r.fileCloseEntered=$true;try{$r.file.Close();$r.fileClosed=$true;if($r.eof -and $r.raw -eq $r.saved -and -not $r.recordFailed){$r.rawSha=Digest (Join-Path $root ($request.id+'-'+$r.role+'.bin'))}}catch{Fail 'ORIGINAL_RAW_FILE_CLOSE_UNKNOWN'}}
  }
 }
}
$timer=[Diagnostics.Stopwatch]::StartNew()
try{
 $c.processCreateEntered=$true;$c.process=[Diagnostics.Process]::new();$c.processCreateReturned=$true
 try{$c.lockOpenEntered=$true;$c.lock=[IO.FileStream]::new((Join-Path $root '.capture.lock'),[IO.FileMode]::OpenOrCreate,[IO.FileAccess]::ReadWrite,[IO.FileShare]::Read);$c.lockOpenReturned=$true}catch{
  $e=$_.Exception;while($e.InnerException){$e=$e.InnerException};if(($e.HResult -band 65535) -in @(32,33)){$c.admissionRejected=$true;throw 'ORIGINAL_CONTROLLER_EXCLUSIVE_NO_CHILD'};$c.lockOpenUnknown=$true;throw
 }
 # Repeat persistent admission under this SAME lock, without deleting/overwriting any record.
 if((Test-Path -LiteralPath (Join-Path $root 'capture-halted.json')) -or (Test-Path -LiteralPath (Join-Path $root ($request.id+'-entered.json')))){$c.admissionRejected=$true;throw 'PERSISTENT_REPLAY_OR_HALT_NO_CHILD'}
 foreach($role in @('stdout','stderr')){if(Test-Path -LiteralPath (Join-Path $root ($request.id+'-'+$role+'.bin'))){$c.admissionRejected=$true;throw 'EXISTING_OUTPUT_NO_CHILD'}}
 WriteRecord ($request.id+'-entered.json') @{schema='ANDROID02_CAPTURE_INTENT_V1';request=$request;owner=$c.owner;controllerPid=$PID;policySha256=$request.policySha256} 8192
 while(-not (RecordsReturned)){PumpRecords;if($timer.Elapsed.TotalSeconds -gt $request.qualificationSeconds){Fail 'PRESTART_RECORD_TIMEOUT'};Start-Sleep -Milliseconds 2}
 if($null -eq $c.firstFailure){
  OpenPinnedSource
  if($c.firstFailure){throw 'SOURCE_PIN_REJECTED_BEFORE_CHILD'};try{RuntimeSourcePreflight}catch{Fail $_.Exception.Message;throw};if($timer.Elapsed.TotalSeconds -ge $request.qualificationSeconds -or (-not $fixture -and $localAdmissionTimer.Elapsed.TotalSeconds -ge $activation.localProofSeconds)){Fail 'PRESTART_LOCAL_OR_QUALIFICATION_BOUND';throw 'PRESTART_STOP_NO_CHILD'}
  foreach($role in @('stdout','stderr')){
   $r=@{role=$role;kind=if($role -ceq 'stdout' -and $request.maxBinaryBytes -gt 0){'BINARY'}else{'TEXT'};readCalls=0;writeCalls=0;writeAttempted=[long]0;token=[Guid]::NewGuid().ToString();file=$null;fileOpenEntered=$false;fileOpenReturned=$false;fileOpenUnknown=$false;fileCloseCalls=0;pipeOpenEntered=$false;pipeOpenReturned=$false;pipeNeverCreated=$false;fileCloseEntered=$false;fileClosed=$false;pipe=$null;pipeCloseEntered=$false;pipeClosed=$false;read=$null;write=$null;buffer=[byte[]]::new(4096);queue=[Collections.Generic.Queue[byte[]]]::new();raw=[long]0;saved=[long]0;eof=$false;readTaskReturned=$false;recordFailed=$false}
   $c.readers+=,$r
   try{$r.fileOpenEntered=$true;$r.file=[IO.FileStream]::new((Join-Path $root ($request.id+'-'+$role+'.bin')),[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read,4096,$true);$r.fileOpenReturned=$true}catch{$r.fileOpenUnknown=$true;throw}
  }
  $info=[Diagnostics.ProcessStartInfo]::new();$info.FileName=$request.argv[0];$info.UseShellExecute=$false;$info.CreateNoWindow=$true;$info.RedirectStandardInput=$true;$info.RedirectStandardOutput=$true;$info.RedirectStandardError=$true
  for($i=1;$i -lt $request.argv.Count;$i++){$info.ArgumentList.Add([string]$request.argv[$i])}
  if($fixture -and $policy.fixtureFault -ceq 'PRESTART_KNOWN_REJECT'){throw 'CONTROLLED_PRESTART_AFTER_TWO_FILES'}
  RunnerFinalStartGate $ad $policy $scopeStartTick $index $fixture
  $c.process.StartInfo=$info;$c.startEntered=$true
  try{$startValue=$c.process.Start();$c.startReturned=$true;$c.startReturnedValue=[bool]$startValue;if(-not $startValue){$c.startUnknown=$true;throw 'START_UNPROVEN'};$c.started=$true;$c.childPid=$c.process.Id}catch{$c.startUnknown=$true;throw}
  foreach($r in $c.readers){
   $r.pipeOpenEntered=$true;$r.pipe=if($r.role -ceq 'stdout'){$c.process.StandardOutput.BaseStream}else{$c.process.StandardError.BaseStream};$r.pipeOpenReturned=$true;$r.streamToken=[Runtime.CompilerServices.RuntimeHelpers]::GetHashCode($r.pipe)
   if($fixture -and $policy.fixtureFault -ceq 'READ_FAULT_ONCE' -and $r.role -ceq 'stdout'){$tcs=[Threading.Tasks.TaskCompletionSource[int]]::new();$tcs.SetException([IO.IOException]::new('CONTROLLED_FIXTURE_READ_FAULT'));$r.read=$tcs.Task}else{$r.readCalls++;$r.read=$r.pipe.ReadAsync($r.buffer,0,4096)}
  }
  PumpInput
 }
}catch{$c.initializationFailure=$_.Exception.Message;Fail 'ORIGINAL_INITIALIZATION_OR_ADMISSION_FAILED'}
if(-not $c.startEntered){[void](Close-KnownPrestartResources $c);$c.lockNeverCreated=-not $c.lockOpenEntered}
if($c.admissionRejected){if($c.lock -and -not $c.lockCloseEntered){$c.lockCloseEntered=$true;$c.lock.Close();$c.lockClosed=$true};if(-not $c.noStartResourcesReturned){while($true){Start-Sleep -Milliseconds 500}};$global:Android02CaptureCustody.Remove($c.owner);throw 'ADMISSION_REJECTED_NO_CHILD_NO_NEW_RECORD'}
# This controller remains the strong owner while any original result is pending or unknown.
do{
 PumpRecords
 if($c.started -and -not $c.waitReturned -and -not $c.waitEntered){try{if($c.process.HasExited){$c.waitEntered=$true;$c.process.WaitForExit();$c.waitReturned=$true;$c.exitCode=$c.process.ExitCode;if($c.exitCode -ne 0){Fail 'CHILD_NONZERO_EXIT'}}}catch{$c.waitEntered=$true;Fail 'ORIGINAL_WAIT_UNKNOWN'}}
 PumpReaders
 PumpInput
 PumpInputSourceClose
 if(-not $fixture -and ([Environment]::TickCount64-$c.scopeStartTick -ge 1000*$activation.wholeWallSeconds)){Fail 'WHOLE_SCOPE_OBSERVATION_UNKNOWN_NO_TERMINATION'}
 if($timer.Elapsed.TotalSeconds -gt $request.qualificationSeconds){Fail 'QUALIFICATION_TIMEOUT_NO_TERMINATION'}
 if($c.waitReturned -and (ReadersReturned) -and (InputReturned) -and -not $c.semanticChecked){$c.semanticChecked=$true;if($null -eq $c.firstFailure){try{$c.semantic=RoleSemantic $request.id (Join-Path $root ($request.id+'-stdout.bin')) $fixture;if($c.semantic -cnotin @('PASS','PASS_LIMITED_APP_RECEIPT_INTERNAL_FINISH_UNPROVEN')){Fail $c.semantic}}catch{$c.semantic='ROLE_SEMANTIC_UNPROVEN';Fail 'ROLE_SEMANTIC_UNPROVEN'}}else{$c.semantic='NOT_RUN_UNQUALIFIED_CAPTURE'}}
 if($c.firstFailure -and -not $c.haltAttempted){$c.haltAttempted=$true;WriteRecord 'capture-halted.json' @{id=$c.id;scope=$c.scope;owner=$c.owner;controllerPid=$PID;childPid=$c.childPid;firstFailure=$c.firstFailure;rawKnownPrefix=$c.rawBytes;unknownOrPending=$true;noSuccessor=$true} 2048}
 $bodyReturned=$c.started -and $c.waitReturned -and $c.stdinReturned -and (InputReturned) -and (ReadersReturned)
 if(-not $c.startEntered -and $c.noStartResourcesReturned -and (ReadersReturned) -and (InputReturned)){$bodyReturned=$true}
 if($bodyReturned -and -not $c.processDisposeEntered -and -not $c.processNeverCreated){$c.processDisposeEntered=$true;try{$c.processDisposeCalls++;$c.process.Dispose();$c.processDisposed=$true}catch{Fail 'ORIGINAL_PROCESS_DISPOSE_UNKNOWN'}}
 if($bodyReturned -and ($c.processDisposed -or $c.processNeverCreated) -and (RecordsReturned) -and -not $c.receiptAttempted){
  $c.receiptAttempted=$true;$c.qualified=($null -eq $c.firstFailure) -and @($c.readers|Where-Object {-not $_.eof -or $_.recordFailed}).Count -eq 0
  $facts=Snapshot;$facts.schema='ANDROID02_CAPTURE_RECEIPT_V1';$facts.captureQualified=$c.qualified;$facts.receiptOwnCloseNotProvenByThisFile=$true;$facts.metadataFilesBeforeReceiptReturned=$true;$facts.rawAmountUnknown=$c.rawUnknown -or $c.input.pinUnknown -or $c.input.sourceUnknown -or $c.input.writeAmountUnknown
  WriteRecord ($request.id+'-receipt.json') $facts 8192
 }
 $allReturned=$bodyReturned -and ($c.processDisposed -or $c.processNeverCreated) -and $c.receiptAttempted -and (RecordsReturned)
 if(-not $allReturned){Start-Sleep -Milliseconds 5}
}while(-not $allReturned)
if($c.lock -and -not $c.lockCloseEntered){$c.lockCloseEntered=$true;try{$c.lock.Close();$c.lockClosed=$true}catch{Fail 'ORIGINAL_BATCH_LOCK_CLOSE_UNKNOWN'}}
if(-not $c.lockClosed -and -not $c.lockNeverCreated){while($true){Start-Sleep -Milliseconds 500}}
$console=Snapshot;$console.schema='ANDROID02_CAPTURE_CONSOLE_V1';$console.captureQualified=$c.qualified -and $null -eq $c.firstFailure;$console.allOriginalResourcesReturnedAtConsole=$true;$console.recordWriteBytesKnown=$c.recordBytes;$console.rawTextSavedBytesKnown=($c.readers|Where-Object kind -CEQ 'TEXT'|Measure-Object saved -Sum).Sum;$console.binaryArchiveSavedBytesKnown=($c.readers|Where-Object kind -CEQ 'BINARY'|Measure-Object saved -Sum).Sum;$console.recordWriteAmountUnknown=[bool]$c.recordAmountUnknown;$console.captureReceiptSha256=Digest (Join-Path $root ($request.id+'-receipt.json'));$console.externalControllerExitProofStillRequired=$true;$console.consoleBytes=0;$console.consoleForwardReserveBytes=4096;$console.proofReadBytes=$proofReadBytes;$console.logicalControlReads=@{requestBodyBytes=$requestBodyReadBytes;requestBodyReadCalls=$requestBodyReadCalls;ownerAdmissionBytes=([long]$ownerCurrentReadCost-$requestBodyReadBytes);predecessorProofAndNativeBytes=([long]$proofReadBytes-$ownerCurrentReadCost)};$console.batchSdkChildrenEntered=$batchSdkBefore+[int]$c.started;$console.batchTextChargedBytesKnown=[long]0;$console.batchBinaryArchiveBytesKnown=$batchBinaryBefore+[long]$console.binaryArchiveSavedBytesKnown;$console.batchGroups=@{preflight=[long]$groups.preflight;install=[long]$groups.install;instrument=[long]$groups.instrument;control=[long]$groups.control;payload=[long]$groups.payload+[long]$c.input.payloadCommitted;command=[long]$groups.command+[long]$commandBytes};$console.batchGroups[$group]+=$c.textBytes;$console.batchAmountUnknown=[bool]($c.rawUnknown -or $c.recordAmountUnknown -or $c.input.pinUnknown -or $c.input.sourceUnknown -or $c.input.writeAmountUnknown -or @($c.readers|Where-Object savedAmountUnknown -EQ $true).Count -gt 0);$console.controlRecordAndConsoleKnown=0
for($sizing=0;$sizing -lt 8;$sizing++){
 $text=($console|ConvertTo-Json -Depth 12 -Compress)+"`n";$console.consoleBytes=[Text.UTF8Encoding]::new($false).GetByteCount($text)
 $console.controlRecordAndConsoleKnown=$c.recordBytes+$console.consoleBytes;$console.batchGroups.control=[long]$groups.control+$c.recordBytes+2*$console.consoleBytes+$proofReadBytes
 $console.batchTextChargedBytesKnown=$batchTextBefore+$c.textBytes+$c.recordBytes+2*$console.consoleBytes+$proofReadBytes
 if($c.recordBytes+2*$console.consoleBytes+$proofReadBytes -gt 65536 -or $console.batchTextChargedBytesKnown -gt 3276800 -or $console.batchGroups.control -gt 1048576 -or $console.batchGroups.payload -gt 7629605 -or $console.batchGroups.command -gt 28672 -or $console.batchBinaryArchiveBytesKnown -gt 0){Fail 'CONTROL_OR_BATCH_QUALIFIER_EXCEEDED';$console.firstFailure=$c.firstFailure;$console.captureQualified=$false}
}
$text=($console|ConvertTo-Json -Depth 12 -Compress)+"`n";$consoleBytes=[Text.UTF8Encoding]::new($false).GetByteCount($text)
if($consoleBytes -gt 8192 -or $consoleBytes -ne $console.consoleBytes){while($true){Start-Sleep -Milliseconds 500}}
[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false)
try{[Console]::Out.Write($text);[Console]::Out.Flush()}catch{while($true){Start-Sleep -Milliseconds 500}}
$global:Android02CaptureCustody.Remove($c.owner)
if($console.captureQualified){exit 0}else{exit 2}
