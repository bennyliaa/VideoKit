from pathlib import Path
import hashlib,json,difflib
B=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
old=(B/'reference/ready02-entry.ps1').read_text();s=old.replace('d1android02-capture-ready02-fix','d1android02-capture-ready03-fix').replace('D1_ANDROID02_CAPTURE_READY02_FIX_REVIEW_EVIDENCE','D1_ANDROID02_CAPTURE_READY03_FIX_REVIEW_EVIDENCE')
oldowner=sha(B/'reference/ready02-outer-owner.py');newowner=sha(B/'tools/outer_owner.py');s=s.replace(oldowner,newowner)
s=s.replace('function ReadJsonExact(', '$requestBodyReadBytes=[long]0;$requestBodyReadCalls=0\nfunction ReadJsonExact(',1)
needle='$raw=[IO.File]::ReadAllBytes($Path);'
assert needle in s;s=s.replace(needle,needle+"if($Path -ceq $RequestPath){$script:requestBodyReadBytes+=[long]$raw.Length;$script:requestBodyReadCalls++};",1)
needle='$ownerCurrentReadCost=[long]$ad.admissionWriteBytes';assert needle in s
s=s.replace(needle,needle+'+[long]$requestBodyReadBytes')
s=s.replace("$console.proofReadBytes=$proofReadBytes;","$console.proofReadBytes=$proofReadBytes;$console.logicalControlReads=@{requestBodyBytes=$requestBodyReadBytes;requestBodyReadCalls=$requestBodyReadCalls;ownerAdmissionBytes=([long]$ownerCurrentReadCost-$requestBodyReadBytes);predecessorProofAndNativeBytes=([long]$proofReadBytes-$ownerCurrentReadCost)};")
(B/'tools/capture_android02.ps1').write_text(s,encoding='utf-8')
p=json.loads((B/'release/capture-policy.json').read_text());p.update(entrySha256=sha(B/'tools/capture_android02.ps1'),outerOwnerSha256=newowner);save(B/'release/capture-policy.json',p)
a=json.loads((B/'release/activation-required.template.json').read_text());a.update(entrySha256=p['entrySha256'],outerOwnerSha256=newowner);save(B/'release/activation-required.template.json',a)
(B/'evidence/ready02-to-ready03-entry.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile='frozen-ready02-entry',tofile='ready03-entry')),encoding='utf-8')
o=(B/'reference/ready02-outer-owner.py').read_text();n=(B/'tools/outer_owner.py').read_text();(B/'evidence/ready02-to-ready03-owner.patch').write_text(''.join(difflib.unified_diff(o.splitlines(True),n.splitlines(True),fromfile='frozen-ready02-owner',tofile='ready03-owner')),encoding='utf-8')
print(json.dumps({'entry':p['entrySha256'],'owner':newowner,'producer':sha(B/'selfchecks/capture_fixture.py')}))
