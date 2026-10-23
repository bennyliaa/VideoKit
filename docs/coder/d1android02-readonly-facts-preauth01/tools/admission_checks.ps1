function UIntField($Object,[string]$Key,[bigint]$Max){
 if($Object -isnot [pscustomobject]){return $false};$p=$Object.PSObject.Properties[$Key]
 if($null -eq $p){return $false};$v=$p.Value
 if($v -isnot [int] -and $v -isnot [long] -and $v -isnot [uint] -and $v -isnot [ulong] -and $v -isnot [bigint]){return $false}
 return [bigint]$v -ge 0 -and [bigint]$v -le $Max
}
function CheckRouteStats($s,[bool]$fixture){
 $keys=@('mode','logicalObservations','tcpCalls','tableWorkflows','tableAllocatedBytes','tableReturnedBytes','metadataBytesKnown','metadataAmountUnknown','imageHashBytes','imageHashAmountUnknown','imageHashBytesReservedUnknown','apiCalls','observationOrder','processCreationFiletime','imageFileIdentity')
 if($s -isnot [pscustomobject] -or @(Compare-Object -CaseSensitive @($s.PSObject.Properties.Name|Sort-Object) @($keys|Sort-Object)).Count){throw 'ROUTE_STATS_SCHEMA'}
 $mode=if($fixture){'OFFLINE_TABLES'}else{'LIVE_SYSTEM_API'}
 if($s.mode -cne $mode -or -not (BoolField $s 'metadataAmountUnknown' $false) -or -not (BoolField $s 'imageHashAmountUnknown' $false)){throw 'ROUTE_STATS_MODE'}
 $caps=@{logicalObservations=4;tcpCalls=8;tableWorkflows=4;tableAllocatedBytes=32768;tableReturnedBytes=32768;metadataBytesKnown=40960;imageHashBytes=8273560;imageHashBytesReservedUnknown=8273560;processCreationFiletime=2650467743999999999}
 foreach($k in $caps.Keys){if(-not (IntField $s $k $caps[$k])){throw 'ROUTE_STATS_INTEGER'}}
 if($s.logicalObservations -ne 4 -or $s.tableWorkflows -ne 4 -or $s.imageHashBytes -ne 8273560 -or $s.imageHashBytesReservedUnknown -ne 0 -or $s.tableReturnedBytes -lt (2*(4+24)+2*4) -or $s.tableReturnedBytes -gt $s.tableAllocatedBytes -or $s.metadataBytesKnown -le 0 -or $s.processCreationFiletime -le 0 -or -not (SameArgv @($s.observationOrder) @('L1','P1','P2','L2'))){throw 'ROUTE_STATS_SUCCESS'}
 $limits=@{GetExtendedTcpTable=8;OpenProcess=1;GetProcessId=2;GetProcessTimes=2;QueryFullProcessImageNameW=2;WaitForSingleObject=2;GetFileAttributesW=16;CreateFileW=1;GetFileInformationByHandle=2;GetFinalPathNameByHandleW=2;ReadFile=127;CloseHandle=2}
 if($s.apiCalls -isnot [pscustomobject]){throw 'ROUTE_API_SCHEMA'}
 foreach($p in $s.apiCalls.PSObject.Properties){if($p.Name -cnotin @($limits.Keys) -or -not (IntField $s.apiCalls $p.Name $limits[$p.Name] 1)){throw 'ROUTE_API_BOUND'}}
 if($fixture){if($s.tcpCalls -ne 0 -or @($s.apiCalls.PSObject.Properties).Count){throw 'ROUTE_FIXTURE_NATIVE_CALL'}}
 else{foreach($k in $limits.Keys){$min=if($k -ceq 'GetFileAttributesW'){1}else{$limits[$k]};if(-not (IntField $s.apiCalls $k $limits[$k] $min)){throw 'ROUTE_API_EXACT'}};if($s.tcpCalls -ne 8){throw 'ROUTE_TCP_EXACT'}}
 $f=$s.imageFileIdentity;$fk=@('volume','fileId','creation','lastWrite','bytes','attrs','finalPath')
 if($f -isnot [pscustomobject] -or @(Compare-Object -CaseSensitive @($f.PSObject.Properties.Name|Sort-Object) @($fk|Sort-Object)).Count){throw 'ROUTE_FILE_SCHEMA'}
 foreach($k in @('volume','attrs')){if(-not (UIntField $f $k ([bigint]4294967295))){throw 'ROUTE_FILE_DWORD'}}
 foreach($k in @('fileId','bytes','creation','lastWrite')){if(-not (UIntField $f $k ([bigint][ulong]::MaxValue))){throw 'ROUTE_FILE_UINT64'}}
 if($f.finalPath -isnot [string] -or $f.bytes -ne 8273560 -or $f.creation -le 0 -or $f.lastWrite -le 0 -or $f.creation -gt $s.processCreationFiletime -or $f.lastWrite -gt $s.processCreationFiletime -or ($f.attrs -band 1104) -or (($f.attrs -band 128) -and $f.attrs -ne 128)){throw 'ROUTE_FILE_BINDING'}
 $path=$f.finalPath;$pathBytes=[Text.UnicodeEncoding]::new($false,$false,$true).GetByteCount($path)
 if($pathBytes -le 0 -or $pathBytes -gt 1022 -or $path.IndexOf([char]0) -ge 0){throw 'ROUTE_FILE_PATH_LENGTH'}
 if($path.StartsWith('\\?\')){$path=$path.Substring(4)}
 if($path -cnotmatch '^[A-Za-z]:[\\/]' -or $path.Substring(2).Contains(':')){throw 'ROUTE_FILE_LOCAL_PATH'}
 foreach($part in $path.Substring(3).Replace('/','\').Split('\')){if($part -cnotin @('','.','..') -and ($part.EndsWith('.') -or $part.EndsWith(' '))){throw 'ROUTE_FILE_PATH_SUFFIX'}}
 if([IO.Path]::GetFullPath($path).ToLowerInvariant() -cne 'd:\android\sdk\platform-tools\adb.exe'){throw 'ROUTE_FILE_FINAL_PATH'}
 $counts=if($fixture){@{GetProcessId=2;GetProcessTimes=2;QueryFullProcessImageNameW=2;WaitForSingleObject=2;GetFileInformationByHandle=2;GetFinalPathNameByHandleW=2}}else{$s.apiCalls}
 $sizeCalls=if($fixture){2*$s.tableWorkflows}else{$s.tcpCalls}
 if(-not $fixture -and $s.tcpCalls -ne 2*$s.tableWorkflows){throw 'ROUTE_TABLE_CALL_RELATION'}
 $base=[long]$s.tableReturnedBytes+4*$sizeCalls
 $fees=@{GetProcessId=4;GetProcessTimes=32;QueryFullProcessImageNameW=4;WaitForSingleObject=4;GetFileInformationByHandle=52;GetFileAttributesW=4;ReadFile=4}
 foreach($k in $fees.Keys){$n=if($fixture){$counts[$k]}else{$counts.PSObject.Properties[$k].Value};if($null -ne $n){$base+=$fees[$k]*[long]$n}}
 $finalCount=if($fixture){$counts.GetFinalPathNameByHandleW}else{$counts.GetFinalPathNameByHandleW}
 $base+=([Text.Encoding]::Unicode.GetByteCount($f.finalPath)+2)*[long]$finalCount
 $queryCount=[long]$counts.QueryFullProcessImageNameW
 $minimumNameBytes=[Text.Encoding]::Unicode.GetByteCount('d:\android\sdk\platform-tools\adb.exe')+2
 if($s.metadataBytesKnown -lt $base+$minimumNameBytes*$queryCount -or $s.metadataBytesKnown -gt $base+2*512*$queryCount){throw 'ROUTE_METADATA_DERIVED_BOUNDS'}
}

function CheckInitialGate($proof,$proofPath,$ad,$policy,[bool]$fixture){
 $expectedKind=if($fixture){'OFFLINE_FIXTURE'}else{'LIVE_LOCAL_METADATA'}
 $h=$ad.gateHandoff;$d=$proof.outerDelta
 foreach($o in @(@{obj=$h;keys=@('schema','generation','scopeStartTick','ownerPid','initialProofSha256','receiverControlBytes','gateSourcesSha256','claimFileId','kind')},@{obj=$d;keys=@('eventId','nativeWriteBytes','proofWriteBytes','additionalForwardBytes','sourceOwnerSha256','gateSourcesSha256','generation','kind')})){
  if(@(Compare-Object -CaseSensitive @($o.obj.PSObject.Properties.Name|Sort-Object) @($o.keys|Sort-Object)).Count){throw 'INITIAL_GATE_EXACT_NESTED_SCHEMA'}
 }
 if($h.schema -cne 'ENTRY_GATE_HANDOFF_V1' -or $h.kind -cne $expectedKind -or $d.kind -cne $expectedKind -or $h.generation -cne $d.generation -or $h.ownerPid -ne $ad.ownerPid -or $h.scopeStartTick -ne $proof.scopeStartTick -or $h.initialProofSha256 -cne $PredecessorProofSha -or $h.gateSourcesSha256 -cne $policy.gateSourcesSha256 -or $d.gateSourcesSha256 -cne $policy.gateSourcesSha256 -or $d.sourceOwnerSha256 -cne $policy.outerOwnerSha256){throw 'INITIAL_GATE_LIVE_HANDOFF_BINDING'}
 foreach($k in @('ownerPid','scopeStartTick','receiverControlBytes','claimFileId')){if(-not (IntField $h $k ([long]::MaxValue) 1)){throw 'INITIAL_HANDOFF_INTEGER'}}
 foreach($k in @('nativeWriteBytes','proofWriteBytes','additionalForwardBytes')){if(-not (IntField $d $k 131072)){throw 'INITIAL_DELTA_INTEGER'}}
 if($h.generation -isnot [string] -or $h.generation -cnotmatch '^[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{12}$'){throw 'INITIAL_GENERATION_TYPE'}
 $manifestPath='D:\CodexProjects\VideoKit\docs\coder\d1android02-global-idle-contract03-fix\reference\gate-sources.json'
 if((Digest $manifestPath) -cne $policy.gateSourcesSha256 -or $policy.gateSourcesSha256 -cne $script:expectedGateSourcesSha256){throw 'INITIAL_GATE_SOURCE_MANIFEST'}
 $gm=ReadJsonExact $manifestPath @('schema','files') 8192
 foreach($row in $gm.files){$f=Join-Path 'D:\CodexProjects\VideoKit\docs\coder\d1android02-global-idle-contract03-fix' $row.path;NoLinks $f;if((Digest $f) -cne $row.sha256){throw 'INITIAL_GATE_SOURCE_CHANGED'}}
 $rp=Join-Path $root 'gate-original-return.json';NoLinks $rp
 $r=ReadJsonExact $rp @('schema','scope','planId','kind','generation','ownerPid','checkerPid','temporaryResourcesReturned','scopeClaimIntentionallyRetained','claimFileId','claimPath','scopeStartTick','checkerSourceSha256','gateSourcesSha256','entrySha256','ownerSha256','routeSha256','events','controlBeforeReceipt','receiptWriteBytes','physicalIO','sourceHashBytes','sourceHashReads') 16384
 $script:initialGateReceipt=$r
 $receiptHash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($script:lastJsonBytes)).ToLowerInvariant();$receiptLength=$script:lastJsonBytes.Length
 if($r.schema -cne 'ENTRY_GATE_RETURN_V1' -or $r.scope -cne $policy.scope -or $r.planId -cne $policy.planId -or $r.kind -cne $expectedKind -or $r.generation -cne $h.generation -or $r.ownerPid -ne $ad.ownerPid -or $r.checkerPid -ne $proof.controllerPid -or $r.claimFileId -ne $h.claimFileId -or $r.scopeStartTick -ne $h.scopeStartTick -or $r.gateSourcesSha256 -cne $policy.gateSourcesSha256 -or $r.entrySha256 -cne $policy.entrySha256 -or $r.ownerSha256 -cne $policy.outerOwnerSha256 -or $receiptHash -cne $proof.outerReturnSha256 -or $receiptHash -cne $proof.captureReceiptSha256){throw 'INITIAL_GATE_ORIGINAL_RECEIPT'}
 if(-not (BoolField $r 'temporaryResourcesReturned' $true) -or -not (BoolField $r 'scopeClaimIntentionallyRetained' $true) -or -not (BoolField $proof 'candidateOnlyWriterCloseNotProven' $true)){throw 'INITIAL_GATE_RESOURCE_SETS'}
 foreach($k in @('ownerPid','checkerPid','scopeStartTick','claimFileId')){if(-not (IntField $r $k ([long]::MaxValue) 1)){throw 'INITIAL_RECEIPT_INTEGER'}}
 $expectedClaim=if($fixture){Join-Path ([IO.Path]::GetDirectoryName($root)) 'cooperative-default-route.lock'}else{'D:\CodexProjects\VideoKit\docs\coder\d1android02-production-runner01\release\cooperative-default-route.lock'}
 if($r.claimPath -isnot [string] -or $r.claimPath -cne $expectedClaim){throw 'INITIAL_CLAIM_PATH'};NoLinks $r.claimPath
 $sourcePath=if($fixture){'selfchecks/route_fixture.py'}else{'tools/win32_route.py'}
 $expectedSource=@($gm.files|Where-Object path -CEQ $sourcePath)
 if($expectedSource.Count -ne 1 -or $r.checkerSourceSha256 -cne $expectedSource[0].sha256){throw 'INITIAL_CHECKER_SOURCE'}
 foreach($k in @('controlBeforeReceipt','receiptWriteBytes','sourceHashBytes','sourceHashReads')){if(-not (IntField $r $k 268435456 1)){throw 'INITIAL_GATE_ACCOUNTING_TYPE'}}
 if($r.sourceHashReads -gt 64 -or $r.physicalIO -cne 'UNPROVEN'){throw 'INITIAL_GATE_SOURCE_ACCOUNTING'}
 $names=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal);$sum=[long]0
 if($r.events -isnot [array] -or $r.events.Count -lt 5 -or $r.events.Count -gt 32){throw 'INITIAL_EVENT_SET'}
 foreach($e in $r.events){if(@(Compare-Object -CaseSensitive @($e.PSObject.Properties.Name|Sort-Object) @('bytes','event')).Count -or $e.event -isnot [string] -or -not $names.Add($e.event) -or -not (IntField $e 'bytes' 131072)){throw 'INITIAL_ONCE_EVENT'};$sum+=$e.bytes}
 if($sum -ne $r.controlBeforeReceipt -or $r.receiptWriteBytes -ne $receiptLength -or $d.nativeWriteBytes -ne $receiptLength -or -not (IntField $proof 'proofWriteBytes' 4096 1) -or $proof.proofWriteBytes -ne (Get-Item -LiteralPath $proofPath).Length -or $d.proofWriteBytes -ne $proof.proofWriteBytes -or $d.additionalForwardBytes -ne 0 -or $h.receiverControlBytes -ne $receiptLength+$proof.proofWriteBytes){throw 'INITIAL_ACTUAL_BYTES_DELTA'}
 $expectedEvent=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($policy.scope+'|pre_sdk_local_gate|'+$h.generation+'|'+$receiptHash))).ToLowerInvariant()
 if($d.eventId -cne $expectedEvent -or $proof.semanticDependency -cne 'pre_sdk_local_gate_ACTUAL_RETURN_AND_SEMANTIC_PASS'){throw 'INITIAL_EVENT_SOURCE'}
 if(@(Compare-Object -CaseSensitive @($proof.batchGroups.PSObject.Properties.Name|Sort-Object) @('command','control','install','instrument','payload','preflight')).Count){throw 'INITIAL_GROUP_SCHEMA'}
 foreach($k in @('preflight','install','instrument','payload','command')){if($proof.batchGroups.$k -ne 0){throw 'INITIAL_NO_SDK_CONSUMPTION'}}
 if($proof.batchGroups.control -ne $sum+$receiptLength+$proof.proofWriteBytes -or $proof.batchGroups.control -gt 262144 -or $proof.batchTextChargedBytesKnown -ne $proof.batchGroups.control){throw 'INITIAL_LEDGER_RESET_DUPLICATE'}
 $freshPath=Join-Path $root 'fresh-route.json';NoLinks $freshPath
 $fresh=ReadJsonExact $freshPath @('scope','planId','checkedAtUtc','serverPid','serverCreationUtc','serverImage','serverFileSha256','routingOverrides','toolSha256','sourceContractSha256','claimHeldExclusive','claimScope','originalCheckerReturned','gateGeneration','kind','sourceSha256','routeBackend','queryStats') 16384;$freshHash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($script:lastJsonBytes)).ToLowerInvariant();$freshLength=$script:lastJsonBytes.Length
 if($policy.routeBackend -cne 'WIN32_OWNER_PID_V1' -or $fresh.routeBackend -cne $policy.routeBackend){throw 'INITIAL_ROUTE_BACKEND'}
 CheckRouteStats $fresh.queryStats $fixture
 $metadataEvents=@($r.events|Where-Object event -CEQ 'checker-native-metadata-known');if($metadataEvents.Count -ne 1 -or $metadataEvents[0].bytes -ne $fresh.queryStats.metadataBytesKnown){throw 'INITIAL_NATIVE_METADATA_ACCOUNTING'}
 if($freshHash -cne $r.routeSha256 -or $fresh.kind -cne $expectedKind -or $fresh.gateGeneration -cne $h.generation -or $fresh.sourceSha256 -cne $r.checkerSourceSha256 -or $fresh.scope -cne $policy.scope -or $fresh.planId -cne $policy.planId){throw 'INITIAL_ROUTE_RECEIPT'}
 $age=([DateTime]::UtcNow-[DateTime]::Parse($fresh.checkedAtUtc).ToUniversalTime()).TotalSeconds
 if($age -lt 0 -or $age -ge 30){throw 'INITIAL_ROUTE_NOT_FRESH'}
 if(-not $fixture -and $policy.freshRouteProof.sha256 -cne $freshHash){throw 'INITIAL_ROUTE_ACTIVATION'}
 return [long]($receiptLength+$freshLength)
}

function CheckRunnerMaterialization($ad,$policy,$proof,[bool]$fixture){
 $h=$ad.runnerHandoff;$kind=if($fixture){'OFFLINE_FIXTURE'}else{'LIVE'}
 $keys=@('schema','ownerPid','scopeStartTick','initialProofStartTick','permitExpiresUtc','generation','permitSha256','approvalSha256','runnerSourceSha256','materializationSha256','initialProofSha256','postControlBytes','receiverControlBytes','kind','eventId')
 if(@(Compare-Object -CaseSensitive @($h.PSObject.Properties.Name|Sort-Object) @($keys|Sort-Object)).Count){throw 'RUNNER_HANDOFF_SCHEMA'}
 foreach($k in @('ownerPid','scopeStartTick','initialProofStartTick','postControlBytes','receiverControlBytes')){if(-not (IntField $h $k ([long]::MaxValue) 1)){throw 'RUNNER_HANDOFF_INTEGER'}}
 if($h.schema -cne 'RUNNER_HANDOFF_V1' -or $h.kind -cne $kind -or $h.ownerPid -ne $ad.ownerPid -or $h.scopeStartTick -ne $proof.scopeStartTick -or $h.generation -cne $ad.gateHandoff.generation -or $h.initialProofSha256 -cne $PredecessorProofSha -or $h.runnerSourceSha256 -cne 'f5574edba919f14414a2734427301499c3f9bbd9f01a078435ec19f06ba1e0d2' -or $policy.runnerSourceSha256 -cne $h.runnerSourceSha256 -or $policy.runnerPermit.sha256 -cne $h.permitSha256 -or $policy.runnerApproval.sha256 -cne $h.approvalSha256){throw 'RUNNER_ORIGINAL_HANDOFF_BINDING'}
 $cost=[long]0
 $permit=ReadJsonExact $policy.runnerPermit.path @('schema','authorizationId','mode','approvedForExecution','notBeforeUtc','expiresUtc','planId','runId','scope','home','evidenceRoot','sources','sourceSeal','review','product','tools','roles','operations','limits','fixtureScenario','routeBackend','globalIdleQualification') 32768
 $permitBytes=$script:lastJsonBytes.Length;$cost+=$permitBytes;$ph=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($script:lastJsonBytes)).ToLowerInvariant()
 if($permit.routeBackend -cne 'WIN32_OWNER_PID_V1' -or $policy.routeBackend -cne $permit.routeBackend){throw 'RUNNER_PERMIT_BACKEND'}
 if($ph -cne $h.permitSha256 -or $permit.schema -cne 'VIDEOKIT_PRODUCTION_RUNNER_PERMIT_V2' -or $permit.mode -cne $kind -or -not (BoolField $permit 'approvedForExecution' $true) -or $permit.scope -cne $policy.scope -or $permit.planId -cne $policy.planId -or $permit.runId -cne $policy.runId -or $permit.evidenceRoot -cne $root -or $permit.home -cne $script:controllerHomeRoot){throw 'RUNNER_PRIOR_PERMIT_BINDING'}
 if(-not $fixture -and $permit.fixtureScenario -cne 'NONE'){throw 'RUNNER_NO_LIVE_FAULTS'}
 if(($policy.globalIdleQualification|ConvertTo-Json -Depth 16 -Compress) -cne ($permit.globalIdleQualification|ConvertTo-Json -Depth 16 -Compress)){throw 'GLOBAL_IDLE_APPROVED_QUALIFICATION_CHANGED'}
 $now=[DateTimeOffset]::UtcNow;$nb=[DateTimeOffset]::Parse($permit.notBeforeUtc);$exp=[DateTimeOffset]::Parse($permit.expiresUtc)
 if($h.permitExpiresUtc -isnot [string] -or $h.permitExpiresUtc -cne $permit.expiresUtc){throw 'RUNNER_ORIGINAL_EXPIRY_BINDING'}
 if($now -lt $nb -or $now -ge $exp -or ($exp-$nb).TotalSeconds -le 0 -or ($exp-$nb).TotalSeconds -gt 900){throw 'RUNNER_PRIOR_PERMIT_EXPIRED'}
 $limits=@{wholeSeconds=600;gateSeconds=30;checkerSeconds=20;proofSeconds=10;outerSeconds=120;sdkChildren=7;concurrency=1;retry=0;metadataQueries=4;controlBytes=1048576;textBytes=3276800;payloadBytes=7629605;commandBytes=28672;localControlBytes=262144;minimumHandoffMs=1000}
 if(@(Compare-Object -CaseSensitive @($permit.limits.PSObject.Properties.Name|Sort-Object) @($limits.Keys|Sort-Object)).Count){throw 'RUNNER_LIMIT_SCHEMA'}
 foreach($k in $limits.Keys){if(-not (IntField $permit.limits $k $limits[$k] $limits[$k])){throw 'RUNNER_PERMISSION_LIMIT_CHANGED'}}
 if(-not (SameArgv @($permit.operations) @('local_gate','hold_claim','materialize_activation','materialize_policy','run_seven','release_claim')) -or $permit.roles.Count -ne 7){throw 'RUNNER_PERMISSION_OPERATIONS'}
 for($i=0;$i -lt 7;$i++){if($permit.roles[$i].id -cne $slots[$i].id -or -not (SameArgv @($permit.roles[$i].argv) @($slots[$i].argv)) -or $permit.roles[$i].maxTextBytes -ne $slots[$i].maxTextBytes -or $permit.roles[$i].qualificationSeconds -ne $slots[$i].qualificationSeconds -or $permit.roles[$i].maxBinaryBytes -ne 0){throw 'RUNNER_PERMISSION_ROLES'}}
 $approval=ReadJsonExact $policy.runnerApproval.path @('schema','mode','evidenceKind','sourceThreadId','sourceTurnId','instructionText','instructionSha256','approvedPermitSha256') 8192
 $cost+=$script:lastJsonBytes.Length;$ah=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($script:lastJsonBytes)).ToLowerInvariant()
 $evidenceKind=if($fixture){'OFFLINE_TEST_ONLY'}else{'COORDINATOR_EXECUTION_ORDER'};$instructionPrefix=if($fixture){'EXECUTE_OFFLINE_PERMIT '}else{'EXECUTE_LIVE_PERMIT '};$instruction=$instructionPrefix+$ph
 $ih=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($instruction))).ToLowerInvariant()
 if($ah -cne $h.approvalSha256 -or $approval.schema -cne 'VIDEOKIT_RUNNER_APPROVAL_EVIDENCE_V1' -or $approval.mode -cne $kind -or $approval.evidenceKind -cne $evidenceKind -or $approval.approvedPermitSha256 -cne $ph -or $approval.instructionText -cne $instruction -or $approval.instructionSha256 -cne $ih -or $approval.sourceThreadId -cne '01a107c3-2bf9-7fa0-94a0-234258ca6774'){throw 'RUNNER_PRIOR_APPROVAL_SOURCE'}
 $seal=ReadJsonExact $policy.runnerSources.path @('schema','sources') 16384;$cost+=$script:lastJsonBytes.Length
 $sh=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($script:lastJsonBytes)).ToLowerInvariant()
 if($sh -cne $permit.sourceSeal.sha256 -or $sh -cne $policy.runnerSources.sha256 -or $seal.schema -cne 'PRODUCTION_RUNNER_SOURCE_SEAL_V1'){throw 'RUNNER_REVIEWED_SOURCE_SEAL'}
 $srcKeys=@('tools/production_runner.py','tools/entry_gates.py','tools/outer_owner.py','tools/capture_android02.ps1','tools/win32_route.py','tools/runtime_binding.py','reference/current-runtime-identity.json','reference/exact-seven-role-plan.json','reference/gate-sources.json','selfchecks/route_fixture.py','selfchecks/capture_fixture.py','reference/route-backend-contract.json','selfchecks/route_model.py','tools/admission_checks.ps1','tools/fact_collector.py','reference/fact-plan.json','selfchecks/fact_fixture.py')
 foreach($obj in @($permit.sources,$seal.sources)){if(@(Compare-Object -CaseSensitive @($obj.PSObject.Properties.Name|Sort-Object) @($srcKeys|Sort-Object)).Count){throw 'RUNNER_EXACT_SOURCE_SET'}}
 foreach($key in $srcKeys){$sourcePath=Join-Path 'D:\CodexProjects\VideoKit\docs\coder\d1android02-global-idle-contract03-fix' $key;NoLinks $sourcePath;if((Digest $sourcePath) -cne $seal.sources.$key -or $seal.sources.$key -cne $permit.sources.$key){throw 'RUNNER_SOURCE_CHANGED'}}
 $mp=Join-Path $root 'runner-materialization.json';$m=ReadJsonExact $mp @('schema','scope','planId','kind','generation','ownerPid','scopeStartTick','initialProofStartTick','permitSha256','approvalSha256','runnerSourceSha256','initialProofSha256','activationSha256','policySha256','preGateControlBytes','events','controlBeforeReceipt','receiptWriteBytes','candidateOnlyWriterCloseNotProven') 16384
 $ml=$script:lastJsonBytes.Length;$cost+=$ml;$mh=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($script:lastJsonBytes)).ToLowerInvariant()
 if($mh -cne $h.materializationSha256 -or $m.schema -cne 'RUNNER_MATERIALIZATION_RETURN_V1' -or $m.scope -cne $policy.scope -or $m.planId -cne $policy.planId -or $m.kind -cne $kind -or $m.generation -cne $h.generation -or $m.ownerPid -ne $ad.ownerPid -or $m.scopeStartTick -ne $proof.scopeStartTick -or $m.permitSha256 -cne $ph -or $m.approvalSha256 -cne $ah -or $m.runnerSourceSha256 -cne $h.runnerSourceSha256 -or $m.initialProofSha256 -cne $PredecessorProofSha -or $m.policySha256 -cne (Digest $policyPath) -or -not (BoolField $m 'candidateOnlyWriterCloseNotProven' $true)){throw 'RUNNER_MATERIALIZATION_ORIGINAL'}
 $act=ReadJsonExact $policy.authorization.path @('schema','scope','planId','runId','entrySha256','planSha256','toolCandidateSealSha256','productSealSha256','reviewSha256','toolSha256','evidenceRoot','wholeWallSeconds','localProofSeconds','outerSeconds','freshRouteProofSha256','initialPredecessorProofSha256','outerOwnerSha256','outerPythonSha256','runtimeIdentitySha256','runtimeBindingSourceSha256','approvedForExecution','runnerPermitSha256','runnerSourceSha256','runnerApprovalSha256','routeBackend') 8192
 $al=$script:lastJsonBytes.Length;$cost+=$al;$actHash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($script:lastJsonBytes)).ToLowerInvariant()
 if($act.routeBackend -cne $permit.routeBackend){throw 'RUNNER_ACTIVATION_BACKEND'}
 if($actHash -cne $m.activationSha256 -or $actHash -cne $policy.authorization.sha256 -or $act.runnerPermitSha256 -cne $ph -or $act.runnerApprovalSha256 -cne $ah -or $act.runnerSourceSha256 -cne $h.runnerSourceSha256 -or -not (BoolField $act 'approvedForExecution' $true) -or $act.scope -cne $policy.scope -or $act.initialPredecessorProofSha256 -cne $PredecessorProofSha -or $act.freshRouteProofSha256 -cne $policy.freshRouteProof.sha256 -or $act.wholeWallSeconds -ne 600 -or $act.localProofSeconds -ne 10 -or $act.outerSeconds -ne 120){throw 'RUNNER_DERIVED_ACTIVATION_BINDING'}
 foreach($k in @('preGateControlBytes','controlBeforeReceipt','receiptWriteBytes')){if(-not (IntField $m $k 262144 1)){throw 'RUNNER_MATERIALIZATION_INTEGER'}}
 if(-not (IntField $m 'initialProofStartTick' ([long]::MaxValue) $proof.scopeStartTick) -or $m.initialProofStartTick -ne $h.initialProofStartTick){throw 'RUNNER_ORIGINAL_PROOF_START'}
 $names=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal);$sum=[long]0
 foreach($e in $m.events){if(@(Compare-Object -CaseSensitive @($e.PSObject.Properties.Name|Sort-Object) @('bytes','event')).Count -or $e.event -isnot [string] -or -not $names.Add($e.event) -or -not (IntField $e 'bytes' 131072)){throw 'RUNNER_POST_ONCE_EVENT'};$sum+=$e.bytes}
 $expectedNames=@('permit-recheck','approval-recheck','materializer-route-read','materializer-proof-read','activation-write','policy-write','activation-readback','policy-readback')
 if(@(Compare-Object -CaseSensitive @($names|Sort-Object) @($expectedNames|Sort-Object)).Count){throw 'RUNNER_POST_EVENT_SET'}
 foreach($e in $m.events){$expected=if($e.event -ceq 'permit-recheck'){$permitBytes}elseif($e.event -ceq 'approval-recheck'){(Get-Item -LiteralPath $policy.runnerApproval.path).Length}elseif($e.event -ceq 'materializer-route-read'){(Get-Item -LiteralPath $policy.freshRouteProof.path).Length}elseif($e.event -ceq 'materializer-proof-read'){$proof.proofWriteBytes}elseif($e.event -cin @('activation-write','activation-readback')){$al}else{(Get-Item -LiteralPath $policyPath).Length};if($e.bytes -ne $expected){throw 'RUNNER_ACTUAL_MATERIALIZATION_EVENT_BYTES'}}
 $pre=[long]0;foreach($e in $script:initialGateReceipt.events){if($e.event.StartsWith('runner-pre:',[StringComparison]::Ordinal)){$pre+=$e.bytes}}
 if($pre -ne $m.preGateControlBytes -or $sum -ne $m.controlBeforeReceipt -or $m.receiptWriteBytes -ne $ml -or $h.postControlBytes -ne $sum+$ml -or $h.receiverControlBytes -ne (Get-Item -LiteralPath $policyPath).Length+$al+$ml){throw 'RUNNER_POST_DELTA_RESET_OR_DUPLICATE'}
 $expectedEvent=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($policy.scope+'|runner-materialization|'+$PredecessorProofSha+'|'+$mh+'|'+$m.policySha256))).ToLowerInvariant()
 if($h.eventId -cne $expectedEvent -or $proof.batchGroups.control+[long]$h.postControlBytes+[long]$h.receiverControlBytes -gt 262144){throw 'RUNNER_UNIQUE_POST_DELTA_OR_LOCAL_CAP'}
 $script:runnerPostControl=[long]$h.postControlBytes+[long]$h.receiverControlBytes
 return [long]($cost+$script:policyBodyBytes+$script:activationStartupBytes)
}
function RunnerFinalStartGate($ad,$policy,[long]$scopeTick,[int]$roleIndex,[bool]$fixture){
 # Last controlled point before actual SDK Process.Start; no new IO/query/clock.
 $h=$ad.runnerHandoff;$kind=if($fixture){'OFFLINE_FIXTURE'}else{'LIVE'}
 foreach($k in @('ownerPid','scopeStartTick','initialProofStartTick')){if(-not (IntField $h $k ([long]::MaxValue) 1)){throw 'RUNNER_FINAL_START_INTEGER'}}
 if($h.schema -cne 'RUNNER_HANDOFF_V1' -or $h.ownerPid -ne $ad.ownerPid -or $h.scopeStartTick -ne $scopeTick -or $h.runnerSourceSha256 -cne 'f5574edba919f14414a2734427301499c3f9bbd9f01a078435ec19f06ba1e0d2' -or $policy.runnerSourceSha256 -cne $h.runnerSourceSha256 -or $h.permitSha256 -cne $policy.runnerPermit.sha256 -or $h.approvalSha256 -cne $policy.runnerApproval.sha256 -or $h.kind -cne $kind){throw 'RUNNER_FINAL_START_SOURCE'}
 if($h.permitExpiresUtc -isnot [string] -or [DateTimeOffset]::UtcNow -ge [DateTimeOffset]::Parse($h.permitExpiresUtc)){throw 'RUNNER_FINAL_START_EXPIRED'}
 $now=[Environment]::TickCount64
 if($now -lt $scopeTick -or $now-$scopeTick -ge 600000 -or $h.initialProofStartTick -lt $scopeTick -or $h.initialProofStartTick -gt $now){throw 'RUNNER_FINAL_START_WHOLE_OR_CLOCK'}
 if($roleIndex -eq 0 -and ($now-$scopeTick -ge 30000 -or $now-$h.initialProofStartTick -ge 10000)){throw 'RUNNER_FINAL_START_ORIGINAL_MINIMUM_WINDOW'}
}


$script:GICollectorSha256='69701c9b28bd338142bb5d5ecbd6d8678b8fb8de5e82d19e5cfd2e879d684ed4'
$script:GIFactPlanSha256='f8fc21137931fb898c4b809047768fc029e011f24d9d995e3e94ed84cb7c105d'
# Passive functions incorporated into the pinned admission_checks.ps1 by build_candidate.py.
# A semantic PASS is internal only: the unchanged original outer owner must still
# prove this controller's actual return, resource closure, and whole ledger.
function GIExact($o,[string[]]$keys){
 if($o -isnot [pscustomobject] -or @(Compare-Object -CaseSensitive @($o.PSObject.Properties.Name|Sort-Object) @($keys|Sort-Object)).Count){throw 'GLOBAL_QUAL_SCHEMA'}
}
function GISha($s){return $s -is [string] -and $s -cmatch '^[a-f0-9]{64}$'}
function GIInt($n,[long]$lo,[long]$hi){return ($n -is [int] -or $n -is [long]) -and $n -ge $lo -and $n -le $hi}
function GIQualification($q,$ctx){
 GIExact $ctx @('scope','runId','mode','rawSha256','rawBytes','captureBodyReturned','sourceSealSha256','planSha256','reviewEvidenceSha256','nowUtc')
 if($ctx.captureBodyReturned -isnot [bool] -or -not $ctx.captureBodyReturned){throw 'GLOBAL_CAPTURE_RETURN_UNPROVEN'}
 GIExact $q @('schema','mode','fixtureOnly','targetScope','targetRunId','targetSourceSealSha256','targetPlanSha256','factScope','factAuthoritySha256','factApprovalSha256','factCaptureReceiptSha256','factOuterReturnSha256','collectorSourceSha256','factPlanSha256','rawSha256','rawBytes','routeProofSha256','sdkSha256','collectedAtUtc','expiresAtUtc','originalReturn','grammar','serial','model','api','fingerprint','user','home','services','systemPackages','reviewEvidenceSha256')
 if([Text.Encoding]::UTF8.GetByteCount(($q|ConvertTo-Json -Depth 16 -Compress)) -gt 16384){throw 'GLOBAL_QUAL_BYTE_BOUND'}
 foreach($k in @('targetScope','targetSourceSealSha256','targetPlanSha256','factScope','factAuthoritySha256','factApprovalSha256','factCaptureReceiptSha256','factOuterReturnSha256','collectorSourceSha256','factPlanSha256','rawSha256','routeProofSha256','sdkSha256','reviewEvidenceSha256')){if(-not (GISha $q.$k)){throw 'GLOBAL_QUAL_HASH'}}
 if($q.schema -cne 'GLOBAL_IDLE_QUALIFICATION_V1' -or $q.targetScope -cne $ctx.scope -or $q.targetRunId -cne $ctx.runId -or $q.targetSourceSealSha256 -cne $ctx.sourceSealSha256 -or $q.targetPlanSha256 -cne $ctx.planSha256 -or $q.factScope -ceq $q.targetScope -or $q.reviewEvidenceSha256 -cne $ctx.reviewEvidenceSha256){throw 'GLOBAL_QUAL_SCOPE_OR_SOURCE'}
 if($ctx.mode -cnotin @('LIVE','OFFLINE_FIXTURE') -or $q.mode -cne $ctx.mode -or $q.fixtureOnly -isnot [bool] -or $q.fixtureOnly -ne ($ctx.mode -ceq 'OFFLINE_FIXTURE')){throw 'GLOBAL_FIXTURE_MODE_BINDING'}
 if($q.collectorSourceSha256 -cne $script:GICollectorSha256 -or $q.factPlanSha256 -cne $script:GIFactPlanSha256 -or $q.sdkSha256 -cne 'b4a6b455702684652cccf7b46258b29e653538904359a58fd4931cf3ef286b3f'){throw 'GLOBAL_FACT_PRODUCER_PIN'}
 if(-not (GIInt $q.rawBytes 1 139264) -or $q.grammar -cne 'API31_APP_PERS_V1' -or $q.serial -cne 'HA1Q6WXR' -or $q.model -cne 'TB138FC' -or -not (GIInt $q.api 31 31) -or -not (GIInt $q.user 0 0) -or $q.fingerprint -isnot [string] -or $q.fingerprint.Length -lt 8 -or $q.fingerprint.Length -gt 256){throw 'GLOBAL_FIRMWARE_UNPROVEN'}
 if($ctx.mode -ceq 'LIVE' -and $q.fingerprint -clike '*FIXTURE*'){throw 'GLOBAL_FIXTURE_NOT_LIVE'}
 foreach($stamp in @($q.collectedAtUtc,$q.expiresAtUtc)){if($stamp -isnot [string] -or $stamp -cnotmatch '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,7})?(?:Z|\+00:00)$'){throw 'GLOBAL_FACT_UTC_FORMAT'}}
 $now=[DateTimeOffset]::Parse($ctx.nowUtc);$from=[DateTimeOffset]::Parse($q.collectedAtUtc);$to=[DateTimeOffset]::Parse($q.expiresAtUtc)
 if($now -lt $from -or $now -ge $to -or ($to-$from).TotalSeconds -gt 300 -or ($to-$from).TotalSeconds -le 0){throw 'GLOBAL_FACT_STALE_OR_FUTURE'}
 GIExact $q.originalReturn @('waitReturned','stdoutEOF','stderrEOF','originalPipesClosed','originalHandleClosed','controllerReturned','unknown','exitCode')
 foreach($k in @('waitReturned','stdoutEOF','stderrEOF','originalPipesClosed','originalHandleClosed','controllerReturned')){if($q.originalReturn.$k -isnot [bool] -or -not $q.originalReturn.$k){throw 'GLOBAL_FACT_ORIGINAL_RETURN_UNPROVEN'}}
 if($q.originalReturn.unknown -isnot [bool] -or $q.originalReturn.unknown -or -not (GIInt $q.originalReturn.exitCode 0 0)){throw 'GLOBAL_FACT_UNKNOWN_OR_FAILED'}
 GIExact $q.home @('package','component','process','user','uid','systemFlag')
 if($q.home.package -cnotmatch '^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z0-9_]+)+$' -or $q.home.component -cnotmatch '^[A-Za-z_][A-Za-z0-9_.]*$' -or $q.home.process -cnotmatch '^[A-Za-z_][A-Za-z0-9_.]*(?::[A-Za-z0-9_.]+)*$' -or -not (GIInt $q.home.user 0 0) -or -not (GIInt $q.home.uid 10000 99999) -or $q.home.systemFlag -isnot [bool] -or -not $q.home.systemFlag){throw 'GLOBAL_HOME_FACT_UNPROVEN'}
 if($q.services -isnot [array] -or $q.services.Count -gt 68 -or $q.systemPackages -isnot [array] -or $q.systemPackages.Count -gt 128){throw 'GLOBAL_POLICY_BOUND'}
 $seen=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
 foreach($p in $q.systemPackages){GIExact $p @('package','uid','systemFlag');if($p.package -cnotmatch '^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z0-9_]+)*$' -or -not (GIInt $p.uid 0 2147483647) -or $p.systemFlag -isnot [bool] -or -not $p.systemFlag -or -not $seen.Add($p.package)){throw 'GLOBAL_SYSTEM_FACT_UNPROVEN'}}
 if(@($q.systemPackages|Where-Object {$_.package -ceq $q.home.package -and $_.uid -eq $q.home.uid}).Count -ne 1){throw 'GLOBAL_HOME_SYSTEM_UID_UNPROVEN'}
 $serviceSeen=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
 foreach($s in $q.services){
  GIExact $s @('packages','process','user','uid','kind','state','category','firmware','evidenceSha256','factScope','validFromUtc','validToUtc','range')
  if($s.packages -isnot [array] -or $s.packages.Count -ne 1 -or $s.process -cnotmatch '^[A-Za-z_.][A-Za-z0-9_.]*(?::[A-Za-z0-9_.]+)*$' -or -not (GIInt $s.user 0 0) -or -not (GIInt $s.uid 0 99999) -or $s.kind -cnotin @('APP','PERS') -or -not (GIInt $s.state 0 6) -or $s.state -cin @(2,3) -or $s.category -cne 'NONCONTENDING_SYSTEM_SERVICE' -or $s.firmware -cne $q.fingerprint -or -not (GISha $s.evidenceSha256) -or $s.factScope -cne $q.factScope -or $s.range -cne 'EXACT_SNAPSHOT' -or $s.validFromUtc -cne $q.collectedAtUtc -or $s.validToUtc -cne $q.expiresAtUtc -or -not $serviceSeen.Add($s.process+'|'+$s.uid)){throw 'GLOBAL_SERVICE_POLICY_UNPROVEN'}
  if(@($q.systemPackages|Where-Object {$_.package -ceq $s.packages[0] -and $_.uid -eq $s.uid}).Count -ne 1){throw 'GLOBAL_SERVICE_SYSTEM_UID_UNPROVEN'}
 }
 return $q
}

# Bounded API31 parser. No IO/query. Qualification is an immutable permit input.
function Get-GlobalIdleDecision([string]$Text,$Qualification,$Context){
 $d=[ordered]@{schema='GLOBAL_IDLE_CONTRACT02_V1';qualified=$false;productionPassCapable=$true;status='BLOCKED_UNPROVEN';reason='GLOBAL_FORMAT_UNPROVEN';stage='format';firstRejectedRecord=$null;processes=@();resumed=@();focused=@();systemPackageFacts='NOT_QUERIED_NOT_PROVEN';defaultHomeFacts='NOT_QUERIED_NOT_PROVEN';api31NumericEnum='343c60effa4ce83ce42296527bae8bd4341a9da942a670a83b1c86a7ef307881';captureQualification='NOT_BOUND_BY_THIS_PURE_TEXT_DIAGNOSTIC'}
 try{
 if($null -eq $Text){return $d}
 if($Text -cmatch '[\x00-\x08\x0b\x0c\x0e-\x1f]'){$d.reason='GLOBAL_INVALID_CONTROL_CHARACTER';return $d}
 try{if([Text.UTF8Encoding]::new($false,$true).GetByteCount($Text) -gt 851968){$d.reason='GLOBAL_INPUT_BOUND';return $d}}catch{return $d}
 $lines=@($Text.Trim().Split("`n")|ForEach-Object {$_.TrimEnd("`r")})
 if($lines.Count -lt 5 -or $lines[0] -cne 'ANDROID02_GLOBAL_BEGIN' -or $lines[-1] -cne 'ANDROID02_GLOBAL_COMPLETE'){return $d}
 $begin=[regex]::Matches($Text,'(?m)^ANDROID02_GLOBAL_BEGIN\r*$');$split=[regex]::Matches($Text,'(?m)^ANDROID02_GLOBAL_ACTIVITIES\r*$');$end=[regex]::Matches($Text,'(?m)^ANDROID02_GLOBAL_COMPLETE\r*$')
 if($begin.Count -ne 1 -or $split.Count -ne 1 -or $end.Count -ne 1 -or [regex]::Matches($Text,'ANDROID02_GLOBAL_(BEGIN|ACTIVITIES|COMPLETE)').Count -ne 3 -or $split[0].Index -le $begin[0].Index -or $end[0].Index -le $split[0].Index){return $d}
 # Preserve all three original global instrumentation predicates, before any
 # allowlist/process exemption. A system-looking package cannot bypass them.
 if($Text -cmatch '(?m)^\s*mInstr=(?!null\b)\S' -or $Text -cmatch '(?m)^\s*Instrumentation #\d+:' -or $Text -cmatch '(?m)^.*\(instrumentation\)\s*$'){$d.reason='ENV_WAIT_OTHER_PROJECT_OR_TEST_OCCUPIED';$d.status='BLOCKED_OCCUPIED';if($Text -cmatch '(?m)^\s*mInstr=(?!null\b|ActiveInstrumentation\{)\S'){$d.reason='GLOBAL_INSTRUMENTATION_FORMAT_UNPROVEN';$d.status='BLOCKED_UNPROVEN'};$d.stage='instrumentation';return $d}
 if($Text -cmatch '(?m)^\s*mInstr=(?!null[ \t]*\r*$)' -or $Text -cmatch '(?m)^\s*Instrumentation #(?![0-9]+:)'){$d.reason='GLOBAL_INSTRUMENTATION_FORMAT_UNPROVEN';return $d}
 $proc=$Text.Substring($begin[0].Index+$begin[0].Length,$split[0].Index-$begin[0].Index-$begin[0].Length)
 $activities=$Text.Substring($split[0].Index+$split[0].Length,$end[0].Index-$split[0].Index-$split[0].Length)
 if($proc -cnotmatch 'ACTIVITY MANAGER RUNNING PROCESSES' -or $activities -cnotmatch 'ACTIVITY MANAGER ACTIVITIES'){return $d}
 $headerPattern='(?m)^  \*(?<kind>APP|PERS)\*[ \t]+UID (?<uid>\d+) ProcessRecord\{(?<token>[A-Za-z0-9]+) (?<pid>\d+):(?<process>[^\s/}]+)/(?<user>[^\s}]+)\}[^\r\n]*\r*$'
 $headers=[regex]::Matches($proc,$headerPattern)
 $suspects=[Collections.Generic.HashSet[int]]::new()
 $summary=[regex]::Match($proc,'(?m)^  (?:Process OOM control|UID states|UID validation|Process LRU list|Total persistent processes):?')
 $recordArea=if($summary.Success){$proc.Substring(0,$summary.Index)}else{$proc}
 foreach($m in [regex]::Matches($proc,'(?m)^[ \t]*\*[^\r\n]*(?:\*|ProcessRecord\{)[^\r\n]*\r*$')){[void]$suspects.Add($m.Index)}
 foreach($m in [regex]::Matches($recordArea,'(?m)^[ \t]{0,2}(?=[^ \t\r\n])(?=[^\r\n]*ProcessRecord\{)[^\r\n]+\r*$')){[void]$suspects.Add($m.Index)}
 foreach($m in [regex]::Matches($proc,'(?m)^[ \t]{0,2}(?:(?i:UID)[^\r\n]*ProcessRecord\{|ProcessRecord\{)[^\r\n]*\r*$')){[void]$suspects.Add($m.Index)}
 foreach($h in $headers){if(-not $suspects.Contains($h.Index) -or ($summary.Success -and $h.Index -ge $summary.Index)){$d.reason='GLOBAL_PROCESS_HEADERS_UNPROVEN';return $d}}
 $prefixStop=if($headers.Count -gt 0){$headers[0].Index}else{$proc.Length}
 if($proc.Substring(0,$prefixStop) -cmatch '(?m)^    (?:user #|packageList=|curProcState=)'){$d.reason='GLOBAL_PROCESS_HEADERS_UNPROVEN';return $d}
 $anyHeaders=$suspects
 if($headers.Count -eq 0 -or $headers.Count -ne $anyHeaders.Count){$d.reason='GLOBAL_PROCESS_HEADERS_UNPROVEN';return $d}
 $records=[Collections.Generic.List[object]]::new();$pids=[Collections.Generic.HashSet[long]]::new();$tokensSeen=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
 for($i=0;$i -lt $headers.Count;$i++){
  $h=$headers[$i];$stop=if($i+1 -lt $headers.Count){$headers[$i+1].Index}else{$tail=[regex]::Match($proc.Substring($h.Index+$h.Length),'(?m)^  (?:Process OOM control|UID states|UID validation|Process LRU list|Total persistent processes):?');if($tail.Success){$h.Index+$h.Length+$tail.Index}else{$proc.Length}};$body=$proc.Substring($h.Index+$h.Length,$stop-$h.Index-$h.Length)
  $uid=[long]0;$pidValue=[long]0
  if(-not [long]::TryParse($h.Groups['uid'].Value,[ref]$uid) -or $uid -gt 2147483647 -or -not [long]::TryParse($h.Groups['pid'].Value,[ref]$pidValue) -or $pidValue -le 0 -or $pidValue -gt 2147483647){$d.reason='GLOBAL_PROCESS_ID_UNPROVEN';return $d}
  if(-not $pids.Add($pidValue) -or -not $tokensSeen.Add($h.Groups['token'].Value)){$d.reason='GLOBAL_DUPLICATE_PROCESS_IDENTITY_UNPROVEN';return $d}
  # Admitted archive grammar: two-space top-level header / four-space owner
  # fields. Six-space UID summaries after the last record are not its state.
  $states=[regex]::Matches($body,'(?m)^    curProcState=([0-9][^ \t\r\n]*)(?=[ \t\r\n]|$)');$users=[regex]::Matches($body,'(?m)^    user #(\d+) uid=(\d+)\b');$packages=[regex]::Matches($body,'(?m)^    packageList=\{([^}\r\n]*)\}')
  if($states.Count -ne [regex]::Matches($body,'(?m)^    curProcState=').Count -or $users.Count -ne [regex]::Matches($body,'(?m)^    user #').Count -or $packages.Count -ne [regex]::Matches($body,'(?m)^    packageList=').Count){$d.reason='GLOBAL_OWN_FIELD_FORMAT_UNPROVEN';return $d}
  $stateValue=[long]0
  if($states.Count -ne 1 -or $states[0].Groups[1].Value -cnotmatch '^(?:0|[1-9][0-9]?)$' -or [regex]::IsMatch($body,'(?m)^    curProcState=[^\r\n]*\bcurProcState=') -or -not [long]::TryParse($states[0].Groups[1].Value,[ref]$stateValue) -or $stateValue -gt 19){$d.reason='GLOBAL_PROCESS_STATE_UNPROVEN';return $d}
  $derivedUser=[long][Math]::Floor($uid/100000);$appId=$uid%100000
  if($users.Count -ne 1 -or [long]$users[0].Groups[2].Value -ne $uid -or [long]$users[0].Groups[1].Value -ne $derivedUser){$d.reason='GLOBAL_PROCESS_USER_UNPROVEN';return $d}
  $userSpec=$h.Groups['user'].Value;$userMatch=[regex]::Match($userSpec,'^u(\d+)[as]\d+(?:i\d+)?$')
  $expectedToken='u'+$derivedUser+$(if($appId -ge 10000){'a'+($appId-10000)}else{'s'+$appId})
  $isolated=($userSpec -cmatch '^u\d+(?:a\d+)?i\d+$|^u\d+ai\d+$')
  if(-not $isolated -and $userSpec -cne $expectedToken -and -not($appId -lt 10000 -and $userSpec -ceq $uid.ToString())){$d.reason='GLOBAL_PROCESS_USER_TOKEN_UNPROVEN';return $d}
  $pkg=@();if($packages.Count -eq 1){$pkg=@($packages[0].Groups[1].Value.Split(',')|ForEach-Object {$_.Trim()})}
  if($packages.Count -ne 1 -or $pkg.Count -ne @($pkg|Sort-Object -Unique -CaseSensitive).Count -or $pkg.Count -eq 0 -or @($pkg|Where-Object {$_ -cnotmatch '^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z0-9_]+)*$'}).Count){$d.reason='GLOBAL_PACKAGE_MAPPING_UNPROVEN';return $d}
  $r=[ordered]@{index=$i+1;kind=$h.Groups['kind'].Value;token=$h.Groups['token'].Value;uid=$uid;pidFromText=$pidValue;processName=$h.Groups['process'].Value;userSpec=$h.Groups['user'].Value;user=$derivedUser;appId=$appId;isolatedOwnerUnproven=$isolated;state=$stateValue;packages=$pkg;sourceDir=@([regex]::Matches($body,'(?m)^    dir=(\S+)')|ForEach-Object {$_.Groups[1].Value});line=1+[regex]::Matches($Text.Substring(0,$begin[0].Index+$begin[0].Length+$h.Index),'\n').Count}
  $records.Add($r)
 }
 $d.processes=$records.ToArray()
 # Resume/focus observations are reported even when the earlier process guard
 # blocks. They are separate evidence, never an idle override.
 $resumePattern='(?m)^[ \t]*(?:mResumedActivity|topResumedActivity)\s*[:=]\s*ActivityRecord\{(?<token>\S+) u(?<user>\d+) (?<package>[A-Za-z0-9_.]+)/(?<activity>[^\s}]+) (?<task>t\d+)[^}\r\n]*\}'
 $resumes=@([regex]::Matches($activities,$resumePattern)|ForEach-Object {@{token=$_.Groups['token'].Value;task=$_.Groups['task'].Value;display='NOT_BOUND';user=[long]$_.Groups['user'].Value;package=$_.Groups['package'].Value;activity=$_.Groups['activity'].Value}})
 $focusPattern='(?m)^[ \t]*mFocusedApp\s*[:=]\s*ActivityRecord\{(?<token>\S+) u(?<user>\d+) (?<package>[A-Za-z0-9_.]+)/(?<activity>[^\s}]+) (?<task>t\d+)[^}\r\n]*\}'
 $focus=@([regex]::Matches($activities,$focusPattern)|ForEach-Object {@{token=$_.Groups['token'].Value;task=$_.Groups['task'].Value;display='NOT_BOUND';user=[long]$_.Groups['user'].Value;package=$_.Groups['package'].Value;activity=$_.Groups['activity'].Value}})
 $d.resumed=$resumes;$d.focused=$focus
 $d.stage='resume'
 $resumeLabels=[regex]::Matches($activities,'(?m)^[ \t]*(?:mResumedActivity|topResumedActivity)\s*[:=]')
 $focusLabels=[regex]::Matches($activities,'(?m)^[ \t]*mFocusedApp\s*[:=]')
 if($resumes.Count -eq 0 -or $resumes.Count -ne $resumeLabels.Count -or $focus.Count -ne $focusLabels.Count){$d.reason='GLOBAL_RESUME_OR_FOCUS_UNPROVEN';return $d}
 if($resumes.Count -ne 1){$d.reason='ENV_WAIT_MULTIPLE_RESUMED_IDENTITIES_UNPROVEN';return $d}
 $unique=@($resumes|ForEach-Object {[string]$_.user+'|'+$_.package+'|'+$_.activity+'|'+$_.token+'|'+$_.task})

 foreach($r in $focus){if(($r.user.ToString()+'|'+$r.package+'|'+$r.activity+'|'+$r.token+'|'+$r.task) -cne $unique[0]){$d.reason='GLOBAL_FOCUS_RESUME_DISAGREEMENT';return $d}}

 # One admitted display section, bound to the unique resumed/focused record.
 $displays=[regex]::Matches($activities,'(?m)^Display #(\d+) \(activities from top to bottom\):\r*$')
 if($displays.Count -ne 1 -or $displays.Count -ne [regex]::Matches($activities,'(?m)^Display #').Count -or $displays[0].Groups[1].Value -cne '0' -or $activities -cmatch '(?m)\b(?:mDisplayId|displayId)=[1-9][0-9]*\b'){$d.reason='GLOBAL_DISPLAY_UNPROVEN';return $d}
 if($focus.Count -ne 1){$d.reason='GLOBAL_FOCUS_UNPROVEN';return $d}
 try{$q=GIQualification $Qualification $Context}catch{$d.reason=$_.Exception.Message;return $d}
 $rawBytes=[Text.UTF8Encoding]::new($false,$true).GetBytes($Text)
 if($Context.rawSha256 -cne [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($rawBytes)).ToLowerInvariant() -or $Context.rawBytes -ne $rawBytes.Length){$d.reason='GLOBAL_RAW_BINDING';return $d}
 $homeIdentity=$q.home;$r=$resumes[0];$component=if($r.activity.StartsWith('.')){$r.package+$r.activity}else{$r.activity}
 if($r.user -ne $homeIdentity.user -or $r.package -cne $homeIdentity.package){$d.reason='ENV_WAIT_FOREIGN_RESUMED';$d.status='BLOCKED_OCCUPIED';return $d}
 if($component -cne $homeIdentity.component){$d.reason='GLOBAL_HOME_COMPONENT_UNPROVEN';return $d}
 $homeProcesses=@($records|Where-Object {$_.processName -ceq $homeIdentity.process -and $_.uid -eq $homeIdentity.uid -and $_.user -eq $homeIdentity.user -and $_.packages.Count -eq 1 -and $_.packages[0] -ceq $homeIdentity.package})
 if($homeProcesses.Count -ne 1 -or $homeProcesses[0].state -ne 2){$d.reason='GLOBAL_HOME_PROCESS_STATE_UNPROVEN';return $d}
 $hist=[regex]::Matches($activities,'(?m)^      \* Hist #[0-9]+: ActivityRecord\{(?<token>[A-Za-z0-9]+) u(?<user>[0-9]+) (?<package>[A-Za-z0-9_.]+)/(?<activity>[^\s}]+) (?<task>t[0-9]+)[^}\r\n]*\}')
 if($hist.Count -ne 1 -or [regex]::Matches($activities,'(?m)^      \* Hist #').Count -ne 1){$d.reason='GLOBAL_HOME_ACTIVITY_DETAIL_UNPROVEN';return $d}
 foreach($k in @('token','user','package','activity','task')){if($hist[0].Groups[$k].Value -cne [string]$resumes[0].$k){$d.reason='GLOBAL_HOME_ACTIVITY_IDENTITY_UNPROVEN';return $d}}
 $detail=$activities.Substring($hist[0].Index+$hist[0].Length)
 $detailStop=[regex]::Match($detail,'(?m)^(?:      \* Hist #|    \* Task\{|  RootTask #|  Display:|Display #)');if($detailStop.Success){$detail=$detail.Substring(0,$detailStop.Index)}
 $apps=[regex]::Matches($detail,'(?m)^          app=ProcessRecord\{(?<token>[A-Za-z0-9]+) (?<pid>[0-9]+):(?<process>[^\s/}]+)/(?<user>[^\s}]+)\}\r*$')
 $owners=[regex]::Matches($detail,'(?m)^          packageName=(?<package>\S+) processName=(?<process>\S+)\r*$')
 $components=[regex]::Matches($detail,'(?m)^          mActivityComponent=(?<component>\S+)\r*$')
 if($apps.Count -ne 1 -or $owners.Count -ne 1 -or $components.Count -ne 1 -or [regex]::Matches($detail,'(?m)^          app=').Count -ne 1 -or [regex]::Matches($detail,'(?m)^          state=').Count -ne 1 -or $detail -cnotmatch '(?m)^          state=RESUMED stopped=false delayedResume=false finishing=false(?:\s|$)' -or $detail -cnotmatch '(?m)^          mVisibleRequested=true mVisible=true(?:\s|$)'){$d.reason='GLOBAL_HOME_ACTIVITY_OWNER_UNPROVEN';return $d}
 $hp=$homeProcesses[0];$a=$apps[0]
 $hc=$components[0].Groups['component'].Value.Split('/');if($hc.Count -ne 2){$d.reason='GLOBAL_HOME_ACTIVITY_COMPONENT_UNPROVEN';return $d}
 $fullComponent=if($hc[1].StartsWith('.')){$hc[0]+$hc[1]}else{$hc[1]}
 if($a.Groups['token'].Value -cne $hp.token -or $a.Groups['pid'].Value -cne [string]$hp.pidFromText -or $a.Groups['process'].Value -cne $hp.processName -or $a.Groups['user'].Value -cne $hp.userSpec -or $owners[0].Groups['package'].Value -cne $homeIdentity.package -or $owners[0].Groups['process'].Value -cne $homeIdentity.process -or $hc[0] -cne $homeIdentity.package -or $fullComponent -cne $homeIdentity.component){$d.reason='GLOBAL_HOME_ACTIVITY_PROCESS_BINDING';return $d}
 foreach($r in $records){
  $d.firstRejectedRecord=$r
  if($r.isolatedOwnerUnproven){$d.reason='GLOBAL_ISOLATED_OWNER_UNPROVEN';return $d}
  if($r.packages.Count -ne 1){$d.reason='GLOBAL_SHARED_OWNER_UNPROVEN';return $d}
  if($r.user -ne 0){$d.reason='GLOBAL_OTHER_USER_UNPROVEN';return $d}
  # Package/process mapping is complete, never a suffix-derived identity.
  # Nonstandard system process names require the exact reviewed service entry.
  $services=@($q.services|Where-Object {$_.process -ceq $r.processName -and $_.uid -eq $r.uid -and $_.user -eq $r.user -and $_.kind -ceq $r.kind -and $_.state -eq $r.state -and $_.packages[0] -ceq $r.packages[0]})
  $base=$r.processName.Split(':')[0]
  if($base -cne $r.packages[0] -and $services.Count -ne 1){$d.reason='GLOBAL_PROCESS_PACKAGE_MAPPING_UNPROVEN';return $d}
  if($r.token -ceq $homeProcesses[0].token){continue}
  if($r.state -le 6){
   if($r.state -cin @(2,3)){$d.reason='ENV_WAIT_FOREIGN_FOREGROUND';$d.status='BLOCKED_OCCUPIED';return $d}
   if($services.Count -ne 1){$d.reason=if($r.appId -ge 10000){'ENV_WAIT_ACTIVE_SERVICE_UNQUALIFIED'}else{'GLOBAL_CORE_SERVICE_UNPROVEN'};$d.status=if($r.appId -ge 10000){'BLOCKED_OCCUPIED'}else{'BLOCKED_UNPROVEN'};return $d}
  }elseif($r.state -cin @(9,11,12)){$d.reason='ENV_WAIT_CONTENDING_OPERATION';$d.status='BLOCKED_OCCUPIED';return $d}
 }
 $d.firstRejectedRecord=$null;$d.qualified=$true;$d.status='PASS';$d.reason='GLOBAL_IDLE_QUALIFIED_INTERNAL_ONLY';$d.stage='qualified';$d.systemPackageFacts='BOUND_NARROW_POLICY';$d.defaultHomeFacts='BOUND_ROLE_COMPONENT_UID';$d.captureQualification='BODY_RETURNED_OUTER_CONTROLLER_RETURN_STILL_REQUIRED';return $d
 }catch{$d.qualified=$false;$d.reason='GLOBAL_PARSE_UNPROVEN';$d.stage='format';return $d}
}

# Same original context only. No IO in classification, no synthetic EOF/close.
function Get-CaptureStartDisposition($context){
 if($context.started -and $context.startEntered -and $context.startReturned){return 'STARTED_ORIGINAL_STREAM_PATH'}
 if($context.startEntered){return 'RETAIN_START_ENTERED_NOT_ESTABLISHED'}
 if($context.started -or $context.startUnknown){return 'RETAIN_START_STATE_CONFLICT'}
 if($context.processCreateEntered -and -not $context.processCreateReturned){return 'RETAIN_PROCESS_CREATE_UNKNOWN'}
 if($context.processDisposeEntered -and -not $context.processDisposed){return 'RETAIN_PROCESS_DISPOSE_UNKNOWN'}
 if($context.lockOpenUnknown){return 'RETAIN_LOCK_OPEN_UNKNOWN'}
 foreach($reader in $context.readers){
  if($reader.fileOpenUnknown -or ($reader.fileOpenEntered -and -not $reader.fileOpenReturned)){return 'RETAIN_RAW_OPEN_UNKNOWN'}
  if($reader.fileCloseEntered -and -not $reader.fileClosed){return 'RETAIN_RAW_CLOSE_UNKNOWN'}
  if($reader.pipeOpenEntered -or $reader.pipe -or $reader.read -or $reader.write -or $reader.readStartUnknown -or $reader.writeStartUnknown){return 'RETAIN_PRESTART_IO_CONFLICT'}
 }
 $i=$context.input
 if($i -and (($i.openEntered -and -not $i.openReturned) -or ($i.pinHashCreateEntered -and -not $i.pinHashCreateReturned) -or ($i.pinHashCreateReturned -and -not $i.pinHashDisposed))){return 'RETAIN_INPUT_CREATE_OR_HASH_UNKNOWN'}
 if($i -and ($i.write -or $i.sourceRead -or $i.writeStartUnknown -or $i.readStartUnknown -or ($i.sourceCloseEntered -and -not $i.sourceClosed))){return 'RETAIN_INPUT_IO_UNKNOWN'}
 return 'KNOWN_START_NEVER_ENTERED'
}
function Close-KnownPrestartResources($context){
 $state=Get-CaptureStartDisposition $context;$context.prestartDisposition=$state
 if($state -cne 'KNOWN_START_NEVER_ENTERED'){return $false}
 # No Process.Start, pipe getter, reader or waiter has been entered. Absence is
 # explicit in separate never-created fields, never misreported as EOF/close.
 foreach($r in $context.readers){
  $r.pipeNeverCreated=$true
  if($r.fileOpenReturned -and -not $r.fileCloseEntered){
   $r.fileCloseEntered=$true;$r.fileCloseCalls++
   try{$r.file.Close();$r.fileClosed=$true}catch{$context.prestartDisposition='RETAIN_RAW_CLOSE_UNKNOWN';return $false}
  }
 }
 $i=$context.input
 if($i -and $i.openReturned -and -not $i.sourceCloseEntered){$i.sourceCloseEntered=$true;try{$i.source.Close();$i.sourceClosed=$true}catch{$context.prestartDisposition='RETAIN_INPUT_CLOSE_UNKNOWN';return $false}}
 if($context.processCreateReturned -and -not $context.processDisposeEntered){
  $context.processDisposeEntered=$true;$context.processDisposeCalls++
  try{$context.process.Dispose();$context.processDisposed=$true}catch{$context.prestartDisposition='RETAIN_PROCESS_DISPOSE_UNKNOWN';return $false}
 }
 $context.processNeverCreated=-not $context.processCreateEntered
 $context.stdinNeverCreated=$true
 $context.noStartResourcesReturned=($context.processDisposed -or $context.processNeverCreated) -and @($context.readers|Where-Object {$_.fileOpenUnknown -or ($_.fileOpenReturned -and -not $_.fileClosed)}).Count -eq 0 -and (-not $i -or $i.sourceClosed)
 return [bool]$context.noStartResourcesReturned
}
