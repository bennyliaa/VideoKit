[CmdletBinding()]
param([switch]$Run,[string]$ExecutionId='', [string]$ExpectedFreezeSha256='')
$ErrorActionPreference='Stop'
$candidate=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$project=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..\..\..'))
if (-not $Run) { [ordered]@{mode='INSPECT';scope='OWNED_LOCAL_FILE_SYMLINK_ONLY';deviceCalls=0;requires='Existing OS symbolic-link privilege and separately dispatched one execution id; no system setting changes'} | ConvertTo-Json;return }
if ($ExpectedFreezeSha256 -notmatch '^[a-f0-9]{64}$') { throw 'EXACT_REVIEWED_FREEZE_REQUIRED' }
$execution=[Guid]::ParseExact($ExecutionId,'D').ToString('D')
$seal=Join-Path $candidate 'evidence\e5b-freeze.json'
if ((Get-FileHash -LiteralPath $seal -Algorithm SHA256).Hash.ToLowerInvariant() -ne $ExpectedFreezeSha256) { throw 'REVIEWED_FREEZE_MISMATCH' }
$checks=Get-Content -LiteralPath (Join-Path $candidate 'evidence\local-check-results.json') -Raw | ConvertFrom-Json
foreach ($row in $checks.inputs) {
    $path=Join-Path $project $row.path
    if ((Get-Item -LiteralPath $path).Length -ne $row.bytes -or (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $row.sha256) { throw 'FROZEN_JAVA_INPUT_MISMATCH' }
}
$parent=Join-Path $project 'docs\coder\E5B_SYMBOLICLINK_ONCE'
[IO.Directory]::CreateDirectory($parent) | Out-Null
$runRoot=[IO.Path]::GetFullPath((Join-Path $parent $execution))
if (-not $runRoot.StartsWith([IO.Path]::GetFullPath($parent)+'\',[StringComparison]::OrdinalIgnoreCase) -or (Test-Path -LiteralPath $runRoot)) { throw 'ONE_EXECUTION_ID_ALREADY_CONSUMED_OR_INVALID' }
New-Item -ItemType Directory -Path $runRoot | Out-Null
$classes=Join-Path $runRoot 'classes';New-Item -ItemType Directory -Path $classes | Out-Null
$jdk='D:\Android\Android Studio\jbr\bin'
$java=Join-Path $jdk 'java.exe';$javac=Join-Path $jdk 'javac.exe'
$source=@($checks.inputs | ForEach-Object { Join-Path $project $_.path })
& $javac '--release' '11' '-encoding' 'UTF-8' '-d' $classes @source 2>&1 | Out-File -LiteralPath (Join-Path $runRoot 'javac.log') -Encoding utf8
if ($LASTEXITCODE -ne 0) { throw 'OWNED_JAVAC_FAILED' }
$flags=@('-Dsun.nio.fs.ensureAccurateMetadata=true','--add-opens=java.base/sun.nio.fs=ALL-UNNAMED','--add-opens=java.base/sun.nio.ch=ALL-UNNAMED','--add-opens=java.base/java.io=ALL-UNNAMED','-cp',$classes,'com.videokit.spike.e4.E5BGuardSelfCheck')
$results=@()
foreach ($role in @('owner','lease')) {
    $case=[IO.Path]::GetFullPath((Join-Path $runRoot $role));New-Item -ItemType Directory -Path $case | Out-Null
    & $java @flags 'produce' $case 2>&1 | Out-File -LiteralPath (Join-Path $case 'producer.log') -Encoding utf8
    if ($LASTEXITCODE -ne 0) { throw 'OWNED_PRODUCER_FAILED' }
    $node=[IO.Path]::GetFullPath((Join-Path $case ('files\e4a_outputs\86cafdb3-0fc4-447d-920b-b19c884bf494.'+$role)))
    $target=$node+'.original-symlink-target'
    foreach ($p in @($node,$target)) { if (-not $p.StartsWith($case+'\',[StringComparison]::OrdinalIgnoreCase)) { throw 'OWNED_CASE_PATH_BOUNDARY' } }
    $original=Get-Item -LiteralPath $node
    if ($original.PSIsContainer -or ($original.Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'EXPECTED_OWNED_REGULAR_FIXTURE' }
    # Preserve original file identity; an accidental follow would see the same original dev/inode and bytes.
    Move-Item -LiteralPath $node -Destination $target -ErrorAction Stop
    New-Item -ItemType SymbolicLink -Path $node -Target $target -ErrorAction Stop | Out-Null
    if ((Get-Item -LiteralPath $node).LinkType -ne 'SymbolicLink') { throw 'TRUE_FILE_SYMLINK_REQUIRED_NOT_JUNCTION' }
    & $java @flags ('observe-'+$role+'-symlink') $case 2>&1 | Out-File -LiteralPath (Join-Path $case 'observation.log') -Encoding utf8
    if ($LASTEXITCODE -ne 0) { throw 'PRODUCTION_SYMLINK_REFUSAL_FAILED' }
    $results += [ordered]@{role=$role;linkType='SymbolicLink';exitCode=0;log=(Join-Path $case 'observation.log')}
}
$value=[ordered]@{schema=1;status='PASS';scope='OWNED_LOCAL_TRUE_FILE_SYMLINK_PRODUCTION_OBSERVATION';executionId=$execution;freezeSha256=$ExpectedFreezeSha256;cases=$results;deviceCalls=0;realMediaReads=0;systemSettingChanges=0;oldOutcomeChanges=0}
$bytes=[Text.UTF8Encoding]::new($false).GetBytes(($value | ConvertTo-Json -Depth 10)+"`n")
$receipt=[IO.File]::Open((Join-Path $runRoot 'receipt.json'),[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
try { $receipt.Write($bytes,0,$bytes.Length);$receipt.Flush($true) } finally { $receipt.Dispose() }
$value | ConvertTo-Json -Depth 10
