param([Parameter(Mandatory=$true)][string]$InputFile,[Parameter(Mandatory=$true)][string]$OutputFile)
$ErrorActionPreference='Stop'
$script:rows=[Collections.Generic.List[object]]::new();$script:complete=$false;$script:fatal=$null;$script:outputRootValidated=$false;$script:moduleLoaded=$false;$script:failureDelta=$null;$script:fullReferenceDelta=$null
$script:expectedIds=@('no-original-authority','fixed-file-positive','same-global-authority-after-reload','reinitialize-same-context','wrong-hash-charged-and-close','wrong-identity-charged-and-close','no-read-after-four-consumes','reload-keeps-rejection-budget','cap-before-open:baseGateBytes','cap-before-open:baseGateReads','cap-before-open:baseRunnerBytes','cap-before-open:baseRunnerReads','base-missing-not-default-zero','wrong-ticket-scope','base-bool','zero-reservation','real-issued-wire-with-explicit-synthetic-ticket','duplicate-initialize-after-full-reference')
function Persist {
 if(-not $script:outputRootValidated){return}
 $delta=if($script:moduleLoaded){GetGIV2SourceDelta}else{$null}
 $ids=@($script:rows|ForEach-Object {$_.id})
 $sameIds=($ids.Count -eq $script:expectedIds.Count -and ($ids -join '|') -ceq ($script:expectedIds -join '|'))
 $all=$script:complete -and $sameIds -and $null -eq $script:fatal -and @($script:rows|Where-Object {-not $_.pass}).Count -eq 0
 $result=@{schema='INDEPENDENT_Q07_BUDGET_RESULT_V1';complete=[bool]$script:complete;expectedCaseIds=$script:expectedIds;observedCaseIds=$ids;results=@($script:rows.ToArray());allPassed=[bool]$all;fatalError=$script:fatal;syntheticAuthority=$true;realAuthority=$false;actualProductionOwner=$false;moduleLoaded=[bool]$script:moduleLoaded;fileHelperMode='Original frozen functions on future own fixed files with explicit synthetic ticket';shortReadUnknown='NOT_INJECTED_REAL_UNKNOWN';sourceDelta=$delta;failureDelta=$script:failureDelta;fullReferenceDelta=$script:fullReferenceDelta}
 [IO.File]::WriteAllText($OutputFile,($result|ConvertTo-Json -Depth 24 -Compress),[Text.UTF8Encoding]::new($false))
}
function Check($id,[scriptblock]$fn,$want){
 try{[void](& $fn);$reason='ACCEPT'}catch{$reason=$_.Exception.Message}
 $s=$global:VideoKitQ03SourceBudget
 $script:rows.Add(@{id=$id;want=$want;reason=$reason;pass=[bool]($reason -ceq $want);used=if($s){$s.used}else{0};reads=if($s){$s.reads}else{0};authority='SYNTHETIC_TICKET_NO_REAL_PARENT_RESET'})
 Persist
}
function Ticket($bytes,$reads){return [pscustomobject]@{schema='QUALIFICATION_SOURCE_RESERVATION_V1';scope=$i.context.scope;generation='00000000-0000-0000-0000-000000000005';ownerPid=$PID;ownerThread=1;requestId='INDEPENDENT_MODEL';ticketId=[guid]::NewGuid().ToString();version=0;baseGateBytes=0;baseGateReads=0;baseRunnerBytes=0;baseRunnerReads=0;reservedBytes=$bytes;reservedReads=$reads}}
function Init($t){$a=[pscustomobject]@{scope=$i.context.scope;id='INDEPENDENT_MODEL';ownerPid=$PID;gateHandoff=[pscustomobject]@{generation='00000000-0000-0000-0000-000000000005'}};$p=[pscustomobject]@{scope=$i.context.scope};InitializeGIV2SourceBudget $t $a $p}
try{
 $inPath=[IO.Path]::GetFullPath($InputFile);$outPath=[IO.Path]::GetFullPath($OutputFile);$scope=Split-Path $inPath
 if($inPath -cne $InputFile -or $outPath -cne $OutputFile -or (Split-Path -Leaf $inPath) -cne 'budget-input.json' -or $outPath -cne (Join-Path $scope 'budget-result.json') -or -not $scope.StartsWith(($PSScriptRoot+'\fixtures\'),[StringComparison]::Ordinal)){throw 'HELPER_FIXED_IO_ROOT'}
 $script:outputRootValidated=$true
 $raw=[IO.File]::ReadAllBytes($InputFile);if($raw.Length -gt 1048576){throw 'HELPER_INPUT_BYTE_BOUND'}
 $i=[Text.UTF8Encoding]::new($false,$true).GetString($raw)|ConvertFrom-Json -Depth 24 -DateKind String
 $keys=@('schema','artifactRoot','candidateRoot','admissionPath','admissionSha256','ref','root','name','wire','context','expectedFingerprint','expectedCaseIds')
 if(@(Compare-Object -CaseSensitive @($i.PSObject.Properties.Name|Sort-Object) @($keys|Sort-Object)).Count -or $i.schema -cne 'INDEPENDENT_BUDGET_INPUT_V1' -or $i.artifactRoot -cne $PSScriptRoot -or $i.admissionPath -cne (Join-Path $i.candidateRoot 'tools/admission_checks.ps1') -or ($i.expectedCaseIds -join '|') -cne ($script:expectedIds -join '|')){throw 'HELPER_INPUT_SCHEMA_OR_SOURCE_ROOT'}
 $module=$i.admissionPath
 if((Get-FileHash -LiteralPath $module -Algorithm SHA256).Hash.ToLowerInvariant() -cne $i.admissionSha256){throw 'HELPER_ADMISSION_SOURCE_PIN'}
 . $module;$script:moduleLoaded=$true
 Check 'no-original-authority' {GIV2ReadReference $i.ref $i.root $i.name|Out-Null} 'GLOBAL_V2_SOURCE_AUTHORITY_REQUIRED'
 $t=Ticket 4 4;Init $t
 Check 'fixed-file-positive' {GIV2ReadReference $i.ref $i.root $i.name|Out-Null} 'ACCEPT'
 $held=$global:VideoKitQ03SourceBudget;$prior=$held.used;. $module
 Check 'same-global-authority-after-reload' {if(-not [object]::ReferenceEquals($held,$global:VideoKitQ03SourceBudget) -or $global:VideoKitQ03SourceBudget.used -ne $prior){throw 'TESTER_RESET_OBSERVED'};GIV2ReadReference $i.ref $i.root $i.name|Out-Null} 'ACCEPT'
 Check 'reinitialize-same-context' {Init $t} 'GLOBAL_V2_SOURCE_AUTHORITY_ALREADY_BOUND'
 $bad=$i.ref|ConvertTo-Json -Compress|ConvertFrom-Json;$bad.sha256='0'*64
 Check 'wrong-hash-charged-and-close' {GIV2ReadReference $bad $i.root $i.name|Out-Null} 'GLOBAL_V2_EVIDENCE_ORIGINAL_BYTES'
 $bad=$i.ref|ConvertTo-Json -Compress|ConvertFrom-Json;$bad.fileId='1'
 Check 'wrong-identity-charged-and-close' {GIV2ReadReference $bad $i.root $i.name|Out-Null} 'GLOBAL_V2_EVIDENCE_FILE_IDENTITY'
 Check 'no-read-after-four-consumes' {GIV2ReadReference $i.ref $i.root $i.name|Out-Null} 'GLOBAL_V2_EVIDENCE_SOURCE_BUDGET'
 $script:failureDelta=GetGIV2SourceDelta;$held=$global:VideoKitQ03SourceBudget;. $module
 Check 'reload-keeps-rejection-budget' {if(-not [object]::ReferenceEquals($held,$global:VideoKitQ03SourceBudget)){throw 'TESTER_CONTEXT_REPLACED'};GIV2ReadReference $i.ref $i.root $i.name|Out-Null} 'GLOBAL_V2_EVIDENCE_SOURCE_BUDGET'
 # Explicit new independent synthetic contexts, never a production authority reset.
 foreach($field in @('baseGateBytes','baseGateReads','baseRunnerBytes','baseRunnerReads')){
  $global:VideoKitQ03SourceBudget=$null;$t=Ticket 1 1;$t.$field=if($field -like '*Bytes'){if($field -like '*Runner*'){536870912}else{268435456}}else{if($field -like '*Runner*'){256}else{64}}
  Check ('cap-before-open:'+$field) {Init $t} 'GLOBAL_V2_SOURCE_AUTHORITY_CAP'
 }
 $global:VideoKitQ03SourceBudget=$null;$t=Ticket 1 1;$t.PSObject.Properties.Remove('baseGateBytes');Check 'base-missing-not-default-zero' {Init $t} 'GLOBAL_QUAL_SCHEMA'
 $global:VideoKitQ03SourceBudget=$null;$t=Ticket 1 1;$t.scope='0'*64;Check 'wrong-ticket-scope' {Init $t} 'GLOBAL_V2_SOURCE_AUTHORITY_BINDING'
 $global:VideoKitQ03SourceBudget=$null;$t=Ticket 1 1;$t.baseGateReads=$true;Check 'base-bool' {Init $t} 'GLOBAL_V2_SOURCE_AUTHORITY_TYPE'
 $global:VideoKitQ03SourceBudget=$null;$t=Ticket 0 0;Init $t;Check 'zero-reservation' {GIV2ReadReference $i.ref $i.root $i.name|Out-Null} 'GLOBAL_V2_EVIDENCE_SOURCE_BUDGET'
 $global:VideoKitQ03SourceBudget=$null;$t=Ticket 10485760 8;Init $t
 Check 'real-issued-wire-with-explicit-synthetic-ticket' {$q=GIQualification $i.wire $i.context;if($q.fingerprint -cne $i.expectedFingerprint){throw 'TESTER_FIRMWARE_MISMATCH'}} 'ACCEPT'
 $script:fullReferenceDelta=GetGIV2SourceDelta
 Check 'duplicate-initialize-after-full-reference' {Init $t} 'GLOBAL_V2_SOURCE_AUTHORITY_ALREADY_BOUND'
 $script:complete=$true
}catch{$script:fatal=@{type=$_.Exception.GetType().FullName;message=$_.Exception.Message}}
finally{Persist}
if(-not $script:complete -or $null -ne $script:fatal -or @($script:rows|Where-Object {-not $_.pass}).Count){exit 2}
