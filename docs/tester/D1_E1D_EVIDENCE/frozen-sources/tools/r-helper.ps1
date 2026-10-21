param([Parameter(Mandatory=$true)][string]$FixtureRoot)
$ErrorActionPreference = 'Stop'
$base = Split-Path $PSScriptRoot -Parent
Add-Type -Path (Join-Path $base 'artifacts/E1D.dll')
exit [VideoKit.E1.RHost]::Run($FixtureRoot)
