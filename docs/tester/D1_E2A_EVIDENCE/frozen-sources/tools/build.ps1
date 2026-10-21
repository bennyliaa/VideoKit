param([switch]$Compile,[switch]$Repair)
$ErrorActionPreference = 'Stop'
$base = Split-Path $PSScriptRoot -Parent
if (-not $Compile) { Write-Output 'Explicit -Compile required; no execution.'; return }
if (Test-Path -LiteralPath (Join-Path $base 'evidence/freeze-summary.json')) { throw 'FROZEN_PACKAGE_READ_ONLY_NEW_AUTHORIZED_BATCH_REQUIRED' }
$javac = 'D:\Android\Android Studio\jbr\bin\javac.exe'
if (-not (Test-Path -LiteralPath $javac)) { throw 'LOCAL_JAVAC_MISSING' }
$output = Join-Path $base 'artifacts/E2A.dll'
if (Test-Path -LiteralPath $output) {
    if (-not $Repair) { throw 'Explicit -Repair required' }
    $number = 1
    do { $archive = Join-Path $base ('artifacts/E2A-before-repair-' + $number + '.dll'); $number++ } while (Test-Path -LiteralPath $archive)
    Move-Item -LiteralPath $output -Destination $archive
}
$refs = @(Get-ChildItem -LiteralPath (Join-Path $PSHOME 'ref') -Filter '*.dll' | ForEach-Object FullName)
Add-Type -Path @(Get-ChildItem -LiteralPath (Join-Path $base 'src') -Filter '*.cs' | ForEach-Object FullName) -ReferencedAssemblies $refs -OutputAssembly $output
& $javac --enable-preview --release 21 -encoding UTF-8 -d (Join-Path $base 'artifacts/java') @(Get-ChildItem -LiteralPath (Join-Path $base 'src') -Filter '*.java' | ForEach-Object FullName)
if ($LASTEXITCODE -ne 0) { throw 'JAVA_COMPILE_FAILED' }
Write-Output ('COMPILED_ONLY PowerShell=' + $PSVersionTable.PSVersion + ' Runtime=' + [System.Runtime.InteropServices.RuntimeInformation]::FrameworkDescription)
& $javac -version
