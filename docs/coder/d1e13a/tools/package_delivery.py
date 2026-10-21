"""Default/verify/help are strictly read-only. Writing requires the explicit 'pack' subcommand."""
from pathlib import Path
import argparse,hashlib,json,zipfile

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parents[2]
def digest(raw):return hashlib.sha256(raw).hexdigest()
def file_pin(path):
    raw=path.read_bytes();return {'path':path.relative_to(ROOT).as_posix(),'bytes':len(raw),'sha256':digest(raw)}
def verify(expected_seal=None):
    path=BASE/'evidence/e13a-freeze.json'
    if not path.is_file():return {'status':'NOT_FROZEN','mode':'READ_ONLY','writes':0},2
    seal_pin=file_pin(path)
    if expected_seal is not None and seal_pin['sha256']!=expected_seal:raise ValueError('EXTERNAL_SEAL_PIN_MISMATCH')
    seal=json.loads(path.read_text(encoding='utf-8'));rows=seal['immutableFiles'];seen=set()
    for row in rows:
        rel=row['path']
        if rel in seen:raise ValueError('DUPLICATE_IMMUTABLE_PATH')
        seen.add(rel);target=(ROOT/rel).resolve()
        if not target.is_relative_to(ROOT.resolve()):raise ValueError('PIN_PATH_ESCAPE')
        if file_pin(target)!=row:raise ValueError('IMMUTABLE_MISMATCH:'+rel)
    archive=seal['archive'];members={r['path']:r for r in rows if r['path']!=archive['path']}
    with zipfile.ZipFile(ROOT/archive['path']) as z:
        if len(z.namelist())!=len(members) or set(z.namelist())!=set(members):raise ValueError('ZIP_MEMBER_SET')
        for name,row in members.items():
            raw=z.read(name)
            if len(raw)!=row['bytes'] or digest(raw)!=row['sha256']:raise ValueError('ZIP_MEMBER_BYTES:'+name)
    manifest=json.loads((BASE/'evidence/host-jar-manifest.json').read_text(encoding='utf-8'))
    with zipfile.ZipFile(ROOT/manifest['jar']['path']) as z:
        classes=manifest['classes']
        if len(set(z.namelist()))!=len(z.namelist()) or len({r['entry'] for r in classes})!=len(classes) or len(z.namelist())!=len(classes) or set(z.namelist())!={r['entry'] for r in classes}:raise ValueError('JAR_MEMBER_SET')
        for row in classes:
            raw=z.read(row['entry'])
            if len(raw)!=row['bytes'] or digest(raw)!=row['sha256']:raise ValueError('JAR_MEMBER_BYTES')
    inherited=[]
    for original in seal['priorSeals']:
        p=ROOT/original['seal']['path']
        if file_pin(p)!=original['seal']:raise ValueError('OLD_SEAL_CHANGED')
        for row in json.loads(p.read_text(encoding='utf-8'))['immutableFiles']:
            if file_pin(ROOT/row['path'])!=row:raise ValueError('OLD_FROZEN_BYTES_CHANGED:'+row['path'])
        inherited.append(original)
    return {'status':'PASS_E13A_STRICT_READONLY_VERIFY','mode':'READ_ONLY','writes':0,'archive':archive,'externalSeal':seal_pin,'immutableRows':len(rows),'archiveEntries':len(members),'jarClasses':len(manifest['classes']),'priorSeals':inherited,'deviceCalls':0},0

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['verify','pack'],nargs='?',default='verify')
    parser.add_argument('--seal-sha',help='Optional independently supplied external seal SHA256')
    args=parser.parse_args()
    if args.command=='pack':
        if args.seal_sha:parser.error('--seal-sha belongs to verify')
        import runpy
        runpy.run_path(str(Path(__file__).with_name('_write_package.py')),run_name='__main__')
        return
    result,code=verify(args.seal_sha);print(json.dumps(result,ensure_ascii=False));raise SystemExit(code)
if __name__=='__main__':main()
