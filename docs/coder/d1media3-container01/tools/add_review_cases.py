from pathlib import Path
B=Path(__file__).resolve().parents[1];assert not (B/'evidence/media3-container01-freeze.json').exists(),'FROZEN'
for name in ['run_suites.py','review_all.py']:
 p=B/'tools'/name;s=p.read_text()
 marker="for name,cls,extra in plan:" if name=='run_suites.py' else "for mode,cp in [('source',source),('production',prod)]:"
 add="""fixture=json.loads((B/'reference/approved-sample-scope.json').read_text(encoding='utf-8'))
project=B.parents[2]
plan += [('extractor-input','ExtractorInputCheck',[]),('approved-read','ApprovedSampleReadCheck',[str(project/fixture['path']),fixture['sha256']]),('platform-availability','Media3AvailabilityCheck',[])]
"""
 assert marker in s;s=s.replace(marker,add+marker);p.write_text(s,encoding='utf-8')
print('Preserved all baseline regressions; added actual input and availability cases.')
