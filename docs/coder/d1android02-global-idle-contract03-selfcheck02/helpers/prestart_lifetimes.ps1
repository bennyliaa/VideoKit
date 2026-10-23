param([string]$OutputFile)
$ErrorActionPreference='Stop'
$b='D:\CodexProjects\VideoKit\docs\coder\d1android02-global-idle-contract03-fix'
. (Join-Path $b 'tools/admission_checks.ps1')
$w=Join-Path (Split-Path $OutputFile) ('prestart-'+[Guid]::NewGuid().ToString('N'));[void][IO.Directory]::CreateDirectory($w)
function Assert($x,[string]$why){if(-not $x){throw $why}}
function NewContext {
 return @{process=$null;processCreateEntered=$false;processCreateReturned=$false;processDisposed=$false;processDisposeEntered=$false;processDisposeCalls=0;startEntered=$false;startReturned=$false;started=$false;startUnknown=$false;lockOpenUnknown=$false;readers=@();input=@{source=$null;openEntered=$false;openReturned=$false;sourceClosed=$true;sourceCloseEntered=$false;pinHashCreateEntered=$false;pinHashCreateReturned=$false;pinHashDisposed=$false};noStartResourcesReturned=$false}
}
function Raw([string]$path){
 $r=@{file=$null;fileOpenEntered=$true;fileOpenReturned=$false;fileOpenUnknown=$false;fileCloseEntered=$false;fileClosed=$false;fileCloseCalls=0;pipe=$null;pipeOpenEntered=$false;pipeNeverCreated=$false;pipeClosed=$false;read=$null;write=$null;eof=$false}
 $r.file=[IO.FileStream]::new($path,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read);$r.fileOpenReturned=$true
 $r.file.Write([byte[]]@(1,2,3,4));return $r
}
$results=[Collections.Generic.List[object]]::new()
foreach($n in @(0,1,2)){
 $x=NewContext;$x.processCreateEntered=$true;$x.process=[Diagnostics.Process]::new();$x.processCreateReturned=$true
 for($i=0;$i -lt $n;$i++){$x.readers+=,(Raw (Join-Path $w ('raw-'+$n+'-'+$i+'.bin')))}
 $x.input.openEntered=$true;$x.input.sourceClosed=$false;$x.input.source=[IO.FileStream]::new((Join-Path $w ('input-'+$n+'.bin')),[IO.FileMode]::CreateNew,[IO.FileAccess]::ReadWrite,[IO.FileShare]::Read);$x.input.openReturned=$true
 Assert ((Get-CaptureStartDisposition $x) -ceq 'KNOWN_START_NEVER_ENTERED') 'EXACT_KNOWN_REJECTION_CLASS'
 Assert (Close-KnownPrestartResources $x) 'KNOWN_ORIGINALS_NOT_RETURNED'
 Assert (Close-KnownPrestartResources $x) 'SECOND_OBSERVATION_NOT_IDEMPOTENT'
 Assert ($x.processDisposed -and $x.processDisposeCalls -eq 1 -and -not $x.startEntered -and $x.stdinNeverCreated -and $x.input.sourceClosed) 'ORIGINAL_PROCESS_SOURCE_CLOSE_ONCE'
 foreach($r in $x.readers){Assert ($r.fileClosed -and $r.fileCloseCalls -eq 1 -and $r.pipeNeverCreated -and -not $r.pipeClosed -and -not $r.eof) 'NO_FAKE_PIPE_CLOSE_OR_EOF'}
 $results.Add(@{case='known-prestart-'+$n+'-raw';originalProcessDisposedOnce=$true;rawFilesClosedOnce=$n;pinnedSourceClosedOnce=$true;noPipeCreated=$true;noSDKStart=$true})
}
$z=NewContext;Assert (Close-KnownPrestartResources $z) 'NO_CONSTRUCTOR_ENTERED_CASE';Assert ($z.processNeverCreated -and -not $z.processDisposed -and $z.processDisposeCalls -eq 0) 'NO_FAKE_PROCESS_DISPOSE'
$models=@(
 @{case='Start-entered-no-established-return';edit={param($x) $x.startEntered=$true};expected='RETAIN_START_ENTERED_NOT_ESTABLISHED'},
 @{case='Process-create-unreturned';edit={param($x) $x.processCreateEntered=$true};expected='RETAIN_PROCESS_CREATE_UNKNOWN'},
 @{case='raw-create-unreturned';edit={param($x) $x.readers=@(@{fileOpenEntered=$true;fileOpenReturned=$false})};expected='RETAIN_RAW_OPEN_UNKNOWN'},
 @{case='raw-close-unreturned';edit={param($x) $x.readers=@(@{fileCloseEntered=$true;fileClosed=$false})};expected='RETAIN_RAW_CLOSE_UNKNOWN'},
 @{case='Process-dispose-unreturned';edit={param($x) $x.processDisposeEntered=$true};expected='RETAIN_PROCESS_DISPOSE_UNKNOWN'},
 @{case='lock-create-unreturned';edit={param($x) $x.lockOpenUnknown=$true};expected='RETAIN_LOCK_OPEN_UNKNOWN'},
 @{case='input-create-unreturned';edit={param($x) $x.input.openEntered=$true};expected='RETAIN_INPUT_CREATE_OR_HASH_UNKNOWN'},
 @{case='hash-dispose-unreturned';edit={param($x) $x.input.pinHashCreateEntered=$true;$x.input.pinHashCreateReturned=$true};expected='RETAIN_INPUT_CREATE_OR_HASH_UNKNOWN'},
 @{case='source-close-unreturned';edit={param($x) $x.input.sourceCloseEntered=$true;$x.input.sourceClosed=$false};expected='RETAIN_INPUT_IO_UNKNOWN'}
)
foreach($m in $models){$x=NewContext;& $m.edit $x;$state=Get-CaptureStartDisposition $x;Assert ($state -ceq $m.expected) ('MODEL_'+$m.case);Assert (-not (Close-KnownPrestartResources $x)) ('NO_IO_FOR_'+$m.case);$results.Add(@{case=$m.case;state=$state;pureStateOnly=$true;actualUnknownCreated=$false})}
# The third state has a real original, fixed local child and streams. The
# prestart helper must leave it entirely to the normal original stream owner.
$x=NewContext;$x.processCreateEntered=$true;$x.process=[Diagnostics.Process]::new();$x.processCreateReturned=$true
$x.readers=@((Raw (Join-Path $w 'started-stdout.bin')),(Raw (Join-Path $w 'started-stderr.bin')))
$info=[Diagnostics.ProcessStartInfo]::new();$info.FileName='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';$info.UseShellExecute=$false;$info.CreateNoWindow=$true;$info.RedirectStandardOutput=$true;$info.RedirectStandardError=$true
foreach($a in @('-I','-X','utf8','-B','-c','print("LOCAL_PRESTART_STATE_THREE")')){$info.ArgumentList.Add($a)}
$x.process.StartInfo=$info;$x.startEntered=$true
try{$v=$x.process.Start();$x.startReturned=$true;Assert $v 'LOCAL_CHILD_START_FALSE';$x.started=$true}catch{[IO.File]::WriteAllText($OutputFile,'{"status":"LOCAL_START_RETURN_UNPROVEN_STOP_NEW_DYNAMIC"}');while($true){Start-Sleep -Milliseconds 1000}}
Assert ((Get-CaptureStartDisposition $x) -ceq 'STARTED_ORIGINAL_STREAM_PATH') 'ACTUAL_STARTED_CLASS'
Assert (-not (Close-KnownPrestartResources $x)) 'PRESTART_HELPER_TOUCHED_STARTED_PROCESS'
Assert (-not $x.processDisposed -and @($x.readers|Where-Object fileClosed).Count -eq 0) 'NO_EARLY_CLOSE'
$stdout=$x.process.StandardOutput.ReadToEnd();$stderr=$x.process.StandardError.ReadToEnd();$x.process.WaitForExit();$code=$x.process.ExitCode
$x.process.StandardOutput.Close();$x.process.StandardError.Close();foreach($r in $x.readers){$r.file.Close();$r.fileClosed=$true};$x.process.Dispose()
Assert ($code -eq 0 -and $stdout.Trim() -ceq 'LOCAL_PRESTART_STATE_THREE' -and $stderr.Length -eq 0) 'ACTUAL_ORIGINAL_LOCAL_CHILD_RETURN'
$results.Add(@{case='actual-started-local-original';waitAndReadersActuallyReturned=$true;exitCode=$code;streamsAndFilesClosedOnce=$true;originalProcessDisposed=$true;prestartHelperDidNotCloseAnything=$true;sdk=0;nativeClaim=0})
[IO.File]::WriteAllText($OutputFile,(@{schema='GLOBAL_IDLE_REVISION02_PRESTART_LIFETIME_V1';allPassed=$true;results=$results.ToArray();actualUnknownCreated=$false;sdk=0;nativeClaim=0}|ConvertTo-Json -Depth 8))
