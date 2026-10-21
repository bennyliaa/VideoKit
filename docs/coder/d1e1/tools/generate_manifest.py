"""Offline conversion of accepted R3/R4 documents; never reads fixtures or starts helpers."""
import argparse, hashlib, json, re
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parents[2]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def table(path,columns):
    for line in path.read_text(encoding='utf-8').splitlines():
        cells=[s.strip() for s in line.strip('|').split('|')]
        if len(cells)==columns and re.fullmatch(r'[PQ]\d\d-[A-Z0-9]+',cells[0]): yield cells
def split_top(text):
    depth=0;start=0;out=[]
    for i,ch in enumerate(text):
        if ch=='(':depth+=1
        elif ch==')':depth-=1
        elif ch==',' and depth==0:out.append(text[start:i].strip());start=i+1
    out.append(text[start:].strip());return out
def tokens(text):
    text=text.split('→',1)[1]
    if text=='无新控制':return []
    output=[]
    for step in text.split(';'):
        step=step.strip()
        group=split_top(step[1:-1]) if step.startswith('{') else [step]
        group_id=len(output) if len(group)>1 else None
        for token in group:output.append({'token':token,'concurrentGroup':group_id})
    return output

ENTRIES={
 'res':'Core.cs:SourceAuthority.Reserve','g+':'Native.cs:NativeFile.Open',
 'h+':'JavaHelper.java:main/OPEN','r+':'Native.cs:NetHelper.Run/OPEN',
 'seal':'Core.cs:SourceAuthority.Seal','end':'Core.cs:SourceAuthority.End',
 'cancel':'Core.cs:SourceAuthority.Cancel','cancelO':'Core.cs:SinkAuthority.Abort',
 'ch':'JavaHelper.java:Owned.close','cr':'Native.cs:NetHelper.Run/CLOSE',
 'cg':'Native.cs:NativeFile.Close','retry':'Core.cs:CloseTicket.Attempt',
 'gate':'Core.cs:CompletionGate.Release','retire':'Core.cs:SourceAuthority.Fence',
 'version':'Core.cs:SourceAuthority.Authorize','notice':'Core.cs:SourceAuthority.Notice',
 'grant':'Core.cs:SinkAuthority.Grant','allocA':'Native.cs:NativeFile.Open',
 'dupB':'Native.cs:NativeFile.Dup','sendB':'Native.cs:Mailbox.Send',
 'takeB':'Native.cs:Mailbox.Take','claim':'Core.cs:SinkAuthority.Claim',
 'flushB':'Native.cs:NativeFile.Flush','ca':'Native.cs:NativeFile.Close',
 'cb':'Native.cs:NativeFile.Close','v+':'Core.cs:SinkAuthority.OpenValidation + NativeFile.Open',
 'cv':'Core.cs:SinkAuthority.CloseValidation + NativeFile.Close',
 'takeover':'Core.cs:SinkAuthority.Takeover','ready':'Core.cs:SinkAuthority.Ready',
 'abort':'Core.cs:SinkAuthority.Abort','recoverJournal':'JavaHelper.java:main/RECOVER',
}
def generate():
    r3=ROOT/'docs/coder/D1_R3_BRANCH_MANIFEST_V1.0.md'
    r4=ROOT/'docs/coder/D1_R4_CONTROL_OPERATION_MANIFEST_V1.0.md'
    old={r[0]:r for r in table(r3,9)};rows=[]
    for r in table(r4,6):
        previous=old[r[0]];ops=tokens(r[1]);assert len(ops)==int(r[3])
        for index,op in enumerate(ops,1):
            name=next((x for x in sorted(ENTRIES,key=len,reverse=True) if op['token'].startswith(x)),None);op.update(requestId=f'{r[0]}/n{index:02}',entry=ENTRIES.get(name,'UNSUPPORTED'),binding='PRIMITIVE_ONLY_CONTEXT_NOT_WIRED')
            assert op['entry']!='UNSUPPORTED',op
        i,c=map(int,previous[3].split('/'));g,m,o=map(int,previous[5].split('/'));h,b=map(int,previous[6].split('/'));qr,qn=map(int,r[4].split('/'))
        task=re.search(r'[ST]\d\d',r[1]).group()
        rows.append(dict(id=r[0],task=task,initialAndControls=r[1],operations=ops,nonquery=len(ops),queriesReplay=qr,queriesNew=qn,
            inputBytes=i,inputCalls=c,validationBytes=int(previous[4]),newTargets=g,newRecords=m,outputBytes=o,mediaHandles=h,buffers=b,seconds=int(r[5]),
            ioAndAssertions=r[2],entry='Controller.cs:OperationRouter.Execute',executionStatus='NOT_RUN',implementation='PRIMITIVES_IMPLEMENTED_FULL_SCENARIO_UNWIRED',
            blockers=['No concrete branch context/data-operation placement/IPC persistence transaction driver','No authorization for PF or test_media execution']))
    phases={}
    for prefix,count in [('PF',16),('GC',32)]:
        ids=[]
        for line in r4.read_text(encoding='utf-8').splitlines():
            cells=[x.strip() for x in line.strip('|').split('|')]
            if len(cells)==3 and re.fullmatch(prefix+r'/n\d\d',cells[0]):ids.append({'id':cells[0],'receiverAndCommand':cells[1],'boundedEffects':cells[2],'implementation':'PLANNED_NOT_DISPATCH_WIRED'})
        assert len(ids)==count;phases[prefix]=ids
    caps=dict(control=452,controlHard=544,nonquery=351,query=101,inputBytes=1573522,inputCalls=59,targets=10,records=32,outputBytes=655360,
        validationBytes=262144,filePeakBytes=3178496,fileHardBytes=4194304,metadataWriteBytes='separate-monotonic-counter',seconds=180,osHandles=24,mediaHandles=6,buffers64KiB=8)
    assert len(rows)==61 and sum(r['nonquery'] for r in rows)+48==351
    assert sum(r['queriesReplay']+r['queriesNew'] for r in rows)==101
    assert sum(r['inputBytes'] for r in rows)+32==caps['inputBytes']
    result={'schema':1,'scope':'E1_OFFLINE_TOOL_IMPLEMENTATION','experimentEnabled':False,'inputs':{str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in [r3,r4]},
        'limits':caps,'branches':rows,'phases':phases,'compiler':'existing PowerShell Roslyn / .NET 10 host; no dotnet SDK','missingFullDriver':True}
    out=BASE/'manifest/branches.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'branches':61,'controls':452,'sourceSha256':sha(out),'execution':'NOT_RUN'}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--generate',action='store_true');args=parser.parse_args()
    if args.generate:generate()
    else:print('Explicit --generate required; no execution.')
