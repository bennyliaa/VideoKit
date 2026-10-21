from pathlib import Path
import json,hashlib,difflib
B=Path(__file__).resolve().parents[1];assert not (B/'evidence/capture-adapt-freeze.json').exists()
old=(B/'reference/capture_metadata.ps1').read_text(encoding='utf-8-sig');body=old[old.index('$c=@{'):]
body=body.replace('Resume01CaptureCustody','Render02CaptureCustody').replace('RESUME01_CAPTURE_','RENDER02_CAPTURE_')
body=body.replace('rawBytes=[long]0;','rawBytes=[long]0;textBytes=[long]0;binaryBytes=[long]0;')
body=body.replace('rawBytesKnown=$c.rawBytes;','rawBytesKnown=$c.rawBytes;textBytesKnown=$c.textBytes;binaryBytesKnown=$c.binaryBytes;input=(InputFacts);')
body=body.replace('rawBytes=$_.raw;savedBytes=$_.saved;','kind=$_.kind;rawBytes=$_.raw;savedBytes=$_.saved;readCalls=$_.readCalls;writeCalls=$_.writeCalls;writeAttemptedBytes=$_.writeAttempted;')
body=body.replace('name=$_.name;opened=$_.opened;','name=$_.name;writeRequestedBytes=$_.bytes;opened=$_.opened;')
body=body.replace('function WriteRecord(', (B/'tools/stdin-owner.ps1.txt').read_text(encoding='utf-8')+'\nfunction WriteRecord(')
body=body.replace("$c.rawBytes+=$n;$r.raw+=$n\n     if($c.rawBytes -gt $request.maxTextBytes){Fail 'RAW_QUALIFIER_EXCEEDED';$r.recordFailed=$true}","$c.rawBytes+=$n;$r.raw+=$n\n     if($r.kind -ceq 'BINARY'){$c.binaryBytes+=$n;if($c.binaryBytes -gt $request.maxBinaryBytes){Fail 'BINARY_QUALIFIER_EXCEEDED';$r.recordFailed=$true}}else{$c.textBytes+=$n;if($c.textBytes -gt $request.maxTextBytes){Fail 'TEXT_QUALIFIER_EXCEEDED';$r.recordFailed=$true}}")
body=body.replace('$r.read=$r.pipe.ReadAsync($r.buffer,0,4096)','$r.readCalls++;$r.read=$r.pipe.ReadAsync($r.buffer,0,4096)')
body=body.replace('$b=$r.queue.Dequeue();$r.writingBytes=$b.Length','$b=$r.queue.Dequeue();$r.writingBytes=$b.Length;$r.writeCalls++;$r.writeAttempted+=$b.Length')
body=body.replace("$r=@{role=$role;", "$r=@{role=$role;kind=if($role -ceq 'stdout' -and $request.maxBinaryBytes -gt 0){'BINARY'}else{'TEXT'};readCalls=0;writeCalls=0;writeAttempted=[long]0;")
body=body.replace("  foreach($role in @('stdout','stderr')){\n   $r=", "  OpenPinnedSource\n  if($c.firstFailure){throw 'SOURCE_PIN_REJECTED_BEFORE_CHILD'}\n  foreach($role in @('stdout','stderr')){\n   $r=")
body=body.replace('$r.read=$r.pipe.ReadAsync($r.buffer,0,4096)}', '$r.readCalls++;$r.read=$r.pipe.ReadAsync($r.buffer,0,4096)}')
body=body.replace('$c.process.StandardInput.Close();$c.stdinReturned=$true','PumpInput')
body=body.replace(' PumpReaders\n',' PumpReaders\n PumpInput\n PumpInputSourceClose\n')
body=body.replace('$c.stdinReturned -and (ReadersReturned)','$c.stdinReturned -and (InputReturned) -and (ReadersReturned)')
body=body.replace('if(-not $c.startEntered -and $c.readers.Count -eq 0){$bodyReturned=$true}','if(-not $c.startEntered -and $c.readers.Count -eq 0 -and (InputReturned)){$bodyReturned=$true}')
body=body.replace("$facts.rawAmountUnknown=$c.rawUnknown","$facts.rawAmountUnknown=$c.rawUnknown -or $c.input.pinUnknown -or $c.input.sourceUnknown -or $c.input.writeAmountUnknown")
body=body.replace("$console.recordWriteBytesKnown=$c.recordBytes;","$console.recordWriteBytesKnown=$c.recordBytes;$console.rawTextSavedBytesKnown=($c.readers|Where-Object kind -CEQ 'TEXT'|Measure-Object saved -Sum).Sum;$console.binaryArchiveSavedBytesKnown=($c.readers|Where-Object kind -CEQ 'BINARY'|Measure-Object saved -Sum).Sum;")
body=body.replace("$console.externalControllerExitProofStillRequired=$true","$console.externalControllerExitProofStillRequired=$true;$console.consoleBytes=0;$console.consoleForwardReserveBytes=4096;$console.controlRecordAndConsoleKnown=0")
body=body.replace('$text=($console|ConvertTo-Json -Depth 12 -Compress)+"`n";$consoleBytes=[Text.UTF8Encoding]::new($false).GetByteCount($text)', '''for($sizing=0;$sizing -lt 4;$sizing++){$text=($console|ConvertTo-Json -Depth 12 -Compress)+"`n";$console.consoleBytes=[Text.UTF8Encoding]::new($false).GetByteCount($text);$console.controlRecordAndConsoleKnown=$c.recordBytes+$console.consoleBytes}
$text=($console|ConvertTo-Json -Depth 12 -Compress)+"`n";$consoleBytes=[Text.UTF8Encoding]::new($false).GetByteCount($text)''')
body=body.replace('$r.readCalls++;$r.readCalls++;','$r.readCalls++;')
body=body.replace("WriteRecord 'capture-halted.json' (Snapshot) 2048", "WriteRecord 'capture-halted.json' @{id=$c.id;scope=$c.scope;owner=$c.owner;controllerPid=$PID;childPid=$c.childPid;firstFailure=$c.firstFailure;rawKnownPrefix=$c.rawBytes;unknownOrPending=$true;noSuccessor=$true} 2048")
body=body.replace('$console.consoleForwardReserveBytes=4096;', '$console.consoleForwardReserveBytes=4096;$console.proofReadBytes=$proofReadBytes;$console.batchSdkChildrenEntered=$batchSdkBefore+[int]$c.started;$console.batchTextChargedBytesKnown=[long]0;$console.batchBinaryArchiveBytesKnown=$batchBinaryBefore+[long]$console.binaryArchiveSavedBytesKnown;$console.batchAmountUnknown=[bool]($c.rawUnknown -or $c.recordAmountUnknown -or $c.input.pinUnknown -or $c.input.sourceUnknown -or $c.input.writeAmountUnknown -or @($c.readers|Where-Object savedAmountUnknown -EQ $true).Count -gt 0);')
body=body.replace('$console.controlRecordAndConsoleKnown=$c.recordBytes+$console.consoleBytes}', '$console.controlRecordAndConsoleKnown=$c.recordBytes+$console.consoleBytes;$console.batchTextChargedBytesKnown=$batchTextBefore+$c.textBytes+$c.recordBytes+2*$console.consoleBytes+$proofReadBytes}')
body=body.replace('if($consoleBytes -gt 4096){while($true){Start-Sleep -Milliseconds 500}}', '''if($c.recordBytes+2*$consoleBytes+$proofReadBytes -gt 14000 -or $console.batchTextChargedBytesKnown -gt 4194304 -or $console.batchBinaryArchiveBytesKnown -gt 16777216){Fail 'CONTROL_OR_BATCH_QUALIFIER_EXCEEDED';$console.firstFailure=$c.firstFailure;$console.captureQualified=$false;$text=($console|ConvertTo-Json -Depth 12 -Compress)+"`n"}
if([Text.UTF8Encoding]::new($false).GetByteCount($text) -gt 8192){while($true){Start-Sleep -Milliseconds 500}}''')
begin=body.index('for($sizing=0;');end=body.index('[Console]::OutputEncoding',begin)
body=body[:begin]+'''for($sizing=0;$sizing -lt 8;$sizing++){
 $text=($console|ConvertTo-Json -Depth 12 -Compress)+"`n";$console.consoleBytes=[Text.UTF8Encoding]::new($false).GetByteCount($text)
 $console.controlRecordAndConsoleKnown=$c.recordBytes+$console.consoleBytes
 $console.batchTextChargedBytesKnown=$batchTextBefore+$c.textBytes+$c.recordBytes+2*$console.consoleBytes+$proofReadBytes
 if($c.recordBytes+2*$console.consoleBytes+$proofReadBytes -gt 14000 -or $console.batchTextChargedBytesKnown -gt 4194304 -or $console.batchBinaryArchiveBytesKnown -gt 16777216){Fail 'CONTROL_OR_BATCH_QUALIFIER_EXCEEDED';$console.firstFailure=$c.firstFailure;$console.captureQualified=$false}
}
$text=($console|ConvertTo-Json -Depth 12 -Compress)+"`n";$consoleBytes=[Text.UTF8Encoding]::new($false).GetByteCount($text)
if($consoleBytes -gt 8192 -or $consoleBytes -ne $console.consoleBytes){while($true){Start-Sleep -Milliseconds 500}}
'''+body[end:]
# The single output console is a bounded control record; no raw child output is forwarded.
text=(B/'tools/admission.ps1.txt').read_text(encoding='utf-8')+'\n'+body
(B/'tools/capture_render02.ps1').write_text(text,encoding='utf-8')
(B/'evidence/source-diff.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),text.splitlines(True),fromfile='frozen-original-capture_metadata.ps1',tofile='capture_render02.ps1')),encoding='utf-8')
policy={'schema':'RENDER02_CAPTURE_POLICY_V1','mode':'PREPARATION_ONLY','entrySha256':hashlib.sha256((B/'tools/capture_render02.ps1').read_bytes()).hexdigest(),'scope':'UNASSIGNED_NEW_SCOPE_REQUIRED','planId':'UNASSIGNED','evidenceRoot':'UNASSIGNED','toolSha256':'UNASSIGNED_NEW_REVIEW_REQUIRED','authorization':None,'independentReview':None,'sdkChildCap':32,'textCap':4194304,'binaryArchiveCap':16777216,'plannedSlots':28,'runnableSerialSlots':25,'screenshots':'NOT_RUN_LIVE_PARENT_ASSOCIATION_UNPROVEN','spare4':'NOT_RETRY_OR_MANUAL_AUTHORIZATION'}
(B/'release/capture-policy.json').write_text(json.dumps(policy,ensure_ascii=False,indent=2),encoding='utf-8')
print('DERIVED PREPARATION_ONLY ENTRY; no execution')
