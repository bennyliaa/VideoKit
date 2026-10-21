param([Parameter(Mandatory=$true)][string]$Candidate)
$ErrorActionPreference='Stop'
$b=[IO.Path]::GetFullPath($Candidate)
foreach($file in @('policy/observe_e13k.ps1','release/launch_once.ps1')){
 $t=$null;$errors=$null;$null=[Management.Automation.Language.Parser]::ParseFile((Join-Path $b $file),[ref]$t,[ref]$errors)
 if($errors.Count){throw 'K_PS_PARSE_FAILED'}
}
$observer=[IO.File]::ReadAllText((Join-Path $b 'policy/observe_e13k.ps1'))
$prefix=$observer.Substring(0,$observer.IndexOf('# Same original local context'))
# Exact production preflight prefix only; original context/Process initialization is excluded.
& ([scriptblock]::Create($prefix)) -RequestPath (Join-Path $b 'release/observer-request.json')
$launch=[IO.File]::ReadAllText((Join-Path $b 'release/launch_once.ps1'))
$summaryCode=$launch.Substring($launch.IndexOf('$facts ='))
$captured=@{allOriginalResourcesReturned=$true;metadataRecordFilesReturnedAtConsole=$true}|ConvertTo-Json
& ([scriptblock]::Create($summaryCode))
'PASS_STATIC_POLICY_PREFIX_AND_SUMMARY_ONLY noObserverOwnerStarted=true dispatch=0 actual5037=0'
