$ErrorActionPreference='Stop'
$r=$PSScriptRoot
$b=[IO.Path]::GetFullPath((Join-Path $r '../../coder/d1android02-global-idle-contract03-fix'))
$fullPath=Join-Path $b 'reference/freeze-manifest.json'
$full=Get-Content -LiteralPath $fullPath -Raw|ConvertFrom-Json
$bad=@();[long]$readBytes=0
foreach($x in $full.files){$p=Join-Path $b $x.path;$size=(Get-Item -LiteralPath $p).Length;$h=(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant();$readBytes+=$size;if($size -ne $x.bytes -or $h -cne $x.sha256){$bad+=$x.path}}
if($full.files.Count -ne 98 -or $bad.Count){throw 'FROZEN_98_MISMATCH'}
$order=Get-Content -LiteralPath (Join-Path $r 'order.json') -Raw|ConvertFrom-Json
foreach($x in $order.sources){$p=$x.path;$h=(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant();$readBytes+=(Get-Item -LiteralPath $p).Length;if($h -cne $x.sha256){throw "OWN_FROZEN_INPUT_OR_SOURCE_CHANGED: $p"}}
$receipt=Get-Content -LiteralPath (Join-Path $b '../D1_GLOBAL_IDLE_CONTRACT03_FIX_BLOCKED_FREEZE_RECEIPT_V1.0.json') -Raw|ConvertFrom-Json
if((Get-FileHash -LiteralPath $receipt.archivePath -Algorithm SHA256).Hash.ToLowerInvariant() -cne $receipt.archiveSha256){throw 'ZIP_FILE_SHA'}
$readBytes+=$receipt.archiveBytes
$zip=[IO.Compression.ZipFile]::OpenRead($receipt.archivePath);$closed=$false;$count=0;$uncompressed=0
try{
 $names=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
 foreach($x in $zip.Entries){if(-not $names.Add($x.FullName)){throw 'ZIP_DUPLICATE'};$count++}
 if($count -ne 99){throw 'ZIP_99_COUNT'}
 $rows=@($full.files)+[pscustomobject]@{path='reference/freeze-manifest.json';bytes=(Get-Item -LiteralPath $fullPath).Length;sha256=(Get-FileHash -LiteralPath $fullPath -Algorithm SHA256).Hash.ToLowerInvariant()}
 foreach($x in $rows){$item=$zip.GetEntry($x.path);if($null -eq $item -or $item.Length -ne $x.bytes){throw "ZIP_EXACT_PATH_OR_SIZE: $($x.path)"};$s=$item.Open();try{$h=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($s)).ToLowerInvariant()}finally{$s.Dispose()};if($h -cne $x.sha256){throw 'ZIP_MEMBER_HASH'};$uncompressed+=$item.Length}
}finally{$zip.Dispose();$closed=$true}
$result=Get-Content -LiteralPath (Join-Path $r 'semantic-results.json') -Raw|ConvertFrom-Json
$history=@($result|Where-Object {$_.id -in @('H01','H02')});if($history.Count -ne 4 -or @($history|Where-Object {$_.processCount -ne 68 -or $_.qualified}).Count){throw 'ARCHIVED_68_QUALIFICATION_BOUNDARY'}
$matrix=@($result|Where-Object {$_.origin -ceq 'independent175'}|Select-Object -First 45)
if($matrix.Count -ne 45 -or @($matrix|Where-Object {-not $_.pass}).Count){throw 'ORIGINAL_45_MATRIX'}
$selfReport=Join-Path $r '../D1_DRIVER_CAPTURE_SELF01_REPORT_V1.0.md'
if((Get-FileHash -LiteralPath $selfReport -Algorithm SHA256).Hash.ToLowerInvariant() -cne '2fd415f0bbee624abae236934514a4f9a3310e3d04ac7937d10b65cc9f3fb613'){throw 'SELF_REPORT_SHA'}
$data=[ordered]@{schema='SEMANTICS_A_FROZEN_POST_AUDIT_V1';frozenFiles=98;bad=$bad;zipUniqueMembers=99;zipSha256=$receipt.archiveSha256;zipOriginalStreamDisposed=$closed;zipMemberBytes=$uncompressed;postExplicitReadBytes=$readBytes+$uncompressed;original45Passed=45;historicalSamples=4;historicalRecordsEach=68;historicalQualified=$false;currentProductionModuleSha256=(Get-FileHash -LiteralPath (Join-Path $b 'tools/admission_checks.ps1') -Algorithm SHA256).Hash.ToLowerInvariant();oldRuntimeQueries=0;originalCandidateChanges=0;newUnknown=$false;physicalIO='UNPROVEN'}
$out=Join-Path $r 'post-audit.json';if(Test-Path -LiteralPath $out){throw 'POST_AUDIT_ALREADY_EXISTS'}
[IO.File]::WriteAllText($out,($data|ConvertTo-Json -Depth 8),[Text.UTF8Encoding]::new($false));$data|ConvertTo-Json -Depth 5
