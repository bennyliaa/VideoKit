"""Reuse frozen C02 package matching; fetch public details for ONLY its 47 matched advisory IDs."""
import argparse,json,urllib.request,hashlib,concurrent.futures
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('root');p.add_argument('--fetch',action='store_true');args=p.parse_args();root=Path(args.root).resolve()
baseline=root/'docs/coder/d1c02/evidence';out=root/'docs/coder/d1c08/evidence';details=out/'advisories';details.mkdir(parents=True,exist_ok=True)
load=lambda p:json.loads(p.read_text(encoding='utf-8'));original=load(baseline/'osv-results.json');inventory=load(baseline/'supply-inventory.json');component={r['coordinate']:r for r in inventory['components']}
ids=sorted({x['id'] for r in original['results'] for x in r['vulnerabilities']})
def get(identifier):
    dest=details/(identifier+'.json')
    if dest.exists():return identifier,None
    if not args.fetch:return identifier,'NOT_FETCHED'
    try:
        req=urllib.request.Request('https://api.osv.dev/v1/vulns/'+identifier,headers={'User-Agent':'VideoKit-D1-C08-advisory-review'})
        with urllib.request.urlopen(req,timeout=30) as response:data=response.read()
        value=json.loads(data);assert value['id']==identifier;dest.write_bytes(data);return identifier,None
    except Exception as e:return identifier,type(e).__name__+': '+str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:failures=[{'id':i,'error':error} for i,error in executor.map(get,ids) if error]
review=[]
for original_row in original['results']:
    if not original_row['vulnerabilities']:continue
    coordinate=original_row['coordinate'];maven=':'.join(coordinate.split(':')[:2]);configs=component[coordinate]['configurations'];advisories=[]
    for hit in original_row['vulnerabilities']:
        identifier=hit['id'];file=details/(identifier+'.json')
        if not file.exists():continue
        value=load(file);affected=[a for a in value.get('affected',[]) if a.get('package',{}).get('ecosystem')=='Maven' and a['package']['name']==maven]
        fixed=sorted({event['fixed'] for a in affected for r in a.get('ranges',[]) for event in r.get('events',[]) if 'fixed' in event})
        advisories.append({'id':identifier,'summary':value.get('summary',''),'withdrawn':value.get('withdrawn'),'fix_versions_by_advisory':fixed,'severity':value.get('severity',[]),'primary_references':[r['url'] for r in value.get('references',[]) if r['type'] in ('ADVISORY','FIX','REPORT','WEB')],'detail_sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
    if coordinate.startswith('io.netty:'):
        reachability='Declared only by UTP core / emulator-control. None of these task paths were executed in D1; Gradle connected/managed instrumentation is restricted. Direct APK instrumentation later does not start UTP. Native/Binder test process isolation is separate from Netty tool services. No universal unreachable assertion.'
        decision='RESTRICTED_USE: no UTP/remote emulator-control until a supported AGP/UTP graph contains official fixed versions and is compatibility-tested. No forced internal Netty override.'
    elif coordinate.startswith('org.apache.commons:'):
        reachability='Loaded by lint/result-listener tool classpaths; current lint ran on this local project. Version match is real; actual hostile format-string/API call requires per-advisory caller proof. Do not accept untrusted external projects/results.'
        decision='RESTRICTED_USE / CALLER_REVIEW_REQUIRED: local known project only; upgrade with supported lint/UTP toolchain or exact API fix after official compatibility review.'
    elif coordinate.startswith('org.apache.httpcomponents:'):
        reachability='Lint/result-listener can make HTTP calls. Current final build was offline; no arbitrary URL/remote-result transport ran. Remote insecure routing/host ambiguity is still a risk if tools are enabled online.'
        decision='RESTRICTED_USE: offline pinned build; do not enable remote result listener or attacker-controlled URLs. Compatible toolchain fix is required before relaxing restrictions.'
    else:
        reachability='BouncyCastle is on lint/result-listener classpaths, not APKs. Certificate, ASN.1 and cryptographic parsing may be reachable for hostile tool inputs; this package ran lint on known local artifacts. Reachability cannot be universally ruled out.'
        decision='RESTRICTED_USE / SECURITY_REVIEW_REQUIRED: only pinned local artifacts/self-generated debug signing; no hostile certificates/archives or remote listener. Follow official fixed ranges in compatible lint/UTP upgrade; no blind provider override.'
    review.append({'coordinate':coordinate,'scope':original_row['scope'],'configurations':configs,'advisories':advisories,'reachability':reachability,'decision':decision,'patched':False})
result={'candidateId':'D1-20261005-C08','scope':'No repeat ecosystem scan; frozen C02 exact matches reused and public advisory details expanded','matched_components':len(review),'unique_advisories':len(ids),'fetch_failures':failures,'baseline_osv_sha256':hashlib.sha256((baseline/'osv-results.json').read_bytes()).hexdigest(),'components':review}
(out/'tool-vulnerability-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# C08 tool vulnerability review','This is a version-match and constrained-use decision, not a patch, complete reachability proof, or risk waiver. Complete primary advisory data and exact fixed ranges are under advisories/.']
for row in review:
    lines+=['\n## '+row['coordinate'],'Configurations: '+', '.join(row['configurations']),'Reachability: '+row['reachability'],'Decision: '+row['decision']]
    for advisory in row['advisories']:
        lines+=['- ['+advisory['id']+'](https://osv.dev/vulnerability/'+advisory['id']+'): '+advisory['summary']+'; official fixed events: '+(', '.join(advisory['fix_versions_by_advisory']) or 'not declared for this package; do not invent a safe version')]
        lines+=['  Primary reference: '+u for u in advisory['primary_references'] if '/security/advisories/' in u][:2]
(out/'TOOL_VULNERABILITY_REVIEW.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('components',len(review),'unique advisories',len(ids),'fetch failures',failures)
