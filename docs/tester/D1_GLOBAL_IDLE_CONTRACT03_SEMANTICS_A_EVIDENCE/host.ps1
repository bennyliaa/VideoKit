param([string]$InputFile,[string]$OutputFile)
$ErrorActionPreference='Stop'
$u=[Text.UTF8Encoding]::new($false,$true)
. 'D:\CodexProjects\VideoKit\docs\coder\d1android02-global-idle-contract03-fix\tools\admission_checks.ps1'
$index=[IO.File]::ReadAllText($InputFile,$u)|ConvertFrom-Json -DateKind String
$out=@(foreach($p in $index){
 if(([IO.FileInfo]$p).Length -gt 1048576){throw 'CASE_INPUT_BOUND'}
 $r=[IO.File]::ReadAllText($p,$u)|ConvertFrom-Json -DateKind String
 $d=Get-GlobalIdleDecision $r.text $r.qualification $r.context
 $ok=($null -eq $r.expectedReason -or $d.reason -ceq $r.expectedReason)
 [ordered]@{id=$r.id;origin=$r.origin;logicalIndex=$r.logicalIndex;expected=$r.expected;expectedReason=$r.expectedReason;status=$d.status;reason=$d.reason;qualified=$d.qualified;stage=$d.stage;processCount=$d.processes.Count;processes=$d.processes;pass=($d.status -ceq $r.expected -and $d.qualified -eq ($r.expected -ceq 'PASS') -and $ok)}
})
[IO.File]::WriteAllText($OutputFile,($out|ConvertTo-Json -Depth 16),$u)
if(@($out|Where-Object {-not $_.pass}).Count){exit 2}
