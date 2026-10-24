param([string]$InputFile,[string]$OutputFile)
$ErrorActionPreference='Stop'
$b=Split-Path $PSScriptRoot
. (Join-Path $b 'tools/admission_checks.ps1')
$rows=[IO.File]::ReadAllText($InputFile)|ConvertFrom-Json -DateKind String
$out=@(foreach($r in $rows){
 $d=Get-GlobalIdleDecision $r.text $r.qualification $r.context
 [ordered]@{id=$r.id;expected=$r.expected;status=$d.status;reason=$d.reason;qualified=$d.qualified;processCount=$d.processes.Count;processes=$d.processes;pass=($d.status -ceq $r.expected -and $d.qualified -eq ($r.expected -ceq 'PASS') -and ($null -eq $r.PSObject.Properties['expectedReason'] -or $null -eq $r.expectedReason -or $d.reason -ceq $r.expectedReason))}
})
[IO.File]::WriteAllText($OutputFile,($out|ConvertTo-Json -Depth 16))
if(@($out|Where-Object {-not $_.pass}).Count){exit 2}
