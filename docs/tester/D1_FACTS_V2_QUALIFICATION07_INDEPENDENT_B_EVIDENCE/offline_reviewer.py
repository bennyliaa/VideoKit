"""One independent finite synthetic reviewer. Never a human/LIVE approval.

It reads the returned original packet and exported observation, never rebuilds
a Capture or opens a process. The original trusted host keeps that object.
"""
from pathlib import Path
from datetime import datetime,timedelta
import sys,json,argparse
R=Path(__file__).resolve().parent;B=R.parents[1]/'coder/d1android02-facts-v2-qualification07/rev2';sys.path.insert(0,str(B/'tools'))
from facts_contract import dec,enc,sha,decode_entry,EVIDENCE_BYTES,exact
from immutable_evidence import read
p=argparse.ArgumentParser();p.add_argument('--request',required=True);p.add_argument('--reply-root',required=True);a=p.parse_args()
request=Path(a.request);root=Path(a.reply_root)
if not request.is_absolute() or not request.is_relative_to(R/'fixtures') or root!=request.parent/'reply' or root.exists():raise ValueError('OFFLINE_REVIEW_FIXED_ROOT')
r=dec(request.read_bytes(),EVIDENCE_BYTES,'OFFLINE_REVIEW_REQUEST')
exact(r,{'schema','fixtureOnly','candidateUtf8','bundle','outerReturn','preauthUtf8','policyUtf8','packetRef','target','serviceCount','reviewTurnId','processChars'},'OFFLINE_REVIEW_REQUEST_SCHEMA')
if r['schema']!='OFFLINE_REVIEW_REQUEST_V1' or r['fixtureOnly'] is not True or r['target']['mode']!='OFFLINE_FIXTURE' or type(r['serviceCount']) is not int or r['serviceCount'] not in (0,1,8,16,68):raise ValueError('OFFLINE_REVIEW_ONLY')
if type(r['processChars']) is not int or r['processChars'] not in (0,12000) or (r['processChars'] and r['serviceCount']!=68):raise ValueError('OFFLINE_REVIEW_PROCESS_FIXTURE')
candidate=dec(r['candidateUtf8'].encode(),EVIDENCE_BYTES,'OFFLINE_CANDIDATE');outer=r['outerReturn'];bundle=r['bundle'];policy=dec(r['policyUtf8'].encode(),16384,'POLICY');template=dec(r['preauthUtf8'].encode(),16384,'TEMPLATE')
if candidate['approved'] is not False or candidate['status']!='REQUIRES_REVIEW' or candidate['bundleSha256']!=sha(enc(bundle)) or bundle['outerReturnSha256']!=sha(enc(outer)):raise ValueError('OFFLINE_REVIEW_ORIGINAL_LINK')
ledger={};packet=read(r['packetRef'],str(Path(template['evidenceRoot'])/'v2-original-return'),'facts-entry-'+template['scope']+'.json',ledger,262144)
if sha(packet)!=outer['stdoutSha256']:raise ValueError('OFFLINE_REVIEW_PACKET_HASH')
identity=dict(pid=outer['ownerPid'],creationFileTime=outer['creationFileTime'],argv=outer['creatorArgv'],image=outer['image'])
d=decode_entry(packet,r['preauthUtf8'].encode(),r['policyUtf8'].encode(),outer['creatorArgv'],identity,lambda q:Path(q).read_bytes());facts=d['parsed'];start=d['receipt']['collectedAtUtc'];end=(datetime.fromisoformat(start)+timedelta(seconds=300)).isoformat()
home=candidate['home'];evidence={}
hb=enc(dict(schema='GLOBAL_IDLE_HOME_REVIEW_EVIDENCE_V1',mode='OFFLINE_FIXTURE',factScope=bundle['factScope'],rawSha256=bundle['rawSha256'],firmware=facts['fingerprint'],home=home,statement='EXACT_OBSERVED_HOME_IDENTITY'));evidence[sha(hb)]=hb.decode();services=[]
packages=[x for x in facts['systemPackages'] if x['package']!=home['package']]
if len(packages)<r['serviceCount']:raise ValueError('OFFLINE_REVIEW_SYSTEM_FACTS')
for package in packages[:r['serviceCount']]:
 s=dict(packages=[package['package']],process=package['package']+':worker',user=0,uid=package['uid'],kind='PERS',state=5,category='NONCONTENDING_SYSTEM_SERVICE',firmware=facts['fingerprint'],factScope=bundle['factScope'],validFromUtc=start,validToUtc=end,range='EXACT_SNAPSHOT')
 if r['processChars']:s['process']=package['package']+':'+'w'*(r['processChars']-len(package['package'])-1)
 eb=enc(dict(schema='GLOBAL_IDLE_SERVICE_REVIEW_EVIDENCE_V1',mode='OFFLINE_FIXTURE',rawSha256=bundle['rawSha256'],**s));s['evidenceSha256']=sha(eb);evidence[sha(eb)]=eb.decode();services.append(s)
review=dict(schema='GLOBAL_IDLE_FACT_REVIEW_V2',sourceThreadId='01a107c3-2bf9-7fa0-94a0-234258ca6774',sourceTurnId=r['reviewTurnId'],mode='OFFLINE_FIXTURE',approvedForQualification=True,candidateSha256=sha(r['candidateUtf8'].encode()),bundleSha256=candidate['bundleSha256'],target=r['target'],notBeforeUtc=start,expiresUtc=end,home=home,homeEvidenceSha256=sha(hb),services=services)
raw=enc(review);root.mkdir();(root/'review.json').write_bytes(raw);(root/'policy-evidence.json').write_bytes(enc(evidence))
reply=dict(schema='OFFLINE_SYNTHETIC_REVIEW_REPLY_V1',fixtureOnly=True,realHumanApproval=False,reviewPath=str(root/'review.json'),evidencePath=str(root/'policy-evidence.json'),approvedReviewSha256=sha(raw),candidateSha256=review['candidateSha256'],bundleSha256=review['bundleSha256'],fileReads=ledger)
sys.stdout.buffer.write(enc(reply))
