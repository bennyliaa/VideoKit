$ErrorActionPreference='Stop'
$rows=@();$bad=@()
foreach($f in @(Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot 'tools') -Filter *.ps1)+@(Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot 'selfchecks') -Filter *.ps1)){
 $tokens=$null;$errors=$null;$ast=[System.Management.Automation.Language.Parser]::ParseFile($f.FullName,[ref]$tokens,[ref]$errors)
 $wrong=@($ast.FindAll({param($n)$n -is [System.Management.Automation.Language.CommandAst] -and $n.GetCommandName() -cin @('true','false','null')},$true)|ForEach-Object {$_.Extent.Text})
 $rows+=@{path=$f.FullName;parseErrors=@($errors|ForEach-Object {$_.Message});bareBooleanCommands=$wrong}
 if($errors.Count -or $wrong.Count){$bad+=$f.FullName}
}
$shapes=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'reference/control-message-shapes06.json') -Raw|ConvertFrom-Json -Depth 24
$tokens=$null;$errors=$null;$ast=[System.Management.Automation.Language.Parser]::ParseFile((Join-Path $PSScriptRoot 'tools/capture_android02.ps1'),[ref]$tokens,[ref]$errors)
$fn=$ast.Find({param($n)$n -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -ceq 'Snapshot'},$true)
$table=$fn.Body.Find({param($n)$n -is [System.Management.Automation.Language.HashtableAst]},$true);$keys=@($table.KeyValuePairs|ForEach-Object {$_.Item1.Value})
if(@(Compare-Object -CaseSensitive @($keys|Sort-Object) @($shapes.sourceSnapshotKeys|Sort-Object)).Count){$bad+='SnapshotShape'}
$t=$null;$e=$null;$refAst=[System.Management.Automation.Language.Parser]::ParseFile((Join-Path $PSScriptRoot 'tools/qualification_reference.ps1'),[ref]$t,[ref]$e)
$t=$null;$e=$null;$admitAst=[System.Management.Automation.Language.Parser]::ParseFile((Join-Path $PSScriptRoot 'tools/admission_checks.ps1'),[ref]$t,[ref]$e)
$inlineRows=@()
foreach($fn in @($refAst.FindAll({param($n)$n -is [System.Management.Automation.Language.FunctionDefinitionAst]},$true))){
 $other=@($admitAst.FindAll({param($n)$n -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -ceq $fn.Name},$true))
 $left=($fn.Extent.Text -split "`r?`n"|ForEach-Object {$_.TrimEnd()}) -join "`n"
 $right=if($other.Count -eq 1){($other[0].Extent.Text -split "`r?`n"|ForEach-Object {$_.TrimEnd()}) -join "`n"}else{''}
 $same=$left -ceq $right;$inlineRows+=@{name=$fn.Name;same=$same};if(-not $same){$bad+='INLINE:'+ $fn.Name}
}
if($inlineRows.Count -ne 11){$bad+='INLINE_FUNCTION_COUNT'}
$out=@{allPassed=($bad.Count -eq 0);files=$rows;inlineFunctions=$inlineRows;bad=$bad;snapshotFields=$keys;productResources=0}
[IO.Directory]::CreateDirectory((Join-Path $PSScriptRoot 'evidence'))|Out-Null
[IO.File]::WriteAllText((Join-Path $PSScriptRoot 'evidence/ps-parse07.json'),($out|ConvertTo-Json -Depth 16 -Compress),[Text.UTF8Encoding]::new($false))
if($bad.Count){throw 'PS_PURE_PARSE_FAILED'}
