param([Parameter(Mandatory=$true)][string]$FixtureRoot)
$ErrorActionPreference = 'Stop'
$base = [System.IO.Path]::GetFullPath([System.IO.Path]::Combine($PSScriptRoot, '..'))
if ([System.IO.File]::Exists([System.IO.Path]::Combine($base, 'evidence', 'freeze-summary.json'))) { throw 'FROZEN_PACKAGE_READ_ONLY_NEW_AUTHORIZED_BATCH_REQUIRED' }
$assemblyPath = [System.IO.Path]::GetFullPath([System.IO.Path]::Combine($base, 'artifacts', 'E2C.dll'))
[void][System.Reflection.Assembly]::LoadFrom($assemblyPath)
exit [VideoKit.E1.RHost]::Run($FixtureRoot)
