"""Explicit local APK identity/signing/manifest audit; never installs or starts anything."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parents[2]
JAVA='D:/Android/Android Studio/jbr/bin/java.exe'
SDK=Path('D:/Android/SDK/build-tools/36.0.0')
RESUME=False

def sha(data):return hashlib.sha256(data).hexdigest()
def relative(path):return path.relative_to(ROOT).as_posix()
def command(args,path):
    if path.exists():
        if not RESUME or path.stat().st_size>1048576:raise ValueError('EXISTING_AUDIT_REPORT_NOT_AUTHORIZED')
        return path.read_text(encoding='utf-8-sig')
    with path.open('xb') as output:
        result=subprocess.run(args,stdin=subprocess.DEVNULL,stdout=output,stderr=subprocess.STDOUT,check=False)
    if result.returncode or path.stat().st_size>1048576:raise ValueError('E4_LOCAL_APK_AUDIT_FAILED:'+path.name)
    return path.read_text(encoding='utf-8-sig')

def audit():
    if (BASE/'evidence/e5-freeze.json').exists():raise ValueError('FROZEN_READ_ONLY')
    snapshot=json.loads((BASE/'evidence/final-build-inputs.json').read_text(encoding='utf-8'))
    for row in snapshot['files']:
        raw=(ROOT/row['path']).read_bytes()
        if len(raw)!=row['bytes'] or sha(raw)!=row['sha256']:raise ValueError('SOURCE_CHANGED_AFTER_FINAL_BUILD:'+row['path'])
    artifacts=BASE/'artifacts/D1-20261017-E5/final';artifacts.mkdir(parents=True,exist_ok=True)
    apks=[];certificate=None;commands=[]
    for role,source,name in [('app-debug',BASE/'app/build/outputs/apk/debug/app-debug.apk','app-debug.apk'),
                             ('androidTest',BASE/'app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk','app-debug-androidTest.apk')]:
        raw=source.read_bytes();target=artifacts/name
        if target.exists():
            if not RESUME or target.read_bytes()!=raw:raise ValueError('EXISTING_ARTIFACT_DIFFERS_FROM_FINAL_BUILD')
        else:
            with target.open('xb') as stream:stream.write(raw)
        report=BASE/('evidence/'+role+'-signing.txt')
        args=[JAVA,'-jar',str(SDK/'lib/apksigner.jar'),'verify','--verbose','--print-certs',str(target)]
        signing=command(args,report);commands.append(dict(argv=args,exitCode=0,log=relative(report)))
        matches=re.findall(r'certificate SHA-256 digest:\s*([0-9a-fA-F]{64})',signing)
        if len(matches)!=1:raise ValueError('EXACT_ONE_SIGNER_REQUIRED')
        current=matches[0].lower()
        if current!="5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f":raise ValueError("ORIGINAL_CERTIFICATE_CHANGED")
        if certificate is not None and current!=certificate:raise ValueError('APP_TEST_SIGNER_MISMATCH')
        certificate=current
        badging_path=BASE/('evidence/'+role+'-badging.txt')
        badging_args=[str(SDK/'aapt2.exe'),'dump','badging',str(target)]
        badging=command(badging_args,badging_path);commands.append(dict(argv=badging_args,exitCode=0,log=relative(badging_path)))
        package=re.search(r"package: name='([^']+)'",badging).group(1)
        expected='com.videokit.app' if role=='app-debug' else 'com.videokit.app.test'
        if package!=expected:raise ValueError('APPLICATION_ID_CHANGED')
        apks.append(dict(role=role,path=relative(target),bytes=len(raw),sha256=sha(raw),
                         applicationId=package,signerCertificateSha256=certificate,signingVerified=True,signingReport=relative(report)))
    app=next(item for item in apks if item['role']=='app-debug')
    manifest_path=BASE/'evidence/app-manifest-xmltree.txt'
    args=[str(SDK/'aapt2.exe'),'dump','xmltree','--file','AndroidManifest.xml',str(ROOT/app['path'])]
    manifest=command(args,manifest_path);commands.append(dict(argv=args,exitCode=0,log=relative(manifest_path)))
    expected_services={'com.videokit.spike.e4.E4CodecService':(':e4_codec',False),
                       'com.videokit.spike.c14.CpuIsolatedService':(':d1_cpu_worker',True)}
    services=[]
    for part in re.split(r'(?m)^\s*E: service\b',manifest)[1:]:
        part=part.split('\n      E:',1)[0]
        names=[name for name in expected_services if name in part]
        if len(names)!=1:raise ValueError('UNEXPECTED_SERVICE')
        name=names[0];process,isolated=expected_services[name]
        if process not in part or not re.search(r'android:exported[^\n]*(?:=false\b|0x0\b)',part):raise ValueError('SERVICE_EXPORTED_OR_PROCESS')
        actual=bool(re.search(r'android:isolatedProcess[^\n]*(?:=true\b|0xffffffff)',part))
        if actual!=isolated:raise ValueError('SERVICE_ISOLATION_MANIFEST')
        services.append(dict(name=name,process=process,exported=False,isolatedProcess=actual))
    if len(services)!=2 or 'com.videokit.worker' in manifest or 'android.permission.INTERNET' in manifest:raise ValueError('NOT_SINGLE_APK_FINITE_MANIFEST')
    native=[]
    with zipfile.ZipFile(ROOT/app['path']) as archive:
        entries=sorted(name for name in archive.namelist() if name.startswith('lib/') and name.endswith('.so'))
        if len(entries)!=7:raise ValueError('NATIVE_LIBRARY_COUNT_CHANGED')
        for entry in entries:
            raw=archive.read(entry);upstream=BASE/'upstream-c14/native-libs'/Path(entry).relative_to('lib')
            if raw!=upstream.read_bytes():raise ValueError('NATIVE_LIBRARY_CHANGED:'+entry)
            native.append(dict(apkPath=app['path'],entry=entry,bytes=len(raw),sha256=sha(raw),upstreamPath=relative(upstream)))
    value=dict(schema=1,status='PASS',apks=apks,nativeLibraries=native,singleApk=True,services=services,
               commands=commands,manifestReport=relative(manifest_path),finalBuildInputsVerified=True,
               signingKeysIncluded=False,androidExecution='NOT_RUN',deviceCalls=0,nativeFaultExecution='NOT_RUN',
               resumedManifestParser=RESUME,declaredPermissions=re.findall(r'Raw: "(android\.permission\.[A-Z_]+)"',manifest))
    with (BASE/'evidence/apk-audit.json').open('x',encoding='utf-8') as stream:json.dump(value,stream,indent=2)
    print(json.dumps(dict(status='PASS',apks=apks,services=services,nativeLibraries=len(native)),sort_keys=True))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--audit',action='store_true');parser.add_argument('--resume-owned',action='store_true');options=parser.parse_args();RESUME=options.resume_owned
    if options.audit:audit()
    else:print('{"status":"INSPECT","deviceCalls":0}')
