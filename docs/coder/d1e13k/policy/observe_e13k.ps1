param([Parameter(Mandatory=$true)][string]$RequestPath)
$ErrorActionPreference='Stop'
if([IO.Path]::GetFullPath($RequestPath) -ne 'D:\CodexProjects\VideoKit\docs\coder\d1e13k\release\observer-request.json' -or (Get-FileHash -LiteralPath $RequestPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne 'a2040964fbcbae5e070d84472a7e4d73454e6f1488441466cc96ec8723e5bf5d'){throw 'K_EXACT_OBSERVER_REQUEST_ONLY'}
$request=Get-Content -LiteralPath $RequestPath -Raw|ConvertFrom-Json
$root=[IO.Path]::GetFullPath($request.evidenceRoot)
if($root -ne 'D:\CodexProjects\VideoKit\docs\tester\D1_E13J_R1_G_SUPPLEMENT_EVIDENCE'){throw 'Fixed J-only evidence root required'}
foreach($pin in $request.pins){if((Get-FileHash -LiteralPath $pin.path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $pin.sha256){throw 'Reviewed input pin changed'}}
$argv=@($request.argv)
if($argv.Count -ne 7 -or $argv[0] -ne 'D:/Android/Android Studio/jbr/bin/java.exe' -or $argv[1] -ne '-cp' -or $argv[2] -ne 'D:/CodexProjects/VideoKit/docs/coder/d1e13k/artifacts/e13k-host-tools.jar' -or $argv[3] -ne 'com.videokit.spike.e4.E13JReadOnly' -or $argv[4] -ne '--g-readonly'){throw 'Exact J-only fixed socket role required'}
$cap=[int]$request.maxTextBytes
if($cap -ne 32768 -or $request.id -ne 'E13J-R1-SUPPLEMENT-ONCE' -or $request.scope -ne '116c978327fc2240dbe04a9ead566165d231b88d14166776e03938a40b76aaef'){throw 'Exact J-only scope/text budget required'}
$approvedRequestSha='a5a7fd2f15c41f2a01f8e49f11b942c34bb23c9e890e5d6f8f275d49a7bffa03'
if($approvedRequestSha -eq 'ABSENT' -or $argv[6] -ne $approvedRequestSha){throw 'J_EXECUTION_NOT_DISPATCHED_BEFORE_PROCESS'}
# Same original local context is retained before Process/files/start, including recording faults.
if(-not (Get-Variable -Name E13OriginalCustody -Scope Global -ErrorAction SilentlyContinue)){$global:E13OriginalCustody=@{}}
$id=[string]$request.id
if($id -notmatch '^[A-Za-z0-9_-]{1,80}$'){throw 'Fixed request basename required'}
if($global:E13OriginalCustody.ContainsKey($id)){throw 'Original request already entered'}
$c=@{id=$id;process=[Diagnostics.Process]::new();started=$false;startEntered=$false;readers=@();records=@();failures=[Collections.Generic.List[string]]::new();bytes=0;overflow=$false;pending=$false;waitReturned=$false;processDisposed=$false;stdinReturned=$false;scope=[string]$request.scope}
$global:E13OriginalCustody[$id]=$c
[IO.Directory]::CreateDirectory($root)|Out-Null
$intent=Join-Path $root ($id+'-intent.json')
if(Test-Path -LiteralPath $intent){throw 'Persistent request already entered; no replay'}
function WriteOriginalRecord([string]$path,[string]$text){
 $record=@{path=$path;stream=$null;openEntered=$false;openReturned=$false;write=$null;writeReturned=$false;closeEntered=$false;closed=$false}
 $c.records+=,$record
 $bytes=[Text.UTF8Encoding]::new($false).GetBytes($text)
 if($bytes.Length -gt 8192){throw 'Bounded metadata record required'}
 $record.openEntered=$true;$record.stream=[IO.FileStream]::new($path,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read,4096,$true);$record.openReturned=$true
 $record.write=$record.stream.WriteAsync($bytes,0,$bytes.Length)
}
function ObserveRecordReturns {
 foreach($record in $c.records){if($null -ne $record.write -and $record.write.IsCompleted -and -not $record.closeEntered){try{[void]$record.write.GetAwaiter().GetResult();$record.writeReturned=$true}catch{$c.failures.Add('METADATA_WRITE_FAILED')};$record.closeEntered=$true;try{$record.stream.Close();$record.closed=$true}catch{$c.failures.Add('METADATA_CLOSE_UNKNOWN')}}}
}
$info=[Diagnostics.ProcessStartInfo]::new();$info.FileName=$argv[0];$info.UseShellExecute=$false;$info.CreateNoWindow=$true;$info.RedirectStandardInput=$true;$info.RedirectStandardOutput=$true;$info.RedirectStandardError=$true
for($i=1;$i -lt $argv.Count;$i++){$info.ArgumentList.Add([string]$argv[$i])}
$c.process.StartInfo=$info;$timer=[Diagnostics.Stopwatch]::StartNew()
try{
 WriteOriginalRecord $intent ($request|ConvertTo-Json -Depth 12)
 while(-not $c.records[0].closed){ObserveRecordReturns;if($timer.Elapsed.TotalSeconds -ge 2){throw 'Original intent record pending before child start'};Start-Sleep -Milliseconds 2}
 $c.startEntered=$true
 if(-not $c.process.Start()){throw 'Original start outcome unproven'}
 $c.started=$true;$c.pid=$c.process.Id
 foreach($role in @('stdout','stderr')){
  $stream=if($role -eq 'stdout'){$c.process.StandardOutput.BaseStream}else{$c.process.StandardError.BaseStream}
  $r=@{role=$role;stream=$stream;buffer=[byte[]]::new(4096);read=$null;write=$null;queue=[Collections.Generic.Queue[byte[]]]::new();file=$null;eof=$false;readReturned=$false;streamCloseEntered=$false;streamClosed=$false;fileCloseEntered=$false;fileClosed=$false;recordFailed=$false;bytes=0;saved=0}
  $c.readers+=,$r
  $capturePath=Join-Path $root ($id+'-'+$role+'.txt')
  if(Test-Path -LiteralPath $capturePath){$r.recordFailed=$true;$r.fileKnownNoOpen=$true;$c.failures.Add($role+'_EXISTING_RECORD_NOT_REPLACED')}else{try{$r.file=[IO.FileStream]::new($capturePath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read,4096,$true);$r.fileOpenReturned=$true}catch{$r.fileOpenUnknown=$true;$r.recordFailed=$true;$c.failures.Add($role+'_OPEN_RECORD_UNKNOWN')}}
  $r.read=$stream.ReadAsync($r.buffer,0,4096)
 }
 try{WriteOriginalRecord (Join-Path $root ($id+'-original-pid.json')) (@{pid=$c.pid;startUtc=$c.process.StartTime.ToUniversalTime().ToString('o');scope=$c.scope}|ConvertTo-Json)}catch{$c.failures.Add('PID_RECORDING_FAILED')}
 $c.process.StandardInput.Close();$c.stdinReturned=$true
 do{
  ObserveRecordReturns
  foreach($r in $c.readers){
   if($null -ne $r.write -and $r.write.IsCompleted){try{[void]$r.write.GetAwaiter().GetResult();$r.saved+=$r.writingBytes}catch{$r.recordFailed=$true;$c.failures.Add($r.role+'_WRITE_FAILED')};$r.write=$null}
   if($null -ne $r.read -and $r.read.IsCompleted){
    try{$n=$r.read.GetAwaiter().GetResult();$r.read=$null;if($n -eq 0){$r.eof=$true;$r.readReturned=$true}else{
      $c.bytes+=$n;$r.bytes+=$n
      if($c.bytes -gt $cap){$c.overflow=$true;$r.recordFailed=$true}
      if(-not $r.recordFailed -and $r.queue.Count -lt 8){$b=[byte[]]::new($n);[Array]::Copy($r.buffer,$b,$n);$r.queue.Enqueue($b)}else{$r.recordFailed=$true}
      $r.read=$r.stream.ReadAsync($r.buffer,0,4096)
     }}catch{$r.readReturned=$true;$r.recordFailed=$true;$c.failures.Add($r.role+'_ORIGINAL_READ_FAILED');$r.read=$null}
   }
   if($r.recordFailed){$r.queue.Clear()}
   if($null -eq $r.write -and $r.queue.Count -gt 0 -and -not $r.recordFailed){$b=$r.queue.Dequeue();$r.writingBytes=$b.Length;$r.write=$r.file.WriteAsync($b,0,$b.Length)}
  }
  if($timer.Elapsed.TotalSeconds -ge 55 -and -not $c.pending){$c.pending=$true;try{WriteOriginalRecord (Join-Path $root ($id+'-pending.json')) (@{state='PENDING_SAME_ORIGINAL_CUSTODY';pid=$c.pid;scope=$c.scope}|ConvertTo-Json)}catch{$c.failures.Add('PENDING_RECORD_FAILED')}}
  $done=$c.process.HasExited -and @($c.readers|Where-Object {-not $_.readReturned -or $null -ne $_.write -or $_.queue.Count -gt 0}).Count -eq 0
  if(-not $done){Start-Sleep -Milliseconds 10}
 }while(-not $done)
 $c.process.WaitForExit();$c.waitReturned=$true;$c.exitCode=$c.process.ExitCode
}catch{$c.failures.Add('ORIGINAL_OBSERVER_EXCEPTION_'+$_.Exception.GetType().Name)}
finally{
 # A live/unknown reader/process is never closed just because recording failed.
 if($c.started -and $c.waitReturned){
  foreach($r in $c.readers){
   if($r.readReturned -and -not $r.streamCloseEntered){$r.streamCloseEntered=$true;try{$r.stream.Close();$r.streamClosed=$true}catch{$c.failures.Add($r.role+'_PIPE_CLOSE_UNKNOWN')}}
   if($null -ne $r.file -and $null -eq $r.write -and -not $r.fileCloseEntered){$r.fileCloseEntered=$true;try{$r.file.Close();$r.fileClosed=$true}catch{$c.failures.Add($r.role+'_ARCHIVE_CLOSE_UNKNOWN')}}
  }
  if(@($c.readers|Where-Object {-not $_.streamClosed -or ($null -ne $_.file -and -not $_.fileClosed)}).Count -eq 0){try{$c.process.Dispose();$c.processDisposed=$true}catch{$c.failures.Add('PROCESS_DISPOSE_UNKNOWN')}}
 }
 ObserveRecordReturns
 $returned=$c.waitReturned -and $c.stdinReturned -and $c.processDisposed -and @($c.readers|Where-Object {$_.fileOpenUnknown}).Count -eq 0
 $facts=@{id=$id;scope=$c.scope;pid=$c.pid;responseTimedOut=$c.pending;originalWaitReturned=$c.waitReturned;originalProcessDisposed=$c.processDisposed;originalStdinClosed=$c.stdinReturned;exitCode=$c.exitCode;originalBytes=$c.bytes;overflow=$c.overflow;recordingFailures=@($c.failures);allOriginalProcessAndPipesReturned=$returned;allOriginalResourcesReturned=$null;receiptOwnCloseNotProvenByThisFile=$true;readers=@($c.readers|ForEach-Object {@{role=$_.role;readReturned=$_.readReturned;eof=$_.eof;pipeClosed=$_.streamClosed;archiveClosed=$_.fileClosed;recordFailed=$_.recordFailed;rawBytes=$_.bytes;savedBytes=$_.saved}})}
 try{WriteOriginalRecord (Join-Path $root ($id+'-receipt.json')) ($facts|ConvertTo-Json -Depth 8)}catch{$c.failures.Add('FINAL_RECEIPT_WRITE_FAILED')}
 $recordDeadline=[DateTime]::UtcNow.AddSeconds(2)
 do{ObserveRecordReturns;$recordsReturned=@($c.records|Where-Object {-not $_.closed}).Count -eq 0;if(-not $recordsReturned){Start-Sleep -Milliseconds 2}}while(-not $recordsReturned -and [DateTime]::UtcNow -lt $recordDeadline)
 $returned=$returned -and $recordsReturned
 $facts.metadataRecordFilesReturnedAtConsole=$recordsReturned
 $facts.metadataRecords=@($c.records|ForEach-Object {@{name=[IO.Path]::GetFileName($_.path);openEntered=$_.openEntered;openReturned=$_.openReturned;writeReturned=$_.writeReturned;closeEntered=$_.closeEntered;closed=$_.closed}})
 $facts.allOriginalResourcesReturned=$returned
 $facts|ConvertTo-Json -Depth 8
 if($returned){$global:E13OriginalCustody.Remove($id)}else{Write-Output 'PENDING_ORIGINAL_CONTEXT_RETAINED_NO_SECOND_CLOSE';while($true){Start-Sleep -Milliseconds 500}}
}
