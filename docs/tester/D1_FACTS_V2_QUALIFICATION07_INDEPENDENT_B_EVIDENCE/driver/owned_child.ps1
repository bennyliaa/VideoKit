[CmdletBinding()]
param()
$ErrorActionPreference='Stop'
if($args.Count -ne 0){throw 'EXTRA_CHILD_ARGUMENTS'}
[Console]::Out.WriteLine('OWNED_DRIVER_PS_CHILD_ONLY')
exit 0
