param([string]$ScriptPath)
$tokens=$null;$errors=$null
$null=[System.Management.Automation.Language.Parser]::ParseFile($ScriptPath,[ref]$tokens,[ref]$errors)
if($errors.Count -ne 0){throw ($errors | Out-String)}
'PASS observer full AST parse; no execution'
