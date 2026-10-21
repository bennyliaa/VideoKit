param([ValidateSet('Inspect','SelfCheck','NegativeChecks','Recover')][string]$Mode='Inspect',[string]$Snapshot)
$ErrorActionPreference='Stop'
$base=Split-Path $PSScriptRoot -Parent
$python='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
switch ($Mode) {
    'Inspect' { & $python -B (Join-Path $base 'src/controller.py') }
    'SelfCheck' { & $python -B (Join-Path $base 'tools/run-selfcheck.py') --run }
    'NegativeChecks' { & $python -B (Join-Path $base 'tools/check-targeted.py') --run }
    'Recover' { if (-not $Snapshot) { throw 'Snapshot name required' }; & $python -B (Join-Path $base 'src/controller.py') --recover-selfcheck $Snapshot }
}
if ($LASTEXITCODE -ne 0) { throw 'TOOL_REPORTED_FAILURE; no automatic retry' }
