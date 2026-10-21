$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
$dir=Join-Path $root 'pending-observation'
if(Test-Path -LiteralPath $dir){throw 'Observation already entered; no replay'}
[void](New-Item -ItemType Directory -Path $dir)
function Save($name,$value){[IO.File]::WriteAllText((Join-Path $dir $name),($value|ConvertTo-Json -Depth 12),[Text.UTF8Encoding]::new($false))}
Save 'authority.json' @{kind='E13C_PENDING_READONLY_OBSERVATION';sourceThread='01a107c3-2bf9-7fa0-94a0-234258ca6774';scope='aeefe32f-816d-4c0b-aca7-16f76dbd45ff';originalSession=42537;originalJava=38056;originalHost=39560;originalStartUtc='2026-10-18T08:48:05.6692683Z';atUtc=[DateTime]::UtcNow.ToString('o');maxAdb=3;maxHost=1;maxEachBytes=65536;maxEachSeconds=10;maxTotalOperations=55;maxTotalText=2097152;noKill=$true;noRestart=$true;noNewTests=$true;originalSessionRead='One empty read: running, zero incremental bytes, no EOF';priorHostAttempt='Sandbox CIM inaccessible, no process identity obtained'}
$all=Get-CimInstance Win32_Process
$selected=@($all|Where-Object {$_.ProcessId -in @(38056,39560) -or $_.ParentProcessId -in @(38056,39560)}|Select-Object ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine)
Save 'host-identity.json' @{atUtc=[DateTime]::UtcNow.ToString('o');processes=$selected;readerState='Not externally inspected; original live session retained; no debugger/handle manipulation'}
$commands=@(
 @{id='01-processes';script='echo E13C_PS_BEGIN; ps -A -o USER,PID,PPID,STIME,NAME,ARGS; r=$?; echo E13C_PS_EXIT=$r; echo E13C_PS_END; exit $r'},
 @{id='02-activity';script='echo E13C_PROCESSES_BEGIN; dumpsys activity processes; a=$?; echo E13C_PROCESSES_EXIT=$a; echo E13C_PROCESSES_END; echo E13C_SERVICES_BEGIN; dumpsys activity services com.videokit; b=$?; echo E13C_SERVICES_EXIT=$b; echo E13C_SERVICES_END; test "$a" = 0 && test "$b" = 0'},
 @{id='03-log-window';script='echo E13C_LOG_BEGIN; logcat -d -v threadtime -T "10-18 16:48:05.000" -s E13 E13Binding E13BindingOwner ActivityManager AndroidRuntime; r=$?; echo E13C_LOG_EXIT=$r; echo E13C_LOG_END; exit $r'}
)
foreach($c in $commands){
 $argv=@('-s','HA1Q6WXR','shell','sh','-c',("'"+$c.script.Replace("'","'\''")+"'"))
 Save ($c.id+'-intent.json') @{atUtc=[DateTime]::UtcNow.ToString('o');exe='D:/Android/SDK/platform-tools/adb.exe';argv=$argv;cap=65536;seconds=10}
 $p=[Diagnostics.Process]::new();$i=[Diagnostics.ProcessStartInfo]::new();$i.FileName='D:/Android/SDK/platform-tools/adb.exe';$i.UseShellExecute=$false;$i.CreateNoWindow=$true;$i.RedirectStandardInput=$true;$i.RedirectStandardOutput=$true;$i.RedirectStandardError=$true
 foreach($a in $argv){$i.ArgumentList.Add($a)};$p.StartInfo=$i
 [void]$p.Start();$p.StandardInput.Close();$out=[IO.MemoryStream]::new();$err=[IO.MemoryStream]::new();$ot=$p.StandardOutput.BaseStream.CopyToAsync($out);$et=$p.StandardError.BaseStream.CopyToAsync($err);$timer=[Diagnostics.Stopwatch]::StartNew();$pending=$false
 while(-not($p.HasExited -and $ot.IsCompleted -and $et.IsCompleted)){
  if($timer.Elapsed.TotalSeconds -ge 10 -and -not $pending){$pending=$true;Save ($c.id+'-pending.json') @{pid=$p.Id;host=$PID;state='PENDING_RETAINED_NO_NEXT_DIAGNOSTIC';atUtc=[DateTime]::UtcNow.ToString('o')};Write-Output 'Diagnostic pending; original retained, no next diagnostic'}
  Start-Sleep -Milliseconds 100
 }
 $p.WaitForExit();[void]$ot.GetAwaiter().GetResult();[void]$et.GetAwaiter().GetResult();$ob=$out.ToArray();$eb=$err.ToArray();$length=$ob.Length+$eb.Length;$overflow=$length -gt 65536
 # Retain complete raw only within the authorized cap; overflow is explicit and never an IDLE proof.
 $keepOut=[Math]::Min(65536,$ob.Length);$keepErr=[Math]::Min(65536-$keepOut,$eb.Length)
 [IO.File]::WriteAllBytes((Join-Path $dir ($c.id+'-stdout.txt')),[byte[]]$ob[0..($keepOut-1)])
 if($keepOut -eq 0){[IO.File]::WriteAllBytes((Join-Path $dir ($c.id+'-stdout.txt')),[byte[]]@())}
 [IO.File]::WriteAllBytes((Join-Path $dir ($c.id+'-stderr.txt')),$(if($keepErr){[byte[]]$eb[0..($keepErr-1)]}else{[byte[]]@()}))
 $receipt=@{atUtc=[DateTime]::UtcNow.ToString('o');pid=$p.Id;host=$PID;exit=$p.ExitCode;seconds=$timer.Elapsed.TotalSeconds;stdoutBytes=$ob.Length;stderrBytes=$eb.Length;retainedBytes=$keepOut+$keepErr;overflow=$overflow;complete=(-not $overflow);pending=$pending;originalWaitReturned=$true;readersReturned=$true}
 $p.StandardOutput.Close();$p.StandardError.Close();$p.Dispose();Save ($c.id+'-receipt.json') $receipt
 $receipt|ConvertTo-Json -Compress
 if($pending -or $overflow -or $receipt.exit -ne 0){break}
}
