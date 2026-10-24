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
