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
 $manifestPath='D:\CodexProjects\VideoKit\docs\coder\d1android02-facts-v2-qualification07\rev2\reference\gate-sources.json'
 if((Digest $manifestPath) -cne $policy.gateSourcesSha256 -or $policy.gateSourcesSha256 -cne $script:expectedGateSourcesSha256){throw 'INITIAL_GATE_SOURCE_MANIFEST'}
 $gm=ReadJsonExact $manifestPath @('schema','files') 8192
 foreach($row in $gm.files){$f=Join-Path 'D:\CodexProjects\VideoKit\docs\coder\d1android02-facts-v2-qualification07/rev2' $row.path;NoLinks $f;if((Digest $f) -cne $row.sha256){throw 'INITIAL_GATE_SOURCE_CHANGED'}}
 $rp=Join-Path $root 'gate-original-return.json';NoLinks $rp
 $r=ReadJsonExact $rp @('schema','scope','planId','kind','generation','ownerPid','ownerThread','proofStartTick','checkerPid','temporaryResourcesReturned','scopeClaimIntentionallyRetained','claimFileId','claimPath','scopeStartTick','checkerSourceSha256','gateSourcesSha256','entrySha256','ownerSha256','routeSha256','events','controlBeforeReceipt','receiptWriteBytes','physicalIO','sourceHashBytes','sourceHashReads') 16384
 $script:initialGateReceipt=$r
 $receiptHash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($script:lastJsonBytes)).ToLowerInvariant();$receiptLength=$script:lastJsonBytes.Length
 if($r.schema -cne 'ENTRY_GATE_RETURN_V2' -or $r.scope -cne $policy.scope -or $r.planId -cne $policy.planId -or $r.kind -cne $expectedKind -or $r.generation -cne $h.generation -or $r.ownerPid -ne $ad.ownerPid -or $r.checkerPid -ne $proof.controllerPid -or $r.claimFileId -ne $h.claimFileId -or $r.scopeStartTick -ne $h.scopeStartTick -or $r.gateSourcesSha256 -cne $policy.gateSourcesSha256 -or $r.entrySha256 -cne $policy.entrySha256 -or $r.ownerSha256 -cne $policy.outerOwnerSha256 -or $receiptHash -cne $proof.outerReturnSha256 -or $receiptHash -cne $proof.captureReceiptSha256){throw 'INITIAL_GATE_ORIGINAL_RECEIPT'}
 if(-not (BoolField $r 'temporaryResourcesReturned' $true) -or -not (BoolField $r 'scopeClaimIntentionallyRetained' $true) -or -not (BoolField $proof 'candidateOnlyWriterCloseNotProven' $true)){throw 'INITIAL_GATE_RESOURCE_SETS'}
 foreach($k in @('ownerPid','ownerThread','proofStartTick','checkerPid','scopeStartTick','claimFileId')){if(-not (IntField $r $k ([long]::MaxValue) 1)){throw 'INITIAL_RECEIPT_INTEGER'}}
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
 if($h.schema -cne 'RUNNER_HANDOFF_V1' -or $h.kind -cne $kind -or $h.ownerPid -ne $ad.ownerPid -or $h.scopeStartTick -ne $proof.scopeStartTick -or $h.generation -cne $ad.gateHandoff.generation -or $h.initialProofSha256 -cne $PredecessorProofSha -or $h.runnerSourceSha256 -cne '09dca271fc141ffe632d1f19af2c6cc2085de47b762c179a5254de8e8929af4a' -or $policy.runnerSourceSha256 -cne $h.runnerSourceSha256 -or $policy.runnerPermit.sha256 -cne $h.permitSha256 -or $policy.runnerApproval.sha256 -cne $h.approvalSha256){throw 'RUNNER_ORIGINAL_HANDOFF_BINDING'}
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
 $srcKeys=@('tools/production_runner.py','tools/entry_gates.py','tools/outer_owner.py','tools/capture_android02.ps1','tools/win32_route.py','tools/runtime_binding.py','reference/current-runtime-identity.json','reference/exact-seven-role-plan.json','reference/gate-sources.json','selfchecks/route_fixture.py','selfchecks/capture_fixture.py','reference/route-backend-contract.json','selfchecks/route_model.py','tools/admission_checks.ps1','tools/fact_collector.py','reference/fact-plan.json','selfchecks/fact_fixture.py','tools/fact_preauth.py','tools/facts_entry.py','tools/facts_qualification.py','tools/outer_capture.py','tools/capture_policy.py','tools/native_identity.py','tools/evidence_io.py','reference/qualification-v2-schema.json','tools/facts_contract.py','tools/immutable_evidence.py','tools/capture_origin.py','tools/qualification_reference.ps1','tools/source_budget.py')
 foreach($obj in @($permit.sources,$seal.sources)){if(@(Compare-Object -CaseSensitive @($obj.PSObject.Properties.Name|Sort-Object) @($srcKeys|Sort-Object)).Count){throw 'RUNNER_EXACT_SOURCE_SET'}}
 foreach($key in $srcKeys){$sourcePath=Join-Path 'D:\CodexProjects\VideoKit\docs\coder\d1android02-facts-v2-qualification07/rev2' $key;NoLinks $sourcePath;if((Digest $sourcePath) -cne $seal.sources.$key -or $seal.sources.$key -cne $permit.sources.$key){throw 'RUNNER_SOURCE_CHANGED'}}
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
 if($h.schema -cne 'RUNNER_HANDOFF_V1' -or $h.ownerPid -ne $ad.ownerPid -or $h.scopeStartTick -ne $scopeTick -or $h.runnerSourceSha256 -cne '09dca271fc141ffe632d1f19af2c6cc2085de47b762c179a5254de8e8929af4a' -or $policy.runnerSourceSha256 -cne $h.runnerSourceSha256 -or $h.permitSha256 -cne $policy.runnerPermit.sha256 -or $h.approvalSha256 -cne $policy.runnerApproval.sha256 -or $h.kind -cne $kind){throw 'RUNNER_FINAL_START_SOURCE'}
 if($h.permitExpiresUtc -isnot [string] -or [DateTimeOffset]::UtcNow -ge [DateTimeOffset]::Parse($h.permitExpiresUtc)){throw 'RUNNER_FINAL_START_EXPIRED'}
 $now=[Environment]::TickCount64
 if($now -lt $scopeTick -or $now-$scopeTick -ge 600000 -or $h.initialProofStartTick -lt $scopeTick -or $h.initialProofStartTick -gt $now){throw 'RUNNER_FINAL_START_WHOLE_OR_CLOCK'}
 if($roleIndex -eq 0 -and ($now-$scopeTick -ge 30000 -or $now-$h.initialProofStartTick -ge 10000)){throw 'RUNNER_FINAL_START_ORIGINAL_MINIMUM_WINDOW'}
}


$script:GICollectorSha256='551f32bd298ea7997c98cdb6d12a7d8d847b1941f57109fabd18e700d8cd1254'
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
 $v2=$q.schema -ceq 'GLOBAL_IDLE_QUALIFICATION_V2'
 $ctxKeys=@('scope','runId','mode','rawSha256','rawBytes','captureBodyReturned','sourceSealSha256','planSha256','reviewEvidenceSha256','nowUtc');if($v2){$ctxKeys+=@('targetPlanId','evidenceRoot')};GIExact $ctx $ctxKeys
 if($ctx.captureBodyReturned -isnot [bool] -or -not $ctx.captureBodyReturned){throw 'GLOBAL_CAPTURE_RETURN_UNPROVEN'}
 if($v2){$q=GIV2LoadReference $q $ctx}
 return GIQualificationExpanded02 $q $ctx $v2
}
function GIQualificationExpanded02($q,$ctx,[bool]$v2){
 if($v2){GIExact $q @('schema','mode','fixtureOnly','targetScope','targetRunId','targetSourceSealSha256','targetPlanSha256','factScope','factCaptureReceiptSha256','factOuterReturnSha256','collectorSourceSha256','factPlanSha256','rawSha256','rawBytes','routeProofSha256','sdkSha256','collectedAtUtc','expiresAtUtc','originalReturn','grammar','serial','model','api','fingerprint','user','home','services','systemPackages','reviewEvidenceSha256','authorizationKind','externalPreauthSha256','runtimeBindingSha256','bundleSha256','adapterSourceSha256','reviewSha256','reviewSourceThreadId','reviewSourceTurnId','approved','targetPlanId','reviewUtf8','candidateUtf8','bundleUtf8','outerReturnUtf8');GIV2Reviewed $q $ctx}else{GIExact $q @('schema','mode','fixtureOnly','targetScope','targetRunId','targetSourceSealSha256','targetPlanSha256','factScope','factAuthoritySha256','factApprovalSha256','factCaptureReceiptSha256','factOuterReturnSha256','collectorSourceSha256','factPlanSha256','rawSha256','rawBytes','routeProofSha256','sdkSha256','collectedAtUtc','expiresAtUtc','originalReturn','grammar','serial','model','api','fingerprint','user','home','services','systemPackages','reviewEvidenceSha256')}
 if(-not $v2 -and (-not(GISha $q.factAuthoritySha256) -or -not(GISha $q.factApprovalSha256))){throw 'GLOBAL_QUAL_HASH'}
 if(-not $v2 -and [Text.Encoding]::UTF8.GetByteCount(($q|ConvertTo-Json -Depth 16 -Compress)) -gt 16384){throw 'GLOBAL_QUAL_BYTE_BOUND'}
 foreach($k in @('targetScope','targetSourceSealSha256','targetPlanSha256','factScope','factCaptureReceiptSha256','factOuterReturnSha256','collectorSourceSha256','factPlanSha256','rawSha256','routeProofSha256','sdkSha256','reviewEvidenceSha256')){if(-not (GISha $q.$k)){throw 'GLOBAL_QUAL_HASH'}}
 if((-not $v2 -and $q.schema -cne 'GLOBAL_IDLE_QUALIFICATION_V1') -or $q.targetScope -cne $ctx.scope -or $q.targetRunId -cne $ctx.runId -or $q.targetSourceSealSha256 -cne $ctx.sourceSealSha256 -or $q.targetPlanSha256 -cne $ctx.planSha256 -or $q.factScope -ceq $q.targetScope -or $q.reviewEvidenceSha256 -cne $ctx.reviewEvidenceSha256){throw 'GLOBAL_QUAL_SCOPE_OR_SOURCE'}
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

$script:GIV2AdapterSha256='b9fed4c80258dfcb7326b1b4e81d568b5068c5cbaf9c7a2332f16cacf7575e55'
# Qualification V2 adds exact reviewed-byte provenance, then shares the original
# HOME/service/process policy body. No legacy authority/approval is synthesized.
function GIV2Json([string]$s,[int]$Max=16384){
 if($s -isnot [string] -or [Text.Encoding]::UTF8.GetByteCount($s) -gt $Max){throw 'GLOBAL_V2_JSON_BOUND'}
 try{$doc=[Text.Json.JsonDocument]::Parse($s)}catch{throw 'GLOBAL_V2_JSON_FORMAT'}
 function Walk($e,[int]$d){
  if($d -gt 16){throw 'GLOBAL_V2_JSON_DEPTH'}
  if($e.ValueKind -eq [Text.Json.JsonValueKind]::Object){$seen=[Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase);foreach($p in $e.EnumerateObject()){if(-not $seen.Add($p.Name)){throw 'GLOBAL_V2_DUPLICATE_JSON'};Walk $p.Value ($d+1)}}
  elseif($e.ValueKind -eq [Text.Json.JsonValueKind]::Array){foreach($a in $e.EnumerateArray()){Walk $a ($d+1)}}
 }
 try{Walk $doc.RootElement 0}finally{$doc.Dispose()}
 return $s|ConvertFrom-Json -Depth 20 -DateKind String
}
function GIV2Sha([string]$s){return [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.UTF8Encoding]::new($false,$true).GetBytes($s))).ToLowerInvariant()}
function GIV2Same($a,$b){return ($a|ConvertTo-Json -Depth 20 -Compress) -ceq ($b|ConvertTo-Json -Depth 20 -Compress)}
function GIV2Reviewed($q,$ctx){
 if($q.schema -cne 'GLOBAL_IDLE_QUALIFICATION_V2' -or $q.authorizationKind -cne 'GLOBAL_IDLE_FACT_PREAUTH_V1' -or $q.approved -isnot [bool] -or -not $q.approved -or $q.reviewSourceThreadId -cne '01a107c3-2bf9-7fa0-94a0-234258ca6774' -or $q.adapterSourceSha256 -cne $script:GIV2AdapterSha256 -or $q.targetPlanId -cne $ctx.targetPlanId){throw 'GLOBAL_V2_APPROVAL_SOURCE_TARGET'}
 foreach($k in @('externalPreauthSha256','runtimeBindingSha256','bundleSha256','reviewSha256','adapterSourceSha256')){if(-not(GISha $q.$k) -or $q.$k -ceq ('0'*64)){throw 'GLOBAL_V2_HASH'}}
 if((GIV2Sha $q.reviewUtf8) -cne $ctx.reviewEvidenceSha256 -or $q.reviewSha256 -cne $ctx.reviewEvidenceSha256){throw 'GLOBAL_V2_EXTERNAL_REVIEW_HASH'}
 $r=GIV2Json $q.reviewUtf8 2097152;$c=GIV2Json $q.candidateUtf8 8388608;$b=GIV2Json $q.bundleUtf8 8388608;$o=GIV2Json $q.outerReturnUtf8 8388608
 GIExact $r @('schema','sourceThreadId','sourceTurnId','mode','approvedForQualification','candidateSha256','bundleSha256','target','notBeforeUtc','expiresUtc','home','homeEvidenceSha256','services')
 GIExact $c @('schema','status','approved','bundleSha256','target','mode','collectedAtUtc','maximumExpiresUtc','home','services','servicePolicy')
 GIExact $b @('schema','factScope','factPlanId','factRunId','nonce','rawSha256','rawBytes','receiptSha256','externalPreauthSha256','runtimeBindingSha256','outerReturnSha256','collectorSha256','factPlanSha256','sourceSealSha256','mode','factEvidenceRoot','gateReceiptSha256','initialProofSha256')
 GIExact $o @('schema','ownerPid','creationFileTime','creatorArgv','stdoutSha256','waitReturned','stdoutEOF','stderrEOF','originalPipesClosed','originalHandleClosed','controllerReturned','unknown','exitCode','image','hostPid','hostThread','captureSourceSha256','originSourceSha256','lifecycle')
 if(-not(GIInt $o.hostPid 1 2147483647) -or -not(GIInt $o.hostThread 1 ([long]::MaxValue)) -or $o.captureSourceSha256 -cne $script:GIV2CaptureSha256 -or $o.originSourceSha256 -cne $script:GIV2OriginSha256 -or $o.lifecycle -cne 'ORIGINAL_CONSTRUCTOR_START_READ_WAIT_CLOSE_JOURNAL_RETURN' -or $o.image -isnot [string] -or $o.image.Replace('\','/').ToLowerInvariant() -cne 'c:/users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'){throw 'GLOBAL_V2_OUTER_ORIGIN'}
 if($q.reviewSourceTurnId -isnot [string] -or $q.reviewSourceTurnId -cnotmatch '^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$'){throw 'GLOBAL_V2_REVIEW_SOURCE'}
 GIExact $r.target @('scope','planId','runId','sourceSealSha256','planSha256','mode','evidenceRoot')
 if($r.schema -cne 'GLOBAL_IDLE_FACT_REVIEW_V2' -or $r.approvedForQualification -isnot [bool] -or -not $r.approvedForQualification -or $r.sourceThreadId -cne $q.reviewSourceThreadId -or $r.sourceTurnId -cne $q.reviewSourceTurnId -or $r.mode -cne $q.mode -or $r.candidateSha256 -cne (GIV2Sha $q.candidateUtf8) -or $r.bundleSha256 -cne (GIV2Sha $q.bundleUtf8) -or $q.bundleSha256 -cne $r.bundleSha256){throw 'GLOBAL_V2_REVIEW_PROVENANCE'}
 if($c.schema -cne 'GLOBAL_IDLE_QUALIFICATION_CANDIDATE_V2' -or $c.status -cne 'REQUIRES_REVIEW' -or $c.approved -isnot [bool] -or $c.approved -or $c.bundleSha256 -cne $q.bundleSha256 -or $c.mode -cne $q.mode -or $c.collectedAtUtc -cne $q.collectedAtUtc -or -not (GIV2Same $c.target $r.target) -or -not (GIV2Same $c.home $q.home) -or @($c.services).Count -ne 0 -or $c.servicePolicy -cne 'NO_AUTOMATIC_EXEMPTIONS'){throw 'GLOBAL_V2_CANDIDATE_BINDING'}
 if($r.target.scope -cne $q.targetScope -or $r.target.planId -cne $q.targetPlanId -or $r.target.runId -cne $q.targetRunId -or $r.target.sourceSealSha256 -cne $q.targetSourceSealSha256 -or $r.target.planSha256 -cne $q.targetPlanSha256 -or $r.target.mode -cne $q.mode -or -not(GIV2Same $r.home $q.home) -or -not(GIV2Same $r.services $q.services) -or $r.expiresUtc -cne $q.expiresAtUtc){throw 'GLOBAL_V2_REVIEW_POLICY_TARGET'}
 if($b.schema -cne 'GLOBAL_IDLE_FACT_EVIDENCE_BUNDLE_V2' -or $b.mode -cne $q.mode -or $b.factScope -cne $q.factScope -or $b.rawSha256 -cne $q.rawSha256 -or $b.rawBytes -ne $q.rawBytes -or $b.receiptSha256 -cne $q.factCaptureReceiptSha256 -or $b.externalPreauthSha256 -cne $q.externalPreauthSha256 -or $b.runtimeBindingSha256 -cne $q.runtimeBindingSha256 -or $b.outerReturnSha256 -cne $q.factOuterReturnSha256 -or $b.collectorSha256 -cne $q.collectorSourceSha256 -or $b.factPlanSha256 -cne $q.factPlanSha256 -or $b.sourceSealSha256 -cne $q.targetSourceSealSha256 -or $q.factOuterReturnSha256 -cne (GIV2Sha $q.outerReturnUtf8)){throw 'GLOBAL_V2_BUNDLE_BINDING'}
 if($o.schema -cne 'GLOBAL_IDLE_FACT_OBSERVED_OUTER_RETURN_V2' -or -not(GIInt $o.ownerPid 1 2147483647) -or -not(GIInt $o.creationFileTime 1 ([long]::MaxValue))){throw 'GLOBAL_V2_OUTER_IDENTITY'}
 foreach($k in @('waitReturned','stdoutEOF','stderrEOF','originalPipesClosed','originalHandleClosed','controllerReturned','unknown','exitCode')){if($o.$k -cne $q.originalReturn.$k){throw 'GLOBAL_V2_OUTER_RETURN_BINDING'}}
 foreach($stamp in @($r.notBeforeUtc,$r.expiresUtc,$ctx.nowUtc)){if($stamp -isnot [string] -or $stamp -cnotmatch '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,7})?(?:Z|\+00:00)$'){throw 'GLOBAL_V2_REVIEW_CLOCK'}}
 if([DateTimeOffset]::Parse($r.notBeforeUtc) -gt [DateTimeOffset]::Parse($ctx.nowUtc) -or [DateTimeOffset]::Parse($r.notBeforeUtc) -lt [DateTimeOffset]::Parse($q.collectedAtUtc)){throw 'GLOBAL_V2_REVIEW_WINDOW'}
}

$script:GIV2CaptureSha256='d26a0a20b6607a8d07eec8a09a63184966c40cb5092db5fcf5118567a881b589'
$script:GIV2OriginSha256='40e4418919ed0050220ba35a8fce5c42c5149ab36ac54c0279b0cdcea27df132'
$script:GIV2CandidateRoot='D:/CodexProjects/VideoKit/docs/coder/d1android02-facts-v2-qualification07/rev2'
# Fixed immutable evidence references for qualification V2 only. All file reads
# are source/evidence reads with the original 256 MiB / 64-read ceiling, recorded
# independently from the <=16 KiB transferred qualification and control ledger.
if($null -eq $script:qualificationEvidenceSourceBytes){$script:qualificationEvidenceSourceBytes=[long]0}
if($null -eq $script:qualificationEvidenceSourceReads){$script:qualificationEvidenceSourceReads=[long]0}
if($null -eq $script:qualificationEvidenceReadEvents){$script:qualificationEvidenceReadEvents=[Collections.Generic.List[object]]::new()}
if(-not ('VideoKitQ02File' -as [type])){
 Add-Type -TypeDefinition @'
using System;using System.Text;using System.Runtime.InteropServices;using Microsoft.Win32.SafeHandles;
public static class VideoKitQ02File{
 [StructLayout(LayoutKind.Sequential)] public struct Info{public uint Attributes;public System.Runtime.InteropServices.ComTypes.FILETIME C,A,W;public uint Volume,SizeHigh,SizeLow,Links,IndexHigh,IndexLow;}
 [DllImport("kernel32.dll",SetLastError=true)] static extern bool GetFileInformationByHandle(SafeFileHandle h,out Info i);
 [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)] static extern uint GetFinalPathNameByHandle(SafeFileHandle h,StringBuilder b,uint n,uint f);
 public static string[] Identity(SafeFileHandle h){Info i;if(!GetFileInformationByHandle(h,out i))throw new System.ComponentModel.Win32Exception();var b=new StringBuilder(32768);var n=GetFinalPathNameByHandle(h,b,32768,0);if(n==0||n>=32768)throw new System.ComponentModel.Win32Exception();return new[]{i.Volume.ToString(System.Globalization.CultureInfo.InvariantCulture),(((ulong)i.IndexHigh<<32)|i.IndexLow).ToString(System.Globalization.CultureInfo.InvariantCulture),(((ulong)i.SizeHigh<<32)|i.SizeLow).ToString(System.Globalization.CultureInfo.InvariantCulture),i.Links.ToString(),i.Attributes.ToString(),b.ToString()};}
}
'@
}
function GIV2NoLinks([string]$Path){
 $p=[IO.FileInfo]::new($Path)
 while($null -ne $p){if($p.Exists -and ($p.Attributes -band [IO.FileAttributes]::ReparsePoint)){throw 'GLOBAL_V2_EVIDENCE_REPARSE'};$p=if($p -is [IO.FileInfo]){$p.Directory}else{$p.Parent}}
}
function GIV2FixedPath([string]$Path,[string]$Root,[string]$Name){
 $expected=[IO.Path]::Combine($Root,$Name)
 if($Path -cne $expected -or [IO.Path]::GetFullPath($Path) -cne $Path -or $Path.Replace('\','/').Split('/') -ccontains '..' -or $Path.Replace('\','/').Split('/') -ccontains '.'){throw 'GLOBAL_V2_EVIDENCE_FIXED_PATH'}
 $p=$Path.Replace('\','/');$dev=($script:GIV2CandidateRoot+'/selfchecks/work/');$test='D:/CodexProjects/VideoKit/docs/tester/D1_FACTS_V2_QUALIFICATION07_INDEPENDENT_B_EVIDENCE/fixtures/';$live='D:/CodexProjects/VideoKit/docs/tester/D1_ANDROID02_CAPTURE_EXECUTION/'
 if(-not ($p.StartsWith($dev,[StringComparison]::Ordinal) -or $p.StartsWith($test,[StringComparison]::Ordinal) -or $p.StartsWith($live,[StringComparison]::Ordinal))){throw 'GLOBAL_V2_EVIDENCE_ROOT'}
 GIV2NoLinks $Path
}
function GIV2ReadReference($r,[string]$Root,[string]$Name,[long]$Cap=8388608){
 GIExact $r @('path','bytes','sha256','volumeId','fileId')
 if(-not(GIInt $r.bytes 1 $Cap) -or -not(GISha $r.sha256) -or $r.path -isnot [string] -or $r.volumeId -isnot [string] -or $r.fileId -isnot [string] -or $r.volumeId -cnotmatch '^(0|[1-9][0-9]*)$' -or $r.fileId -cnotmatch '^[1-9][0-9]*$'){throw 'GLOBAL_V2_EVIDENCE_REFERENCE_TYPE'}
 GIV2FixedPath $r.path $Root $Name
 $event=ReserveGIV2Reference $r.bytes $r.path
 $script:qualificationEvidenceSourceReads++;$f=$null;$closeEntered=$false;$bytes=[byte[]]::new([int]$r.bytes);$offset=0
 try{
  $f=[IO.FileStream]::new($r.path,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read)
  $id=[VideoKitQ02File]::Identity($f.SafeFileHandle);$final=$id[5];if($final.StartsWith('\\?\')){$final=$final.Substring(4)}
  if($id[0] -cne $r.volumeId -or $id[1] -cne $r.fileId -or $id[2] -cne $r.bytes.ToString() -or $id[3] -cne '1' -or ([long]$id[4] -band 1024) -or $final -cne $r.path){throw 'GLOBAL_V2_EVIDENCE_FILE_IDENTITY'}
  while($offset -lt $bytes.Length){
   try{$n=$f.Read($bytes,$offset,$bytes.Length-$offset)}catch{$event.unknown=$true;$script:qualificationEvidenceReadUnknown=$true;while($true){Start-Sleep -Milliseconds 1000}}
   if($n -eq 0){throw 'GLOBAL_V2_EVIDENCE_SHORT_READ'};$offset+=$n;$event.actualBytes+=$n;$script:qualificationEvidenceSourceBytes+=$n
  }
  $after=[VideoKitQ02File]::Identity($f.SafeFileHandle)
  if(($id -join '|') -cne ($after -join '|')){throw 'GLOBAL_V2_EVIDENCE_ID_CHANGED'}
 }finally{
  if($null -ne $f){$closeEntered=$true;try{$f.Dispose()}catch{$event.unknown=$true;$script:qualificationEvidenceCloseUnknown=$true;while($true){Start-Sleep -Milliseconds 1000}}}
  $event.closeReturned=($null -ne $f -and $closeEntered);$event.opened=($null -ne $f)
  $script:qualificationEvidenceReadEvents.Add(@{path=$r.path;bytesRead=$offset;sourceReservation=$r.bytes;closeEntered=$closeEntered;originalCloseReturned=($null -ne $f -and $closeEntered)})
 }
 $h=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($bytes)).ToLowerInvariant()
 if($offset -ne $r.bytes -or $h -cne $r.sha256){throw 'GLOBAL_V2_EVIDENCE_ORIGINAL_BYTES'}
 return ,$bytes
}
function GIV2BytesSha([byte[]]$b){return [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($b)).ToLowerInvariant()}
function GIV2Utf8([byte[]]$b){try{return [Text.UTF8Encoding]::new($false,$true).GetString($b)}catch{throw 'GLOBAL_V2_UTF8'}}
function GIV2Decode64([string]$s,[int]$cap){
 if($s -isnot [string] -or $s.Length -gt 4*[Math]::Ceiling($cap/3.0)){throw 'GLOBAL_V2_BASE64_BOUND'}
 try{$b=[Convert]::FromBase64String($s)}catch{throw 'GLOBAL_V2_BASE64'}
 if($b.Length -gt $cap -or [Convert]::ToBase64String($b) -cne $s){throw 'GLOBAL_V2_BASE64'};return ,$b
}
function GIV2RawFacts([byte[]]$raw){
 if($raw.Length -lt 1 -or $raw.Length -gt 139264){throw 'GLOBAL_V2_RAW_BOUND'}
 $prefix=[Text.Encoding]::ASCII.GetBytes("GI_FACTS_V1`n");if($raw.Length -lt $prefix.Length -or [Text.Encoding]::ASCII.GetString($raw,0,$prefix.Length) -cne "GI_FACTS_V1`n"){throw 'GLOBAL_V2_RAW_BEGIN'}
 $offset=$prefix.Length;$values=@{};$previous=[long]-1;$first=[long]-1;$last=[long]-1
 foreach($name in @('model','api','firmware','user','system','role','home')){
  $end=$offset;while($end -lt $raw.Length -and $end-$offset -lt 130 -and $raw[$end] -ne 10){$end++}
  if($end -ge $raw.Length -or $end-$offset -ge 130){throw 'GLOBAL_V2_RAW_HEADER'}
  $header=[Text.Encoding]::ASCII.GetString($raw,$offset,$end-$offset);$m=[regex]::Match($header,'^GI_ITEM\|([a-z]+)\|([0-9]{1,3})\|([0-9]{1,12})\|([0-9]{1,12})\|([0-9]{1,6})$')
  if(-not $m.Success -or $m.Groups[1].Value -cne $name){throw 'GLOBAL_V2_RAW_ORDER'}
  $status=[long]$m.Groups[2].Value;$a=[long]$m.Groups[3].Value;$z=[long]$m.Groups[4].Value;$n=[long]$m.Groups[5].Value;$offset=$end+1
  if($status -ne 0 -or $z -lt $a -or $z-$a -gt 15 -or $a -lt $previous -or $n -gt 131072 -or $offset+$n -ge $raw.Length -or $raw[$offset+$n] -ne 10){throw 'GLOBAL_V2_RAW_ITEM_VALUES'}
  if($first -lt 0){$first=$a};$last=$z;$previous=$z
  $text=GIV2Utf8 ([byte[]]$raw[$offset..($offset+$n-1)])
  if($text -cmatch '[\x00-\x08\x0b-\x1f]'){throw 'GLOBAL_V2_RAW_CONTROL'};$values[$name]=$text.Trim();$offset+=$n+1
 }
 if([Text.Encoding]::ASCII.GetString($raw,$offset,$raw.Length-$offset) -cne "GI_FACTS_END`n" -or $last-$first -gt 15){throw 'GLOBAL_V2_RAW_END'}
 if($values.model -cne 'TB138FC' -or $values.api -cne '31' -or $values.user -cne '0' -or $values.firmware.Length -lt 8 -or $values.firmware.Length -gt 256){throw 'GLOBAL_V2_RAW_DEVICE'}
 $packages=@();$seen=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
 foreach($line in $values.system.Split("`n")){
  $m=[regex]::Match($line.TrimEnd("`r"),'^package:([A-Za-z_][A-Za-z0-9_.]*) uid:([0-9]+)$')
  if(-not $m.Success -or -not $seen.Add($m.Groups[1].Value) -or [long]$m.Groups[2].Value -gt 2147483647){throw 'GLOBAL_V2_RAW_SYSTEM'}
  $packages+=@([pscustomobject][ordered]@{package=$m.Groups[1].Value;uid=[long]$m.Groups[2].Value;systemFlag=$true})
 }
 if($packages.Count -gt 128){throw 'GLOBAL_POLICY_BOUND'}
 return @{values=$values;systemPackages=$packages}
}
function GIV2LoadReference($wire,$ctx){
 if($null -eq $global:VideoKitQ03SourceBudget){throw 'GLOBAL_V2_SOURCE_AUTHORITY_REQUIRED'}
 if($global:VideoKitQ03SourceBudget.ticket.scope -cne $ctx.scope){throw 'GLOBAL_V2_SOURCE_AUTHORITY_SCOPE'}
 GIExact $wire @('schema','representation','mode','fixtureOnly','targetScope','targetRunId','targetPlanId','targetSourceSealSha256','targetPlanSha256','reviewEvidenceSha256','authorizationKind','adapterSourceSha256','bundleSha256','evidenceRoot','evidenceRef')
 if([Text.Encoding]::UTF8.GetByteCount(($wire|ConvertTo-Json -Depth 16 -Compress)) -gt 16384){throw 'GLOBAL_QUAL_BYTE_BOUND'}
 if($wire.schema -cne 'GLOBAL_IDLE_QUALIFICATION_V2' -or $wire.representation -cne 'PINNED_EVIDENCE_REFERENCE_V1' -or $wire.targetScope -cne $ctx.scope -or $wire.targetRunId -cne $ctx.runId -or $wire.targetPlanId -cne $ctx.targetPlanId -or $wire.targetSourceSealSha256 -cne $ctx.sourceSealSha256 -or $wire.targetPlanSha256 -cne $ctx.planSha256 -or $wire.mode -cne $ctx.mode -or $wire.reviewEvidenceSha256 -cne $ctx.reviewEvidenceSha256 -or $wire.adapterSourceSha256 -cne $script:GIV2AdapterSha256 -or $wire.evidenceRoot -cne $ctx.evidenceRoot){throw 'GLOBAL_V2_WIRE_TARGET_OR_SOURCE'}
 $root=[IO.Path]::Combine($ctx.evidenceRoot,'v2-authority');$bytes=GIV2ReadReference $wire.evidenceRef $root ('qualification-evidence-'+$ctx.scope+'.json')
 $body=GIV2Json (GIV2Utf8 $bytes) 8388608
 GIExact $body @('schema','reviewUtf8','candidateUtf8','bundleUtf8','outerReturnUtf8','preauthUtf8','policyUtf8','factsPacketRef','policyEvidence')
 if($body.schema -cne 'GLOBAL_IDLE_QUALIFICATION_EVIDENCE_V2' -or (GIV2Sha $body.reviewUtf8) -cne $ctx.reviewEvidenceSha256){throw 'GLOBAL_V2_EXTERNAL_REVIEW_HASH'}
 $r=GIV2Json $body.reviewUtf8 2097152;$c=GIV2Json $body.candidateUtf8 8388608;$b=GIV2Json $body.bundleUtf8 8388608;$o=GIV2Json $body.outerReturnUtf8 8388608;$a=GIV2Json $body.preauthUtf8 16384;$p=GIV2Json $body.policyUtf8 16384
 GIExact $r @('schema','sourceThreadId','sourceTurnId','mode','approvedForQualification','candidateSha256','bundleSha256','target','notBeforeUtc','expiresUtc','home','homeEvidenceSha256','services')
 GIExact $r.target @('scope','planId','runId','sourceSealSha256','planSha256','mode','evidenceRoot')
 foreach($key in @('factPlanId','nonce')){if($b.$key -isnot [string] -or $b.$key -cnotmatch '^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$'){throw 'GLOBAL_V2_FACT_PLAN_NONCE_TYPE'}}
 if($b.factRunId -isnot [string] -or $b.factRunId -cnotmatch '^D1MA02-[A-Z0-9_-]{1,32}$'){throw 'GLOBAL_V2_FACT_RUN_TYPE'}
 if($r.target.evidenceRoot -cne $ctx.evidenceRoot -or $b.factEvidenceRoot -cne $a.evidenceRoot -or $p.evidenceRoot -cne $a.evidenceRoot -or $b.factScope -cne $a.scope -or $b.factPlanId -cne $a.planId -or $b.factRunId -cne $a.runId -or $b.nonce -cne $a.nonce){throw 'GLOBAL_V2_EVIDENCE_SCOPE_SOURCE'}
 $packet=GIV2ReadReference $body.factsPacketRef ([IO.Path]::Combine($a.evidenceRoot,'v2-original-return')) ('facts-entry-'+$a.scope+'.json') 262144
 if((GIV2BytesSha $packet) -cne $o.stdoutSha256){throw 'GLOBAL_V2_PACKET_ORIGINAL_RETURN_HASH'}
 $entry=GIV2Json (GIV2Utf8 $packet) 262144
 $entryKeys=@('schema','representation','receipt','receiptSha256','parsedFactsSha256','rawBase64','release','binding','gateReceiptBase64','initialProofBase64','outerProcessReturnStillRequired','qualificationIssued','sourceBytes','sourceReads','controlBytes');if($wire.mode -ceq 'OFFLINE_FIXTURE'){$entryKeys+=@('fixtureConstructorCalls','fixtureAudit')};GIExact $entry $entryKeys
 if($entry.schema -cne 'GLOBAL_IDLE_FACT_ENTRY_RETURN_V2' -or $entry.representation -cne 'FACTS_BASE64_SINGLE_COPY_V1'){throw 'GLOBAL_V2_PACKET_REPRESENTATION'}
 $raw=GIV2Decode64 $entry.rawBase64 139264;$f=GIV2RawFacts $raw;$fr=$entry.receipt;$binding=$entry.binding
 GIExact $fr @('schema','scope','mode','sourceSha256','planSha256','routeProofSha256','initialProofSha256','hostEnvironment','rawSha256','rawBytes','stdoutBytes','stderrBytes','hostElapsedSeconds','collectedAtUtc','originalBodyReturned','outerControllerReturnStillRequired','authorizationKind','externalPreauthSha256','runtimeBindingSha256','captureStartTick')
 GIExact $binding @('schema','mode','preauthSha256','scope','planId','runId','nonce','generation','ownerPid','ownerThread','claimFileId','scopeStartTick','proofStartTick','routeProofSha256','initialProofSha256','gateReceiptSha256','sourceSealSha256','gateSourcesSha256','binderSha256','boundAtUtc')
 GIExact $entry.release @('originalUnlockCloseReturned','generation','failure','sdkChildrenEntered','endTick','allTemporaryThreadsJoined','factProofTimely','factCaptureQualified','outerControllerReturnStillRequired')
 foreach($k in @('ownerPid','ownerThread','claimFileId','scopeStartTick','proofStartTick')){if(-not(GIInt $binding.$k 1 ([long]::MaxValue))){throw 'GLOBAL_V2_BINDING_INTEGER'}}
 foreach($k in @('originalUnlockCloseReturned','allTemporaryThreadsJoined','factProofTimely','factCaptureQualified','outerControllerReturnStillRequired')){if($entry.release.$k -isnot [bool] -or -not $entry.release.$k){throw 'GLOBAL_V2_ORIGINAL_RELEASE'}}
 if($null -ne $entry.release.failure -or -not(GIInt $entry.release.sdkChildrenEntered 1 1) -or -not(GIInt $entry.release.endTick 1 ([long]::MaxValue)) -or -not(GIInt $fr.captureStartTick 1 ([long]::MaxValue))){throw 'GLOBAL_V2_RELEASE_OR_TICK'}
 $grb=GIV2Decode64 $entry.gateReceiptBase64 16384;$pb=GIV2Decode64 $entry.initialProofBase64 4096;$gr=GIV2Json (GIV2Utf8 $grb) 16384;$pr=GIV2Json (GIV2Utf8 $pb) 4096
 GIExact $gr @('schema','scope','planId','kind','generation','ownerPid','ownerThread','checkerPid','temporaryResourcesReturned','scopeClaimIntentionallyRetained','claimFileId','claimPath','scopeStartTick','proofStartTick','checkerSourceSha256','gateSourcesSha256','entrySha256','ownerSha256','routeSha256','events','controlBeforeReceipt','receiptWriteBytes','physicalIO','sourceHashBytes','sourceHashReads')
 if($gr.schema -cne 'ENTRY_GATE_RETURN_V2' -or (GIV2BytesSha $grb) -cne $binding.gateReceiptSha256 -or (GIV2BytesSha $pb) -cne $binding.initialProofSha256 -or $pr.captureReceiptSha256 -cne $binding.gateReceiptSha256 -or $gr.scope -cne $binding.scope -or $gr.generation -cne $binding.generation -or $gr.ownerPid -ne $binding.ownerPid -or $gr.ownerThread -ne $binding.ownerThread -or $gr.claimFileId -ne $binding.claimFileId -or $gr.scopeStartTick -ne $binding.scopeStartTick -or $gr.proofStartTick -ne $binding.proofStartTick -or $gr.gateSourcesSha256 -cne $binding.gateSourcesSha256 -or $gr.routeSha256 -cne $binding.routeProofSha256){throw 'GLOBAL_V2_GATE_ORIGINAL_CHAIN'}
 if($binding.scopeStartTick -gt $binding.proofStartTick -or $binding.proofStartTick -gt $fr.captureStartTick -or $fr.captureStartTick -gt $entry.release.endTick -or $fr.captureStartTick-$binding.proofStartTick -ge 10000 -or $fr.captureStartTick-$binding.scopeStartTick -ge 30000 -or $entry.release.endTick-$binding.scopeStartTick -ge 90000){throw 'GLOBAL_V2_ORIGINAL_TICK_WINDOWS'}
 if($fr.schema -cne 'GLOBAL_IDLE_FACT_CAPTURE_V2' -or $fr.scope -cne $b.factScope -or $fr.rawSha256 -cne (GIV2BytesSha $raw) -or $fr.rawBytes -ne $raw.Length -or $entry.receiptSha256 -cne $b.receiptSha256 -or $fr.externalPreauthSha256 -cne (GIV2Sha $body.preauthUtf8) -or $fr.externalPreauthSha256 -cne $b.externalPreauthSha256 -or $fr.runtimeBindingSha256 -cne $b.runtimeBindingSha256 -or $binding.schema -cne 'GLOBAL_IDLE_FACT_RUNTIME_BINDING_V1' -or $binding.ownerPid -ne $o.ownerPid -or $binding.gateReceiptSha256 -cne $b.gateReceiptSha256 -or $binding.initialProofSha256 -cne $b.initialProofSha256){throw 'GLOBAL_V2_PACKET_BINDING'}
 GIExact $r.home @('package','component','process','user','uid','systemFlag')
 if($r.home.package -isnot [string] -or $r.home.component -isnot [string] -or -not $r.home.component.StartsWith($r.home.package,[StringComparison]::Ordinal)){throw 'GLOBAL_V2_HOME_RAW_RESOLVER'}
 if($f.values.home -cne ($r.home.package+'/'+$r.home.component) -and $f.values.home -cne ($r.home.package+'/'+$r.home.component.Substring($r.home.package.Length))){throw 'GLOBAL_V2_HOME_RAW_RESOLVER'}
 $original=[ordered]@{};foreach($k in @('waitReturned','stdoutEOF','stderrEOF','originalPipesClosed','originalHandleClosed','controllerReturned','unknown','exitCode')){$original[$k]=$o.$k}
 $q=[pscustomobject][ordered]@{schema='GLOBAL_IDLE_QUALIFICATION_V2';mode=$wire.mode;fixtureOnly=$wire.fixtureOnly;targetScope=$wire.targetScope;targetRunId=$wire.targetRunId;targetSourceSealSha256=$wire.targetSourceSealSha256;targetPlanSha256=$wire.targetPlanSha256;factScope=$b.factScope;factCaptureReceiptSha256=$b.receiptSha256;factOuterReturnSha256=$b.outerReturnSha256;collectorSourceSha256=$b.collectorSha256;factPlanSha256=$b.factPlanSha256;rawSha256=$b.rawSha256;rawBytes=$b.rawBytes;routeProofSha256=$fr.routeProofSha256;sdkSha256='b4a6b455702684652cccf7b46258b29e653538904359a58fd4931cf3ef286b3f';collectedAtUtc=$fr.collectedAtUtc;expiresAtUtc=$r.expiresUtc;originalReturn=[pscustomobject]$original;grammar='API31_APP_PERS_V1';serial='HA1Q6WXR';model=$f.values.model;api=[int]$f.values.api;fingerprint=$f.values.firmware;user=[int]$f.values.user;home=$r.home;services=$r.services;systemPackages=@($f.systemPackages);reviewEvidenceSha256=$wire.reviewEvidenceSha256;authorizationKind=$wire.authorizationKind;externalPreauthSha256=$b.externalPreauthSha256;runtimeBindingSha256=$b.runtimeBindingSha256;bundleSha256=$wire.bundleSha256;adapterSourceSha256=$wire.adapterSourceSha256;reviewSha256=$wire.reviewEvidenceSha256;reviewSourceThreadId=$r.sourceThreadId;reviewSourceTurnId=$r.sourceTurnId;approved=$r.approvedForQualification;targetPlanId=$wire.targetPlanId;reviewUtf8=$body.reviewUtf8;candidateUtf8=$body.candidateUtf8;bundleUtf8=$body.bundleUtf8;outerReturnUtf8=$body.outerReturnUtf8}
 # Exact HOME and service evidence remains in the approved source body, never
 # replaced by a bare review hash or an OEM/systemFlag exemption.
 $homeExpected=[pscustomobject][ordered]@{schema='GLOBAL_IDLE_HOME_REVIEW_EVIDENCE_V1';mode=$wire.mode;factScope=$b.factScope;rawSha256=$b.rawSha256;firmware=$q.fingerprint;home=$q.home;statement='EXACT_OBSERVED_HOME_IDENTITY'}
 $hv=$body.policyEvidence.PSObject.Properties[$r.homeEvidenceSha256]
 if($null -eq $hv -or (GIV2Sha $hv.Value) -cne $r.homeEvidenceSha256 -or -not(GIV2Same (GIV2Json $hv.Value 8388608) $homeExpected)){throw 'GLOBAL_V2_HOME_EVIDENCE'}
 foreach($s in $q.services){$ev=$body.policyEvidence.PSObject.Properties[$s.evidenceSha256];if($null -eq $ev -or (GIV2Sha $ev.Value) -cne $s.evidenceSha256){throw 'GLOBAL_V2_SERVICE_EVIDENCE'};$proof=GIV2Json $ev.Value 8388608;GIExact $proof @('schema','mode','rawSha256','packages','process','user','uid','kind','state','category','firmware','factScope','validFromUtc','validToUtc','range');if($proof.schema -cne 'GLOBAL_IDLE_SERVICE_REVIEW_EVIDENCE_V1' -or $proof.mode -cne $q.mode -or $proof.rawSha256 -cne $q.rawSha256){throw 'GLOBAL_V2_SERVICE_EVIDENCE'};foreach($k in @('packages','process','user','uid','kind','state','category','firmware','factScope','validFromUtc','validToUtc','range')){if(-not(GIV2Same $proof.$k $s.$k)){throw 'GLOBAL_V2_SERVICE_EVIDENCE'}}}
 return $q
}
function InitializeGIV2SourceBudget($ticket,$ad,$policy){
 GIExact $ticket @('schema','scope','generation','ownerPid','ownerThread','requestId','ticketId','version','baseGateBytes','baseGateReads','baseRunnerBytes','baseRunnerReads','reservedBytes','reservedReads')
 if($null -ne $global:VideoKitQ03SourceBudget){throw 'GLOBAL_V2_SOURCE_AUTHORITY_ALREADY_BOUND'}
 if($ticket.schema -cne 'QUALIFICATION_SOURCE_RESERVATION_V1' -or $ticket.scope -cne $policy.scope -or $ticket.scope -cne $ad.scope -or $ticket.requestId -cne $ad.id -or $ticket.ownerPid -ne $ad.ownerPid -or $ticket.generation -cne $ad.gateHandoff.generation -or $ticket.ticketId -cnotmatch '^[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{12}$'){throw 'GLOBAL_V2_SOURCE_AUTHORITY_BINDING'}
 foreach($k in @('ownerPid','ownerThread','version','baseGateBytes','baseGateReads','baseRunnerBytes','baseRunnerReads','reservedBytes','reservedReads')){if(-not(GIInt $ticket.$k 0 ([long]::MaxValue))){throw 'GLOBAL_V2_SOURCE_AUTHORITY_TYPE'}}
 if($ticket.baseGateBytes+$ticket.reservedBytes -gt 268435456 -or $ticket.baseGateReads+$ticket.reservedReads -gt 64 -or $ticket.baseRunnerBytes+$ticket.reservedBytes -gt 536870912 -or $ticket.baseRunnerReads+$ticket.reservedReads -gt 256){throw 'GLOBAL_V2_SOURCE_AUTHORITY_CAP'}
 $global:VideoKitQ03SourceBudget=@{ticket=$ticket;events=[Collections.Generic.List[object]]::new();used=[long]0;reads=[long]0}
}
function ReserveGIV2Reference([long]$bytes,[string]$path){
 $s=$global:VideoKitQ03SourceBudget
 if($null -eq $s -or $null -eq $s.ticket){throw 'GLOBAL_V2_SOURCE_AUTHORITY_REQUIRED'}
 if($bytes -le 0 -or $s.used+$bytes -gt $s.ticket.reservedBytes -or $s.reads+1 -gt $s.ticket.reservedReads){throw 'GLOBAL_V2_EVIDENCE_SOURCE_BUDGET'}
 $s.used+=$bytes;$s.reads++;$e=@{path=$path;reservedBytes=$bytes;actualBytes=[long]0;closeReturned=$false;opened=$false;unknown=$false};$s.events.Add($e);return $e
}
function GetGIV2SourceDelta {
 $s=$global:VideoKitQ03SourceBudget;if($null -eq $s){return $null};$t=$s.ticket
 return @{schema='QUALIFICATION_SOURCE_DELTA_V1';ticketId=$t.ticketId;scope=$t.scope;generation=$t.generation;ownerPid=$t.ownerPid;requestId=$t.requestId;version=$t.version;reservedUsedBytes=$s.used;sourceReads=$s.reads;actualBytes=[long](($s.events|Measure-Object actualBytes -Sum).Sum);events=@($s.events.ToArray()|ForEach-Object {@{pathSha256=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($_.path))).ToLowerInvariant();reservedBytes=$_.reservedBytes;actualBytes=$_.actualBytes;closeReturned=$_.closeReturned;opened=$_.opened;unknown=$_.unknown}});finished=$true}
}
