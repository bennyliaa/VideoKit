param([ValidateSet('Inspect','SelfCheck','Helper','Experiment')][string]$Mode='Inspect',[string]$FixtureRoot)
$ErrorActionPreference = 'Stop'
$base = Split-Path $PSScriptRoot -Parent
if ($Mode -eq 'Experiment') { throw 'E1_MEDIA_PF_FULL_RUN_NOT_AUTHORIZED; scenario executor not wired' }
Add-Type -Path (Join-Path $base 'artifacts/E1.dll')
if ($Mode -eq 'Inspect') { [VideoKit.E1.Plan]::Inspect($base); return }
if ($Mode -eq 'Helper') { exit [VideoKit.E1.NetHelper]::Run($FixtureRoot) }
$java = 'D:\Android\Android Studio\jbr\bin\java.exe'
$pwsh = Join-Path $PSHOME 'pwsh.exe'
$report = [VideoKit.E1.SelfCheck]::Run($base,$java,$pwsh)
$report | Set-Content -LiteralPath (Join-Path $base 'evidence/selfcheck.json') -Encoding utf8NoBOM
$report
