from pathlib import Path
import hashlib,json,datetime
E=Path(__file__).resolve().parent;R=E.parents[2]
report=R/'docs/tester/D1_E4A_N_DEVICE_TEST_REPORT_V1.0.md'
methods=['normalMp4SixRealFrames','normalAviSixRealFrames','capabilityDenialDoesNotOpenSource','binderRefusesBeforeBeginAndOversizeParcel','cancelRejectsWrongEpochOversizeAndLateFrame']
cases=[{'device':d,'method':m,'result':'PASS' if d=='tablet' and m==methods[3] else 'BLOCKED','attempts':int(d=='tablet' and m==methods[3])} for d in ['phone','tablet'] for m in methods]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(E.rglob('*')) if p.is_file() and p.name not in ['review-summary.json','evidence-manifest.json','coordinator-notification.json']]
(E/'evidence-manifest.json').write_text(json.dumps({'files':rows},indent=2)+'\n',encoding='utf-8')
summary={'at':datetime.datetime.now().astimezone().isoformat(),'report':report.relative_to(R).as_posix(),'reportSha256':sha(report),'conclusion':'BATCH_BLOCKED_PREPARATION_FAILED','cases':cases,'totals':{'PASS':1,'BLOCKED':9,'FAIL':0},'preparationFailure':'E4A-N-PREP-01','fixturePartialBytes':81407,'fixturePartialSha256':'a790f44fc3c6ff4579c83f57b42a4b31cd95278cca28fd4aa6b97fd295fd9695','normalReceiptAdmission':'NOT_ADMITTED','sourceHostHashBytes':736803758,'sourceCopyInputBytes':349102,'deviceFixtureHashBytes':81407,'testFixtureHashBytes':0,'quarantineRuns':0,'gradleRuns':0,'deviceListEffectiveQueries':1,'inFlight':[],'D1Passed':False,'M0Started':False,'notification':'PENDING'}
(E/'review-summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(summary['reportSha256'])
