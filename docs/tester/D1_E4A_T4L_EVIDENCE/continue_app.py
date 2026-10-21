"""Complete only the originally authorized app checklist; never rerun shell.
Original driver incorrectly matched LF-only terminator against complete CRLF.
Remote scripts and original attempt/result remain untouched.
"""
from pathlib import Path
import hashlib,json
E=Path(__file__).resolve().parent
original=(E/'run_device.py').read_text()
assert not (E/'app-original.json').exists()
r=json.loads((E/'result.json').read_text())
assert r['metadataCommands']==1 and r['retainedLocalOwners']==0 and r['shell_stdout'].splitlines()[-1]=='CHECKLIST_END'
source=original.replace('for app in (False,True):','for app in (True,):').replace("new('attempt.json'","new('app-continuation-attempt.json'").replace("new('result.json'","new('app-continuation-result.json'").replace(".endswith('CHECKLIST_END\\n')",".splitlines()[-1]=='CHECKLIST_END'")
# Parenthesize the revised comparison so the existing and guard remains explicit.
compile(source,'T4L_APP_ONLY_REMAINING_CHECKLIST','exec')
note=dict(reason='HOST_LF_ONLY_TERMINATOR_REJECTED_COMPLETE_CRLF_SHELL_RECEIPT',shellReruns=0,remainingMetadata=1,remoteScriptsUnchanged=True,originalDriverSha256=hashlib.sha256((E/'run_device.py').read_bytes()).hexdigest())
with (E/'host-continuation-note.json').open('x') as f:json.dump(note,f,indent=2)
exec(compile(source,'T4L_APP_ONLY_REMAINING_CHECKLIST','exec'),globals())
