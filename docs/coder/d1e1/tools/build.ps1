param([switch]$Compile,[switch]$Repair)
$ErrorActionPreference = 'Stop'
$base = Split-Path $PSScriptRoot -Parent
if (-not $Compile) { Write-Output 'Explicit -Compile required. Builds E1 tools only; no PF or media execution.'; return }
$javac = 'D:\Android\Android Studio\jbr\bin\javac.exe'
if (-not (Test-Path -LiteralPath $javac)) { throw 'LOCAL_JAVAC_MISSING; no download allowed' }
$output = Join-Path $base 'artifacts/E1.dll'
if (Test-Path -LiteralPath $output) {
    if (-not $Repair) { throw 'BUILD_ARTIFACT_EXISTS: explicit -Repair required' }
    $repairNumber = 1
    do { $archive = Join-Path $base ('artifacts/E1-before-repair-' + $repairNumber + '.dll'); $repairNumber++ } while (Test-Path -LiteralPath $archive)
    Move-Item -LiteralPath $output -Destination $archive
}
$refs = @(Get-ChildItem -LiteralPath (Join-Path $PSHOME 'ref') -Filter '*.dll' | ForEach-Object FullName)
Add-Type -Path @(Get-ChildItem -LiteralPath (Join-Path $base 'src') -Filter '*.cs' | ForEach-Object FullName) -ReferencedAssemblies $refs -OutputAssembly $output
& $javac -encoding UTF-8 -d (Join-Path $base 'artifacts/java') (Join-Path $base 'src/JavaHelper.java')
if ($LASTEXITCODE -ne 0) { throw 'JAVA_COMPILE_FAILED' }
Write-Output ('COMPILED_ONLY CSharp/Roslyn PowerShell=' + $PSVersionTable.PSVersion + ' Runtime=' + [System.Runtime.InteropServices.RuntimeInformation]::FrameworkDescription)
& $javac -version
