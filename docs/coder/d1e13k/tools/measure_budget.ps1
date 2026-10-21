param([Parameter(Mandatory=$true)][string]$Candidate)
$ErrorActionPreference='Stop'
$candidatePath=[IO.Path]::GetFullPath($Candidate)
$request=Get-Content -LiteralPath (Join-Path $candidatePath 'release/observer-request.json') -Raw|ConvertFrom-Json
function ByteCount([string]$s){return [Text.UTF8Encoding]::new($false).GetByteCount($s)}
$maximum=[decimal]::Parse('18446744073709551615')
$failures=[Collections.Generic.List[string]]::new()
1..4|ForEach-Object {$failures.Add('METADATA_WRITE_FAILED');$failures.Add('METADATA_CLOSE_UNKNOWN')}
foreach($name in @('PID_RECORDING_FAILED','PENDING_RECORD_FAILED','FINAL_RECEIPT_WRITE_FAILED','PROCESS_DISPOSE_UNKNOWN')){$failures.Add($name)}
foreach($role in @('stdout','stderr')){foreach($suffix in @('_EXISTING_RECORD_NOT_REPLACED','_OPEN_RECORD_UNKNOWN','_WRITE_FAILED','_ORIGINAL_READ_FAILED','_PIPE_CLOSE_UNKNOWN','_ARCHIVE_CLOSE_UNKNOWN')){$failures.Add($role+$suffix)}}
$failures.Add('ORIGINAL_OBSERVER_EXCEPTION_'+('X'*80))
$readers=@('stdout','stderr')|ForEach-Object {@{role=$_;readReturned=$false;eof=$false;pipeClosed=$false;archiveClosed=$false;recordFailed=$false;rawBytes=$maximum;savedBytes=$maximum}}
$facts=@{id=$request.id;scope=$request.scope;pid=2147483647;responseTimedOut=$false;originalWaitReturned=$false;originalProcessDisposed=$false;originalStdinClosed=$false;exitCode=-2147483648;originalBytes=$maximum;overflow=$false;recordingFailures=@($failures);allOriginalProcessAndPipesReturned=$false;allOriginalResourcesReturned=$null;receiptOwnCloseNotProvenByThisFile=$true;readers=@($readers)}
$receipt=($facts|ConvertTo-Json -Depth 8)
$facts.metadataRecordFilesReturnedAtConsole=$false
$facts.metadataRecords=@('intent.json','original-pid.json','pending.json','receipt.json')|ForEach-Object {@{name=$request.id+'-'+$_;openEntered=$false;openReturned=$false;writeReturned=$false;closeEntered=$false;closed=$false}}
$facts.allOriginalResourcesReturned=$false
$console=($facts|ConvertTo-Json -Depth 8)
$pending=@{state='PENDING_SAME_ORIGINAL_CUSTODY';pid=2147483647;scope=$request.scope}|ConvertTo-Json
$pidText=@{pid=2147483647;startUtc='9999-12-31T23:59:59.9999999Z';scope=$request.scope}|ConvertTo-Json
$parts=[ordered]@{typedRelease=(Get-Item -LiteralPath (Join-Path $candidatePath 'release/read-only-release.json')).Length;executionScope=(Get-Item -LiteralPath (Join-Path $candidatePath 'release/execution-scope.json')).Length;observerRequest=(Get-Item -LiteralPath (Join-Path $candidatePath 'release/observer-request.json')).Length;observerIntent=(ByteCount ($request|ConvertTo-Json -Depth 12));pidRecord=(ByteCount $pidText);pendingRecord=(ByteCount $pending);receiptFile=(ByteCount $receipt);factsConsole=(ByteCount $console);consoleFramingMarkerAndBoundedSummary=256}
$sum=0;foreach($v in $parts.Values){$sum+=[long]$v}
$parts.executionCommandRequest=(Get-Item -LiteralPath (Join-Path $candidatePath 'release/execution-command.json')).Length
$sum+=$parts.executionCommandRequest
$result=@{status=if($sum -le 8192){'PASS'}else{'EXCEEDS_NO_EXECUTION'};bound=8192;totalUpperBound=$sum;remaining=8192-$sum;parts=$parts;failureLabels=25;metadataRecordMax=4;fixedRuntimeExceptionTypeNameReservation=80;earlyGateInputsPlusErrorConsoleBound=(($parts.typedRelease+$parts.executionScope+$parts.observerRequest+$parts.executionCommandRequest)+2048);note='Conservative union of mutually exclusive coded failures; unsigned64 numeric sizes, exact one-pin request and exact outer command JSON, original PS serialization. Full observer console captured once, not echoed again; summary<=128B within256B framing reserve. Fixed PS/.NET exception families use80 character type-name reserve, not arbitrary injected code/types. No runtime role executed.'}
$result|ConvertTo-Json -Depth 8
if($sum -gt 8192){exit 2}
