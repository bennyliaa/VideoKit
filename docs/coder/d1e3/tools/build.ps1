param([switch]$Compile)
$ErrorActionPreference = 'Stop'
$base = [System.IO.Path]::GetFullPath([System.IO.Path]::Combine($PSScriptRoot, '..'))
if (-not $Compile) { Write-Output 'INSPECT_ONLY: explicit -Compile required; no execution.'; return }
$seal = [System.IO.Path]::Combine($base, 'evidence', 'e3-freeze.json')
if ([System.IO.File]::Exists($seal)) { throw 'FROZEN_PACKAGE_READ_ONLY_NEW_AUTHORIZED_BATCH_REQUIRED' }
$reservation = [System.IO.Path]::Combine($base, 'evidence', 'build-reservation.json')
$receiptPath = [System.IO.Path]::Combine($base, 'evidence', 'build.json')
$output = [System.IO.Path]::Combine($base, 'artifacts', 'E3.dll')
$javaOutput = [System.IO.Path]::Combine($base, 'artifacts', 'java-e3')
if ([System.IO.File]::Exists($reservation) -or [System.IO.File]::Exists($receiptPath) -or [System.IO.File]::Exists($output) -or [System.IO.Directory]::Exists($javaOutput)) { throw 'COMPILE_ATTEMPT_ALREADY_RESERVED_NO_OVERWRITE_OR_REPAIR' }
$javac = 'D:\Android\Android Studio\jbr\bin\javac.exe'
if (-not [System.IO.File]::Exists($javac)) { throw 'LOCAL_JAVAC_MISSING' }
function Write-NewJson([string]$Path, $Value) {
    $bytes = [System.Text.UTF8Encoding]::new($false).GetBytes(($Value | ConvertTo-Json -Depth 10) + "`n")
    if ($bytes.Length -gt 32768) { throw 'BUILD_RECEIPT_LIMIT' }
    $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::Read)
    try { $stream.Write($bytes, 0, $bytes.Length); $stream.Flush($true) } finally { $stream.Dispose() }
}
function File-Record([System.IO.FileInfo]$File) {
    $stream = [System.IO.File]::OpenRead($File.FullName)
    try { $hash = [System.Convert]::ToHexString([System.Security.Cryptography.SHA256]::HashData($stream)).ToLowerInvariant() } finally { $stream.Dispose() }
    return @{path=$File.FullName.Substring($base.Length + 1).Replace('\','/'); bytes=$File.Length; sha256=$hash}
}
Write-NewJson $reservation @{schema=1; scope='E3_SINGLE_COMPILE_RESERVATION'; compileInvocations=1; refundAllowed=$false; repairAllowed=$false; createdBeforeCompilers=$true}
$receipt = @{schema=1; scope='E3_COMPILE_ONLY'; status='FAIL'; compileInvocations=1; repairCompilations=0; csharpCompilations=0; javaCompilations=0; helpersStarted=0; newG=0; osMetricSamples=0; realMediaBytesRead=0; actualFullRuns=0; compiledArtifacts=@(); sourceFiles=@(); error=$null}
try {
    $csharp = @(Get-ChildItem -LiteralPath ([System.IO.Path]::Combine($base, 'src')) -Filter '*.cs' | Sort-Object Name)
    $java = @(Get-ChildItem -LiteralPath ([System.IO.Path]::Combine($base, 'src')) -Filter '*.java' | Sort-Object Name)
    $receipt.sourceFiles = @(@($csharp) + @($java) | ForEach-Object { File-Record $_ })
    $refs = @(Get-ChildItem -LiteralPath ([System.IO.Path]::Combine($PSHOME, 'ref')) -Filter '*.dll' | ForEach-Object FullName)
    $receipt.csharpCompilations = 1
    Add-Type -Path @($csharp | ForEach-Object FullName) -ReferencedAssemblies $refs -OutputAssembly $output
    [void][System.IO.Directory]::CreateDirectory($javaOutput)
    $receipt.javaCompilations = 1
    & $javac --enable-preview --release 21 -encoding UTF-8 -d $javaOutput @($java | ForEach-Object FullName)
    if ($LASTEXITCODE -ne 0) { throw 'JAVA_COMPILE_FAILED' }
    $receipt.status = 'PASS'
} catch {
    $message = [string]$_.Exception.Message
    $receipt.error = $message.Substring(0, [Math]::Min($message.Length, 512))
    throw
} finally {
    $compiled = @()
    if ([System.IO.File]::Exists($output)) { $compiled += Get-Item -LiteralPath $output }
    if ([System.IO.Directory]::Exists($javaOutput)) { $compiled += Get-ChildItem -LiteralPath $javaOutput -Recurse -File }
    $receipt.compiledArtifacts = @($compiled | Sort-Object FullName | ForEach-Object { File-Record $_ })
    $receipt.sourceBytesHashed = [long](($receipt.sourceFiles | Measure-Object -Property bytes -Sum).Sum)
    $receipt.artifactBytesHashed = [long](($receipt.compiledArtifacts | Measure-Object -Property bytes -Sum).Sum)
    Write-NewJson $receiptPath $receipt
}
Write-Output 'COMPILED_ONLY: E3.dll and java-e3; baseline artifacts preserved; no helper or driver started.'
