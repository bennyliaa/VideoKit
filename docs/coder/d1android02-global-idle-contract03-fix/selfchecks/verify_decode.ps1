param([string]$OutputFile)
$ErrorActionPreference='Stop'
$b=Split-Path $PSScriptRoot
$entry=Join-Path $b 'tools/capture_android02.ps1'
$tokens=$null;$errors=$null;$ast=[Management.Automation.Language.Parser]::ParseFile($entry,[ref]$tokens,[ref]$errors)
if($errors.Count){throw 'ENTRY_SYNTAX_ERROR'}
$f=@($ast.FindAll({param($n) $n -is [Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -ceq 'RoleSemantic'},$true));if($f.Count -ne 1){throw 'ONE_REAL_PRODUCTION_SEMANTIC_FUNCTION'}
# Execute only the exact frozen function definition, never the entry body.
Invoke-Expression $f[0].Extent.Text
$p=Join-Path (Split-Path $OutputFile) 'invalid-utf8.bin';[IO.File]::WriteAllBytes($p,[byte[]]@(255,254))
$rejected=$false;try{$null=RoleSemantic 'global_idle' $p $true}catch{$rejected=$true}
if(-not $rejected){throw 'INVALID_UTF8_NOT_REJECTED'}
[IO.File]::WriteAllText($OutputFile,(@{schema='GLOBAL_IDLE_REAL_PS_DECODE_CHECK_V1';invalidUtf8Rejected=$true;entrySyntaxErrors=0;actualFrozenFunctionOnly=$true;entryBodyExecuted=$false;sdk=0}|ConvertTo-Json))
