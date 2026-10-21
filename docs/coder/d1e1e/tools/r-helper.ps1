param([Parameter(Mandatory=$true)][string]$FixtureRoot)
$ErrorActionPreference = 'Stop'
$base = Split-Path $PSScriptRoot -Parent
if (Test-Path -LiteralPath (Join-Path $base 'evidence/freeze-summary.json')) { throw 'FROZEN_PACKAGE_READ_ONLY_NEW_AUTHORIZED_BATCH_REQUIRED' }
Add-Type -Path (Join-Path $base 'artifacts/E1E.dll')
exit [VideoKit.E1.RHost]::Run($FixtureRoot)
