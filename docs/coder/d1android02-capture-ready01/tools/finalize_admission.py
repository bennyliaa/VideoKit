from pathlib import Path
B=Path(__file__).resolve().parents[1]
p=B/'tools/admission.ps1.txt';s=p.read_text();s=s.replace("if($policy.mode -ceq 'PREPARATION_ONLY'){throw 'PREPARATION_ONLY_NO_EXECUTION_AUTHORIZATION'}","if($policy.mode -ceq 'PREPARATION_ONLY'){throw 'PREPARATION_ONLY_NO_EXECUTION_AUTHORIZATION'}\n$localAdmissionTimer=[Diagnostics.Stopwatch]::StartNew()")
s=s.replace("$request=ReadJsonExact $RequestPath", "$snapshotRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))+[IO.Path]::DirectorySeparatorChar;$requestFull=[IO.Path]::GetFullPath($RequestPath);if(-not $requestFull.StartsWith($snapshotRoot,[StringComparison]::OrdinalIgnoreCase) -or [IO.Path]::GetExtension($requestFull) -cne '.json'){throw 'EXACT_SNAPSHOT_REQUEST_PATH'};NoLinks $requestFull\n$request=ReadJsonExact $RequestPath")
p.write_text(s,encoding='utf-8')
p=B/'tools/derive_capture.py';s=p.read_text();a=s.index('replace("$c=@{');assert 'id=$request.id;semanticChecked' in s[a:a+150]
needle="replace('$i.expectedBytes -gt 10480388','$i.expectedBytes -gt 7151481')"
s=s.replace(needle,needle+'''\nreplace("  if($c.firstFailure){throw 'SOURCE_PIN_REJECTED_BEFORE_CHILD'}", "  if($c.firstFailure){throw 'SOURCE_PIN_REJECTED_BEFORE_CHILD'};if($timer.Elapsed.TotalSeconds -ge $request.qualificationSeconds -or (-not $fixture -and $localAdmissionTimer.Elapsed.TotalSeconds -ge $activation.localProofSeconds)){Fail 'PRESTART_LOCAL_OR_QUALIFICATION_BOUND';throw 'PRESTART_STOP_NO_CHILD'}")''')
p.write_text(s,encoding='utf-8')
# Remove no-op exploratory lines from the source derivation helper before delivery.
p=B/'tools/refine_bindings.py';s=p.read_text();s='\n'.join(line for line in s.splitlines() if 'if False else s' not in line)+'\n';p.write_text(s,encoding='utf-8')
print('Request files confined to deployment snapshot; prestart time gate before child; no new ownership framework')
