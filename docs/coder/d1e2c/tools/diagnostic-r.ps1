param(
    [Parameter(Mandatory=$true)][string]$FixtureRoot,
    [Parameter(Mandatory=$true)][ValidateSet('AddType','LoadFrom')][string]$Loader,
    [Parameter(Mandatory=$true)][string]$Owner
)
$ErrorActionPreference = 'Stop'
try {
    # Only built-in parameter binding, core GUID validation, and Console IO
    # precede this first checkpoint. No JSON, command/module import, DLL load,
    # fixture enumeration, process query, or native measurement is performed.
    $parsedOwner = [guid]::Empty
    if (-not ([guid]::TryParseExact($Owner, 'N', [ref]$parsedOwner) -or [guid]::TryParseExact($Owner, 'D', [ref]$parsedOwner))) {
        throw 'DIAGNOSTIC_OWNER_INVALID'
    }
    if ($Loader -cne 'AddType' -and $Loader -cne 'LoadFrom') { throw 'DIAGNOSTIC_LOADER_INVALID' }
    [Console]::WriteLine('E2C_DIAGNOSTIC_STAGE|MINIMAL_START|' + $PID + '|' + $Owner)
    [Console]::Out.Flush()
    $acknowledgement = [Console]::In.ReadLine()
    if ($null -eq $acknowledgement -or $acknowledgement -ceq 'STOP') { exit 0 }
    if ($acknowledgement -cne 'ACK:MINIMAL_START') { throw 'DIAGNOSTIC_ACK_INVALID:MINIMAL_START' }

    $packageRoot = [System.IO.Path]::GetFullPath([System.IO.Path]::Combine($PSScriptRoot, '..'))
    $assemblyPath = [System.IO.Path]::GetFullPath([System.IO.Path]::Combine($packageRoot, 'artifacts', 'E2C.dll'))
    if ([System.IO.File]::Exists([System.IO.Path]::Combine($packageRoot, 'evidence', 'freeze-summary.json'))) {
        throw 'FROZEN_PACKAGE_READ_ONLY_NEW_AUTHORIZED_BATCH_REQUIRED'
    }
    if (-not [System.IO.File]::Exists($assemblyPath)) { throw 'EXISTING_E2C_ASSEMBLY_REQUIRED' }
    if ($Loader -ceq 'AddType') {
        Add-Type -Path $assemblyPath
    } else {
        [void][System.Reflection.Assembly]::LoadFrom($assemblyPath)
    }
    [Console]::WriteLine('E2C_DIAGNOSTIC_STAGE|LOAD_COMPLETE|' + $PID + '|' + $Owner)
    [Console]::Out.Flush()
    $acknowledgement = [Console]::In.ReadLine()
    if ($null -eq $acknowledgement -or $acknowledgement -ceq 'STOP') { exit 0 }
    if ($acknowledgement -cne 'ACK:LOAD_COMPLETE') { throw 'DIAGNOSTIC_ACK_INVALID:LOAD_COMPLETE' }

    # RHost itself performs both remaining pauses on this same thread. The
    # controller sends the real HMAC HELLO only after ACK:INIT_COMPLETE.
    exit [VideoKit.E1.RHost]::RunDiagnostic($FixtureRoot, $Owner)
} catch {
    $detail = $_.Exception.Message.Replace("`r", ' ').Replace("`n", ' ').Replace('|', '/')
    if ($detail.Length -gt 240) { $detail = $detail.Substring(0, 240) }
    [Console]::Error.WriteLine('E2C_DIAGNOSTIC_ERROR|' + $_.Exception.GetType().Name + '|' + $detail)
    [Console]::Error.Flush()
    exit 1
}
