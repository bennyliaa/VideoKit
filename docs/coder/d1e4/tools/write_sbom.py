"""Offline metadata-only SBOM/delta. No resolver, download, media or native execution."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import zipfile

BASE=Path(__file__).resolve().parents[1]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def locks(raw):
    result={}
    for line in raw.decode('utf-8').splitlines():
        if line.startswith('#') or '=' not in line:continue
        coordinate,scopes=line.split('=',1)
        if coordinate.count(':')==2:result[coordinate]=scopes.split(',')
    return result
def write():
    if (BASE/'evidence/e4-freeze.json').exists():raise ValueError('FROZEN_READ_ONLY')
    current_raw=(BASE/'app/gradle.lockfile').read_bytes();current=locks(current_raw)
    with zipfile.ZipFile(BASE/'upstream-c14/D1-20261016-C14-source.zip') as archive:old_raw=archive.read('app/gradle.lockfile')
    old=locks(old_raw);old_ga={':'.join(coordinate.split(':')[:2]) for coordinate in old}
    new_ga={':'.join(coordinate.split(':')[:2]) for coordinate in current}
    if not new_ga<=old_ga:raise ValueError('NEW_THIRD_PARTY_PACKAGE_REQUIRES_REVIEW:'+str(sorted(new_ga-old_ga)))
    inherited=json.loads((BASE/'upstream-c14/c14-sbom.cdx.json').read_text(encoding='utf-8'))
    components=copy.deepcopy(inherited['components'])
    cache=Path('C:/Users/benny/.gradle/caches/modules-2/files-2.1')
    cache_bytes=0;cache_files=0
    for coordinate,scopes in sorted(current.items()):
        group,name,version=coordinate.split(':');hashes=[];artifacts=[]
        folder=cache/group/name/version
        for path in sorted(folder.rglob('*')) if folder.exists() else []:
            if not path.is_file() or path.suffix not in ('.jar','.aar','.pom'):continue
            if path.name.endswith(('-sources.jar','-javadoc.jar')):continue
            raw=path.read_bytes();cache_bytes+=len(raw);cache_files+=1
            if cache_bytes>134217728 or cache_files>512:raise ValueError('CACHED_ARTIFACT_METADATA_HASH_CAP')
            artifacts.append(dict(name=path.name,bytes=len(raw),sha256=sha(raw),cacheRelative=path.relative_to(cache).as_posix()))
            if path.suffix in ('.jar','.aar'):hashes.append(dict(alg='SHA-256',content=sha(raw)))
        component=dict(type='library',group=group,name=name,version=version,purl='pkg:maven/'+group+'/'+name+'@'+version,
                       properties=[dict(name='gradleConfigurations',value=','.join(scopes)),
                                   dict(name='scope',value='debug app runtime' if 'debugRuntimeClasspath' in scopes else 'instrumentation/compile only'),
                                   dict(name='source',value='Existing local Maven cache; no download; prior C14 package family')])
        if hashes:component['hashes']=hashes
        if group.startswith('androidx.') or group in ('com.google.guava','com.google.errorprone','com.google.code.findbugs'):
            component['licenses']=[dict(expression='Apache-2.0')]
        component['properties'].append(dict(name='cachedArtifactEvidence',value=json.dumps(artifacts,sort_keys=True,separators=(',',':'))))
        components.append(component)
    old_versions={ga:sorted(coordinate.split(':')[2] for coordinate in old if coordinate.startswith(ga+':')) for ga in old_ga}
    current_versions={ga:sorted(coordinate.split(':')[2] for coordinate in current if coordinate.startswith(ga+':')) for ga in new_ga}
    changed={ga:dict(previous=old_versions[ga],current=current_versions[ga]) for ga in sorted(new_ga) if old_versions[ga]!=current_versions[ga]}
    delta=dict(schema=1,scope='E4_EXACT_LOCK_AND_NATIVE_DIFF_NOT_VULNERABILITY_CLEARANCE',
               originalC14LockSha256=sha(old_raw),currentLockSha256=sha(current_raw),currentCoordinates=len(current),
               addedPackageFamilies=sorted(new_ga-old_ga),removedPackageFamilies=sorted(old_ga-new_ga),selectedVersionDifferences=changed,
               nativeLibraries='Same seven actual APK native members, byte-identical to C14; see apk-audit.json',
               ffmpeg='8.0.3 unchanged allowlist/quota/network-disabled configuration; no native rebuild',
               media3='1.9.3 muxer/common/container only; no new package family; ExoPlayer/Transformer/UI/Compose omitted from E4',
               offlineAlignment='Cached C14 kotlin-stdlib2.2.10 and coroutines-core1.9.0; missing1.8.1 artifact was not downloaded',
               originalRuntimeGraphClaim='Not identical: selected transitive compile/instrumentation versions differ in the reduced project; all differences listed',
               cachedArtifactsRead=dict(bytes=cache_bytes,files=cache_files,byteCap=134217728,fileCap=512),
               safetyAndDistribution='No new SCA/license acceptance claim. Original P0, tool restrictions and release/distribution review remain open.')
    bom=dict(bomFormat='CycloneDX',specVersion='1.6',version=1,
             metadata=dict(component=dict(type='application',name='VideoKit E4 single-APK Debug prototype',version='D1-20261017-E4')),
             components=components,properties=[dict(name='scope',value='Local-only Debug prototype; no production release or Android device acceptance'),
                                              dict(name='correspondingNativeSource',value='upstream-c14/D1-20261016-C14-source.zip retains full original signed source/configuration/license maps'),
                                              dict(name='licenseGate',value='Inherited NOTICE and native license evidence retained; incomplete Maven license declarations are not license clearance')])
    for filename,value in [('sbom.json',bom),('sbom-difference.json',delta)]:
        with (BASE/'evidence'/filename).open('x',encoding='utf-8') as stream:json.dump(value,stream,indent=2)
    print(json.dumps(dict(currentCoordinates=len(current),addedPackageFamilies=delta['addedPackageFamilies'],versionDifferences=len(changed),cachedArtifactBytes=cache_bytes),sort_keys=True))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');options=parser.parse_args()
    if options.write:write()
    else:print('{"status":"INSPECT","downloads":0}')
