$ErrorActionPreference='Stop'
$r=$PSScriptRoot;$t=Split-Path $r
$report=Join-Path $t 'D1_GLOBAL_IDLE_CONTRACT03_SEMANTICS_A_REPORT_V1.0.md'
$manifest=Join-Path $t 'D1_GLOBAL_IDLE_CONTRACT03_SEMANTICS_A_MANIFEST_V1.0.json'
$receiptPath=Join-Path $t 'D1_GLOBAL_IDLE_CONTRACT03_SEMANTICS_A_FREEZE_RECEIPT_V1.0.json'
if((Test-Path -LiteralPath $manifest) -or (Test-Path -LiteralPath $receiptPath)){throw 'ALREADY_FROZEN'}
$o=Get-Content -LiteralPath (Join-Path $r 'order.json') -Raw|ConvertFrom-Json
$w=Get-Content -LiteralPath (Join-Path $r 'worker-final.json') -Raw|ConvertFrom-Json
$outer=Get-Content -LiteralPath (Join-Path $r 'outer-final.json') -Raw|ConvertFrom-Json
$post=Get-Content -LiteralPath (Join-Path $r 'post-audit.json') -Raw|ConvertFrom-Json
if(-not $w.allPassed -or $w.newUnknown -or $outer.newUnknown -or $post.bad.Count){throw 'RESULT_BOUNDARY'}
$b=$o.candidate
$pinFiles=@('reference/runner-source-seal.json','reference/exact-seven-role-plan.json','tools/fact_collector.py','reference/fact-plan.json')
[long]$pinSum=0;foreach($p in $pinFiles){$pinSum+=(Get-Item -LiteralPath (Join-Path $b $p)).Length}
[long]$inputBytes=0;foreach($x in $o.sources){if($x.path -like '*\inputs\case-*'){$inputBytes+=$x.bytes}}
[long]$known=12946008+$w.sourceReadBytes+$outer.sourceReadBytes+$post.postExplicitReadBytes
[long]$generatorBound=(2*(98+73)+1)*$pinSum+2*388784+65536
[long]$hostBound=$inputBytes+(Get-Item -LiteralPath (Join-Path $r 'host.ps1')).Length+(Get-Item -LiteralPath (Join-Path $r 'input-index.json')).Length+(Get-Item -LiteralPath (Join-Path $b 'tools/admission_checks.ps1')).Length
[long]$savedNow=0;Get-ChildItem -LiteralPath $r -Recurse -File|ForEach-Object{$savedNow+=$_.Length};$savedNow+=(Get-Item -LiteralPath $report).Length
[long]$freezeBound=4*($savedNow+1048576)+2097152
[long]$bound=$known+$generatorBound+$hostBound+$freezeBound
if($bound -gt 67108864){throw "CONSERVATIVE_READ_BOUND: $bound"}
$ledger=[ordered]@{schema='SEMANTICS_A_BOUNDED_LOGICAL_IO_LEDGER_V1';knownControlledReadBytes=$known;preparationKnownBytes=12946008;workerKnownBytes=$w.sourceReadBytes;outerKnownBytes=$outer.sourceReadBytes;postKnownBytes=$post.postExplicitReadBytes;generatorAdditionalConservativeBound=$generatorBound;generatorBasis='At most two qualification evaluations per 98+73 row; four pin files each; independent builder pin set; two archived sample reads; source-helper reserve. This is a static bound, not an observed call counter.';PSInputAndModuleReadBound=$hostBound;PSCaseInputBytes=$inputBytes;remainingFreezeReadbackAndManualFileReadBound=$freezeBound;completeControlledLogicalReadBound=$bound;budgetReadBytes=67108864;physicalIO='UNPROVEN';internalInterpreterIO='NOT_INFERRED_FROM_FILESIZE_LOGICAL_LEDGER';controlledDynamicProcesses=3;PSFunctionHosts=1;PopenEvents=2;realSDK=0;realNativeRoute=0;oldRuntimeQueries=0;newUnknown=$false}
$ledgerPath=Join-Path $r 'ledger-summary.json';[IO.File]::WriteAllText($ledgerPath,($ledger|ConvertTo-Json -Depth 6),[Text.UTF8Encoding]::new($false))
$rows=@();[long]$total=0
foreach($p in @(Get-ChildItem -LiteralPath $r -Recurse -File|Sort-Object FullName)){
 if(($p.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){throw 'OWN_REPARSE'}
 $hash=(Get-FileHash -LiteralPath $p.FullName -Algorithm SHA256).Hash.ToLowerInvariant();$rows+=[ordered]@{root='evidence';path=[IO.Path]::GetRelativePath($r,$p.FullName).Replace('\','/');absolutePath=$p.FullName;bytes=$p.Length;sha256=$hash};$total+=$p.Length
}
$reportHash=(Get-FileHash -LiteralPath $report -Algorithm SHA256).Hash.ToLowerInvariant();$n=(Get-Item -LiteralPath $report).Length;$total+=$n
$rows+=[ordered]@{root='report';path=[IO.Path]::GetFileName($report);absolutePath=$report;bytes=$n;sha256=$reportHash}
if($rows.Count -gt 512 -or $total -gt 16777216){throw 'ARTIFACT_BUDGET'}
$data=[ordered]@{schema='CONTRACT03_SEMANTICS_A_MANIFEST_V1';batch=$o.batch;roots=@{evidence=$r;report=$t};candidateManifest=$o.candidateManifest;candidateSourceSeal=$o.candidateSourceSeal;files=$rows;excluded=@('manifest itself','freeze receipt produced after manifest','coordinator send receipt produced after complete report is sent')}
[IO.File]::WriteAllText($manifest,($data|ConvertTo-Json -Depth 9),[Text.UTF8Encoding]::new($false))
$bad=@();foreach($x in $rows){$h=(Get-FileHash -LiteralPath $x.absolutePath -Algorithm SHA256).Hash.ToLowerInvariant();if($h -cne $x.sha256 -or (Get-Item -LiteralPath $x.absolutePath).Length -ne $x.bytes){$bad+=$x.absolutePath}}
if($bad.Count){throw 'NEW_MANIFEST_READBACK_MISMATCH'}
$out=[ordered]@{schema='CONTRACT03_SEMANTICS_A_FREEZE_RECEIPT_V1';batch=$o.batch;reportPath=$report;reportSha256=$reportHash;manifestPath=$manifest;manifestSha256=(Get-FileHash -LiteralPath $manifest -Algorithm SHA256).Hash.ToLowerInvariant();files=$rows.Count;bytes=$total;bad=$bad;verdict='PASS_IN_SCOPE_SEMANTICS_A_ONLY';semanticCases=366;semanticPassed=366;pureStaticCases=34;pureStaticPassed=34;totalLogicalCases=400;independent17PositivePassed=17;original45Passed=45;original98FrozenUnchanged=$true;originalZIP99Unchanged=$true;allNewOriginalsReturned=$true;newUnknown=$false;oldRuntimeQueries=0;readConservativeBound=$bound;readBudget=67108864;formalB='NOT_RUN';realSDK=0;realNativeRoute=0;D1='NOT_PASSED';M0='NOT_STARTED';automaticNextTest=$false;utc=[DateTimeOffset]::UtcNow.ToString('o')}
[IO.File]::WriteAllText($receiptPath,($out|ConvertTo-Json -Depth 7),[Text.UTF8Encoding]::new($false));$out|ConvertTo-Json -Depth 4
