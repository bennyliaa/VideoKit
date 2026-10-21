"""Metadata-only supply review and OSV matching; never sends media or source contents."""
import argparse,hashlib,json,xml.etree.ElementTree as ET,urllib.request,zipfile,io
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('root');p.add_argument('cache');p.add_argument('--fetch',action='store_true');p.add_argument('--osv',action='store_true');args=p.parse_args();root=Path(args.root).resolve();cache=Path(args.cache);out=root/'docs/coder/d1c02/evidence';parents=out/'license-parents';parents.mkdir(parents=True,exist_ok=True)
ns={'m':'http://maven.apache.org/POM/4.0.0'};failures=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def request(url,data=None):
    req=urllib.request.Request(url,data=data,headers={'User-Agent':'VideoKit-D1-local-audit','Content-Type':'application/json'} if data else {'User-Agent':'VideoKit-D1-local-audit'})
    with urllib.request.urlopen(req,timeout=30) as r:return r.read()
def pom_for(g,a,v):
    files=list((cache/g/a/v).rglob('*.pom'))
    if files:return files[0]
    dest=parents/(g+'_'+a+'_'+v+'.pom')
    if dest.exists():return dest
    if not args.fetch:return None
    tail=g.replace('.','/')+'/'+a+'/'+v+'/'+a+'-'+v+'.pom'
    hosts=['https://dl.google.com/dl/android/maven2/','https://repo.maven.apache.org/maven2/'] if g.startswith(('androidx.','com.android.')) else ['https://repo.maven.apache.org/maven2/','https://dl.google.com/dl/android/maven2/']
    for host in hosts:
        try:content=request(host+tail);ET.fromstring(content);dest.write_bytes(content);return dest
        except Exception as e:last=type(e).__name__
    failures.append({'coordinate':g+':'+a+':'+v,'stage':'parent-pom','error':last});return None
def licenses(g,a,v,depth=0):
    if depth>4:return [],[]
    file=pom_for(g,a,v)
    if file is None:return [],[]
    tree=ET.parse(file);found=[{'name':item.findtext('m:name',namespaces=ns),'url':item.findtext('m:url',namespaces=ns)} for item in tree.findall('m:licenses/m:license',ns)]
    evidence=[{'coordinate':g+':'+a+':'+v,'pom_sha256':sha(file.read_bytes())}]
    if found:return found,evidence
    parent=tree.find('m:parent',ns)
    if parent is not None:
        values=[parent.findtext('m:'+key,namespaces=ns) for key in ('groupId','artifactId','version')]
        if all(values) and all('${' not in value for value in values):
            inherited,path=licenses(*values,depth+1);return inherited,evidence+path
    return [],evidence
def supplemental(coord):
    mappings={
        'javax.inject:javax.inject:1':('Apache-2.0','javax-inject-sources.snapshot','javax/inject/Inject.java','https://repo.maven.apache.org/maven2/javax/inject/javax.inject/1/javax.inject-1-sources.jar'),
        'net.sf.kxml:kxml2:2.3.0':('MIT','kxml2-2.3.0-sources.snapshot','org/kxml2/io/KXmlParser.java','https://repo.maven.apache.org/maven2/net/sf/kxml/kxml2/2.3.0/kxml2-2.3.0-sources.jar')}
    if coord in mappings:
        name,filename,member,url=mappings[coord];file=out/filename
        if file.exists():
            with zipfile.ZipFile(file) as z:data=z.read(member)
            return [{'name':name,'url':url,'reviewed_source_member':member}],[{'source_snapshot':filename,'sha256':sha(file.read_bytes()),'member_sha256':sha(data)}]
    if coord.startswith(('org.bouncycastle:bcpkix-jdk18on:1.79','org.bouncycastle:bcprov-jdk18on:1.79','org.bouncycastle:bcutil-jdk18on:1.79')):
        file=out/'bouncycastle-1.79-license.snapshot'
        if file.exists():return [{'name':'MIT','url':'https://raw.githubusercontent.com/bcgit/bc-java/r1rv79/LICENSE.html'}],[{'source_snapshot':file.name,'sha256':sha(file.read_bytes())}]
    return [],[]
def embedded_notices(binary):
    found=[]
    try:
        with zipfile.ZipFile(binary) as z:
            for name in z.namelist():
                lower=name.lower();base=Path(name).name.lower()
                if not name.endswith('/') and z.getinfo(name).file_size<512000 and not base.endswith(('.class','.so')) and (base in ('license','notice','copying') or base.startswith(('license.','notice.','copying.'))):
                    data=z.read(name);found.append({'entry':name,'sha256':sha(data),'text':data.decode('utf-8',errors='replace')})
                if name=='classes.jar':found.extend(embedded_notices(io.BytesIO(z.read(name))))
    except zipfile.BadZipFile:pass
    return found
rows=[]
for line in (root/'app/gradle.lockfile').read_text().splitlines():
    if line.startswith('#') or ':' not in line:continue
    coord,configs=line.split('=',1);g,a,v=coord.split(':');groups=configs.split(',');scope='release_runtime' if 'releaseRuntimeClasspath' in groups else 'debug_runtime' if 'debugRuntimeClasspath' in groups else 'tool_compile_or_test';claims,evidence=licenses(g,a,v);artifacts=[];notices=[]
    if not claims:
        reviewed,proof=supplemental(coord);claims=reviewed;evidence+=proof
    for file in sorted((cache/g/a/v).rglob('*')):
        if not file.is_file():continue
        data=file.read_bytes();artifacts.append({'name':file.name,'bytes':len(data),'sha256':sha(data)})
        if file.suffix in ('.jar','.aar'):
            for notice in embedded_notices(file):notice['artifact']=file.name;notices.append(notice)
    rows.append({'coordinate':coord,'scope':scope,'configurations':groups,'licenses':claims,'license_evidence_chain':evidence,'cached_artifacts':artifacts,'embedded_notices':notices,'review':'metadata/embedded notice review, no ownership inference beyond listed evidence'})
result={'candidateId':'D1-20261005-C02','components':rows,'missing_license_claims':[r['coordinate'] for r in rows if not r['licenses']],'fetch_failures':failures}
(out/'supply-inventory.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
for scopes,name in [({'release_runtime','debug_runtime'},'THIRD_PARTY_NOTICE_RUNTIME.md'),({'tool_compile_or_test'},'THIRD_PARTY_NOTICE_TOOLS.md')]:
    chunks=['# D1 C02 third-party metadata and embedded notices','Local audit evidence. Runtime and tool scopes are separated. Not a final distribution legal opinion.']
    for row in rows:
        if row['scope'] not in scopes:continue
        chunks+=['\n## '+row['coordinate']+' ('+row['scope']+')',json.dumps(row['licenses'],ensure_ascii=False)]
        for note in row['embedded_notices']:chunks+=['\n### '+note['artifact']+' : '+note['entry'],note['text']]
    (out/name).write_text('\n'.join(chunks),encoding='utf-8')
vuln=json.loads((out/'osv-results.json').read_text(encoding='utf-8')) if (out/'osv-results.json').exists() and not args.osv else {'status':'NOT_RUN','provider':'https://api.osv.dev/v1/querybatch','scope':'exact Maven package+version matches; no media/source sent','results':[],'failures':[]}
if args.osv:
    for start in range(0,len(rows),60):
        subset=rows[start:start+60];queries=[{'package':{'ecosystem':'Maven','name':':'.join(r['coordinate'].split(':')[:2])},'version':r['coordinate'].split(':')[2]} for r in subset]
        try:
            response=json.loads(request(vuln['provider'],json.dumps({'queries':queries}).encode()))
            if len(response.get('results',[]))!=len(subset):raise ValueError('OSV result length mismatch')
            for row,item in zip(subset,response['results']):vuln['results'].append({'coordinate':row['coordinate'],'scope':row['scope'],'vulnerabilities':item.get('vulns',[])})
        except Exception as e:vuln['failures'].append({'batch_start':start,'error':type(e).__name__+': '+str(e)})
    vuln['status']='PASS_QUERY_COMPLETED' if not vuln['failures'] else 'PARTIAL_OR_BLOCKED'
(out/'osv-results.json').write_text(json.dumps(vuln,ensure_ascii=False,indent=2),encoding='utf-8')
print('components',len(rows),'runtime',sum(r['scope']!='tool_compile_or_test' for r in rows),'missing licenses',result['missing_license_claims']);print('OSV',vuln['status'],'matches',[(r['coordinate'],[x.get('id') for x in r['vulnerabilities']]) for r in vuln['results'] if r['vulnerabilities']])
