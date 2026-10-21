param([ValidateSet('Inspect','RealAdmission','SelfCheck','NegativeChecks','Recover')][string]$Mode='Inspect',[string]$Snapshot,[string]$Batch)
$ErrorActionPreference='Stop'
$base=Split-Path $PSScriptRoot -Parent
$python='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
switch ($Mode) {
    'Inspect' { & $python -B (Join-Path $base 'src/admission.py') --inspect }
    'RealAdmission' {
        if (-not $Batch) { throw 'Batch name required; admission remains configuration-only' }
        & $python -B (Join-Path $base 'src/admission.py') --request-real $Batch
        if ($LASTEXITCODE -eq 0) { throw 'REAL_EXECUTION_MUST_REMAIN_DISABLED' }
        throw 'REAL_ADMISSION_NOT_EXECUTED; nonzero admission result, no automatic retry'
    }
    'SelfCheck' { & $python -B (Join-Path $base 'tools/run-selfcheck.py') --run }
    'NegativeChecks' { & $python -B (Join-Path $base 'tools/check-targeted.py') --run }
    'Recover' { if (-not $Snapshot) { throw 'Snapshot name required' }; & $python -B (Join-Path $base 'src/controller.py') --recover-selfcheck $Snapshot }
}
if ($LASTEXITCODE -ne 0) { throw 'TOOL_REPORTED_FAILURE; no automatic retry' }
