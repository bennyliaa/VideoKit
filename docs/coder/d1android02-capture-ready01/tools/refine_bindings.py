from pathlib import Path
import json
B=Path(__file__).resolve().parents[1]
p=B/'reference/exact-seven-role-plan.json';v=json.loads(p.read_text());v['product']['caseOrder']=['preopenAdmission','rejectFixture','cancelLateRead','writerPending','inspectKnown','inspectShort3','inspectUnknown','inspectSeek1s','bbbObserve','muxQualified'];v['preparedWallCeilingsNotExecutionAuthorization']={'wholeScopeSecondsMaximum':600,'localProofSecondsMaximum':30,'outerSecondsMaximum':600,'exactScopeValues':'UNASSIGNED_UNTIL_NEW_REVIEWED_ACTIVATION','240IsOnlyQualificationWindowSum':True};p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=B/'tools/admission.ps1.txt';s=p.read_text();s='[CmdletBinding()]\n'+s;s=s.replace("$ErrorActionPreference='Stop'","if(@($PSBoundParameters.Keys|Where-Object {$_ -cnotin @('RequestPath','PredecessorProofSha')}).Count -ne 0){throw 'EXTRA_ENTRY_ARGUMENT_REJECTED'}\n$ErrorActionPreference='Stop'",1)
s=s.replace("$request.qualificationSeconds -isnot [ValueType]","($request.qualificationSeconds -isnot [long] -and $request.qualificationSeconds -isnot [int] -and $request.qualificationSeconds -isnot [double])")
s=s.replace("$args=@($s.argv|","$roleArgv=@($s.argv|").replace("argv=$args;maxTextBytes","argv=$roleArgv;maxTextBytes")
s=s.replace("'wholeWallSeconds','localProofSeconds','outerSeconds','approvedForExecution'","'wholeWallSeconds','localProofSeconds','outerSeconds','freshRouteProofSha256','initialPredecessorProofSha256','approvedForExecution'")
needle=" $route=ReadJsonExact $policy.freshRouteProof.path"
s=s.replace(needle," if($activation.freshRouteProofSha256 -cne $policy.freshRouteProof.sha256){throw 'FRESH_ROUTE_AUTHORIZATION_BINDING'}\n"+needle)
needle=" foreach($key in @('ADB_SERVER_SOCKET'"
s=s.replace(needle," $checked=[DateTimeOffset]::Parse($route.checkedAtUtc);$created=[DateTimeOffset]::Parse($route.serverCreationUtc);$age=([DateTimeOffset]::UtcNow-$checked).TotalSeconds;if($age -lt 0 -or $age -ge $activation.wholeWallSeconds -or $created -gt $checked){throw 'FRESH_ROUTE_TIME_UNPROVEN'}\n"+needle)
s=s.replace("$batchSdkBefore=$proof.batchSdkChildrenEntered;","if([long]$groups.preflight+[long]$groups.install+[long]$groups.instrument+[long]$groups.control -ne [long]$proof.batchTextChargedBytesKnown){throw 'EXACT_AGGREGATE_GROUP_SUM'}\n $batchSdkBefore=$proof.batchSdkChildrenEntered;")
needle="  if((Digest $nativePath) -cne"
s=s.replace(needle,"  foreach($k in @('originalControllerWaitReturned','sameOriginalPipeReadersJoined','outerStreamsClosed','originalWindowsProcessHandleCloseReturned')){if($native.$k -isnot [bool] -or -not $native.$k){throw 'EXACT_OUTER_RETURN_TYPES'}}\n"+needle)
s=s.replace("$co.batchSdkChildrenEntered -ne $batchSdkBefore","$co.batchTextChargedBytesKnown -ne $batchTextBefore -or $co.batchSdkChildrenEntered -ne $batchSdkBefore")
s=s.replace("if(-not $fixture){$age=[Environment]::TickCount64", "if(-not $fixture -and $index -eq 0 -and $PredecessorProofSha -cne $activation.initialPredecessorProofSha256){throw 'INITIAL_ORIGINAL_GATE_AUTHORIZATION_BINDING'}\nif(-not $fixture){$age=[Environment]::TickCount64")
p.write_text(s,encoding='utf-8')
p=B/'tools/semantic-gates.ps1.txt';s=p.read_text().replace('$matches','$receiptMatches');s=s.replace("if($p.fixtureOnly -ne $true -or $p.bytes -ne $c.input.expectedBytes -or $p.sha256 -cne $c.input.expectedSha)","$expectedPin=@($slots|Where-Object id -CEQ $Id)[0].payloadPin;if($p.fixtureOnly -ne $true -or $p.bytes -ne $expectedPin.bytes -or $p.sha256 -cne $expectedPin.sha256)")
needle="  # SDK/watcher return"
checks="""  if(-not $IsFixture){
   for($i=0;$i -lt 10;$i++){if($p.caseReceipts[$i].case -cne $plan.product.caseOrder[$i] -or $p.caseReceipts[$i].caseOriginalResourcesReturned -ne $true){return 'APP_ORDERED_HISTORY_UNPROVEN'}}
   if($p.identity.targetPackage -cne 'com.videokit.d1media3.android02' -or $p.identity.testPackage -cne 'com.videokit.d1media3.android02.test' -or $p.identity.processName -cne 'com.videokit.d1media3.android02:media3'){return 'APP_REPORTED_IDENTITY_UNPROVEN'}
   foreach($pkg in @('com.videokit.d1media3.android02','com.videokit.d1media3.android02.test')){$identity=$p.identity.PSObject.Properties[$pkg].Value;if($identity.versionName -cne $plan.product.version -or $identity.signerSha256 -cne $plan.product.signerCertificateSha256){return 'APP_REPORTED_VERSION_SIGNER_UNPROVEN'}}
   if($p.meter.scopeInputReserved -gt 8388608 -or $p.meter.scopeOutputRequested -gt 16777216 -or $p.meter.scopeOutputAttempted -gt 16777216 -or $p.meter.knownNativeFdActive -ne 0 -or $p.meter.assetStreamActive -ne 0 -or $p.meter.unknownAllocationOrClose -ne 0){return 'APP_REPORTED_ACCOUNTING_UNPROVEN'}
   $mux=$p.caseReceipts[9];if($mux.muxerKeeper.returned -ne $true -or $mux.muxerKeeper.eosReturned -ne $true -or $mux.muxerKeeper.sampleWritesReturned -ne 6 -or $mux.muxReopenCalls -ne 1 -or $mux.muxReadyCalls -ne 0 -or $mux.muxNativeSyncReturned -ne $true -or $mux.reopened.actualExtractorClass -cne 'androidx.media3.extractor.mp4.FragmentedMp4Extractor'){return 'APP_REPORTED_MUX_CHAIN_UNPROVEN'}
  }
"""
assert needle in s;s=s.replace(needle,checks+needle);p.write_text(s,encoding='utf-8')
# The first adaptation must preserve the original id key.
# Actual replacement template originally began with semanticChecked, dropping id.
s=s.replace('"$c=@{id=$request.id;semanticChecked', '"$c=@{id=$request.id;semanticChecked')
s=s.replace('"$c=@{id=$request.id;","$c=@{semanticChecked', '"$c=@{id=$request.id;","$c=@{id=$request.id;semanticChecked')
s=s.replace("'wholeWallSeconds':None,'localProofSeconds':None,'outerSeconds':None,'approvedForExecution':False", "'wholeWallSeconds':None,'localProofSeconds':None,'outerSeconds':None,'freshRouteProofSha256':None,'initialPredecessorProofSha256':None,'approvedForExecution':False")
p.write_text(s,encoding='utf-8')
print('Bindings, fresh-route authority/time, exact cumulative sums and receipt-only limited product semantics refined before any selfcheck')
