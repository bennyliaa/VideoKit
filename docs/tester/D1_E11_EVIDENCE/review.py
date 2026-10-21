"""Independent E11 final R1 static/evidence review; no candidate code execution or device calls."""
import base64,datetime,hashlib,io,json,pathlib,re,struct,zipfile
R=pathlib.Path(__file__).resolve().parents[3];B=R/'docs/coder/d1e11';F=B/'revision-r1';OUT=pathlib.Path(__file__).parent
INPUTS={};CHECKS=[]
def require(v,m):
 if not v:raise ValueError(m)
def sha(b):return hashlib.sha256(b).hexdigest()
def label(p):return p.relative_to(R).as_posix() if p.is_relative_to(R) else p.as_posix()
def data(p):
 p=pathlib.Path(p);require(p.is_file() and not p.is_symlink() and p.stat().st_size<=96*1024*1024,'FILE_ROLE_BOUND:'+str(p));b=p.read_bytes();INPUTS[label(p)]=dict(path=label(p),bytes=len(b),sha256=sha(b));return b
def pin(p):
 p=pathlib.Path(p);b=data(p);return dict(path=label(p),bytes=len(b),sha256=sha(b))
def read(p):return json.loads(data(p))
def verify(row):
 p=pathlib.Path(row['path']);p=p if p.is_absolute() else R/p;b=data(p);require(len(b)==row['bytes'] and sha(b)==row['sha256'],'PIN_MISMATCH:'+row['path']);return p
def output(name,v):
 with (OUT/name).open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def ok(name,details):CHECKS.append(dict(check=name,status='PASS_STATIC_OR_EXISTING_EVIDENCE',details=details))
def wire(f):return ('{"e9":1,"fields":'+json.dumps(f,sort_keys=True,separators=(',',':'))+'}\n').encode('ascii')
def record(b):
 j=json.loads(b);require(set(j)=={'e9','fields'} and type(j['e9']) is int and j['e9']==1 and wire(j['fields'])==b,'ORIGINAL_CANONICAL');return j['fields']
def unpack(s):return base64.urlsafe_b64decode(s+'='*((-len(s))%4))
def seal(p,expected):
 require(pin(p)['sha256']==expected,'EXPECTED_SEAL');s=read(p)
 for x in s['immutableFiles']:verify(x)
 archive=verify(s['archive']);expectedRows={x['path']:x for x in s['immutableFiles'] if x['path']!=s['archive']['path']}
 with zipfile.ZipFile(io.BytesIO(data(archive))) as z:
  require(len(z.namelist())==len(set(z.namelist())) and set(z.namelist())==set(expectedRows),'ZIP_INVENTORY')
  for name,row in expectedRows.items():b=z.read(name);require(len(b)==row['bytes'] and sha(b)==row['sha256'],'ZIP_BYTES:'+name)
 return s
def source(p):return data(p).decode('utf-8-sig')
def contains(p,parts):
 s=source(p)
 for x in parts:require(x in s,'SOURCE_REQUIRED:'+str(p)+':'+x)
 return s
def v2_cert(b):
 e=b.rfind(b'PK\x05\x06');require(e>=0,'APK_EOCD');cd=struct.unpack_from('<I',b,e+16)[0];require(b[cd-16:cd]==b'APK Sig Block 42','APK_SIG_BLOCK');size=struct.unpack_from('<Q',b,cd-24)[0];start=cd-size-8;require(struct.unpack_from('<Q',b,start)[0]==size,'APK_BLOCK_SIZES');pos=start+8;v2=None
 while pos<cd-24:
  n=struct.unpack_from('<Q',b,pos)[0];kind=struct.unpack_from('<I',b,pos+8)[0]
  if kind==0x7109871a:v2=b[pos+12:pos+8+n]
  pos+=8+n
 require(v2 is not None,'APK_V2_PRESENT')
 def lp(blob,n=0):k=struct.unpack_from('<I',blob,n)[0];return blob[n+4:n+4+k],n+4+k
 signers,_=lp(v2);signer,_=lp(signers);signed,_=lp(signer);digests,at=lp(signed);certs,_=lp(signed,at);cert,_=lp(certs);return sha(cert)
def main():
 final=seal(F/'evidence/e11-final-freeze.json','2e1dcdcf212131952529e998da0f0cd1c14e10ca3eee912d1f897181b7cf81d3');base=seal(B/'evidence/e11-freeze.json','fd71fd2f3e696a144befb84307391f5f11c6b966dc068063d409c7df95f3eaa5');require(len(final['immutableFiles'])==65 and len(base['immutableFiles'])==375,'FINAL_BASE_COUNTS');verify(final['baseSeal']);require(final['archive']['sha256']=='0fdc6d9439d48819608d83fd46234f27846ac852d726a614dbeec3103d22fafc','EXACT_FINAL_ARCHIVE')
 oldseal=read(R/'docs/coder/d1e10a/evidence/e10a-freeze.json');require(pin(R/'docs/coder/d1e10a/evidence/e10a-freeze.json')['sha256']=='0a2d1c3a6c02f6194427ca93688a804f7df8d7966ffedb1ee0324cbccaf7d090','OLD_ACCEPTED_SEAL')
 for x in oldseal['immutableFiles']:verify(x)
 require(len(oldseal['immutableFiles'])==463,'OLD463')
 for x in ['DELIVERY','ARCHITECTURE_AND_THREAT_BOUNDARY','REMAINING_GATE_REVIEW','DEVICE_EXECUTION_APPENDIX']:
  data(B.parent/('D1_E11_'+x+'_V1.0.md'));data(B.parent/('D1_E11_R1_'+x+'_V1.0.md'))
 handoff=pin(B.parent/'D1_E11_HANDOFF_REPORT_V1.0.md');ok('full_package_freezes_and_overrides',dict(finalImmutable=65,baseImmutable=375,oldE10AImmutable=463,zipDiskBytesMatched=True,handoff=handoff,finalHostOverride='revision-r1/e11-host-tools-final.jar',candidateExecuted=False))
 provenance=read(B/'evidence/catalog-source-provenance.json');verify(provenance['acceptedFinalReview']);require(provenance['acceptedFinalReview']['sha256']=='a597bca5c392aaf142f1fa5e74ab4a1aa869fb3cdc367df5005af54e335feaff','ACCEPTED_FINAL_REVIEW');verify(provenance['reviewManifest']);priorManifest=read(R/provenance['reviewManifest']['path']);excluded=[]
 for row in priorManifest['files']:
  if row['path']==provenance['reviewManifest']['path']:
   require(row['bytes']==0 and row['sha256']==sha(b'') and 'self' in str(priorManifest['excludes']),'DECLARED_HISTORICAL_SELF_PLACEHOLDER');excluded.append(row)
  else:verify(row)
 pins=read(R/'docs/tester/D1_E10A_FINAL_READONLY_REVIEW_EVIDENCE/input-pins.json');require(len(pins['allActuallyReadLocalFiles'])==688,'ACCEPTED_688_INPUTS')
 for row in pins['allActuallyReadLocalFiles']:verify(row)
 oldmanifest=read(R/'docs/tester/D1_E10A_EXECUTION/4f21f71a-bf66-4a44-a287-320f0ae25fde/evidence/evidence-manifest.json')
 for row in oldmanifest['files']:verify(row)
 mapping=provenance['registrySnapshotMapping'];require(len(mapping)==13,'ORIGINAL_13_REGISTRY_FILES')
 for row in mapping:require(data(verify(row['original']))==data(verify(row['snapshot'])),'ORIGINAL_SNAPSHOT_MATCH')
 g=R/'docs/tester/D1_E10A_EXECUTION/4f21f71a-bf66-4a44-a287-320f0ae25fde/registry';catraw=data(g/'final.acceptance.json');cat=record(catraw);head=sha(data(g/'descriptor.json'));events=[]
 for n,b in enumerate(data(g/'registry.events.jsonl').splitlines(keepends=True),1):
  ev=record(b);require(ev['seq']==str(n) and ev['parent']==head and ev['evidence']==sha(data(g/ev['path'])) and ev['path'] not in ['final.acceptance.json','registry.checkpoint.json','final.seal.json'],'OLD_FINAL_DAG');head=sha(b);events.append(ev['state'])
 require(len(catraw)==5853 and sha(catraw)=='27fe90573f2d8a3a750c270e760f4e19e797fe188287ade5c58268e8c6d911b7' and head==cat['head']=='6ce0f654a5bec6527a6773b141f64e49e858d3ef2e51c8c2e52360fd9ce0a4e5' and events==['BOUND','RETURN_OBSERVED','NORMAL_FINISH_CONFIRMED','FINAL_ACCEPTED'],'ACCEPTED_REAL_CATALOG');require(cat['actorCount']=='1' and cat['disposition1']=='RETURN_VERIFIED_IN_TIME' and cat['environment']=='DEVICE_HA1Q6WXR','CATALOG_TYPE_AND_SCOPE')
 for key,file in [('actor1','../evidence/commit-original-actor.json'),('reserve1','actors/0001/reserve.json'),('returned1','actors/0001/returned.json'),('finish1','actors/0001/finish.json')]:require(unpack(cat[key])==data(g/file),'CATALOG_EMBEDDED_ORIGINAL')
 checkraw=data(g/'registry.checkpoint.json');check=record(checkraw);sealraw=data(g/'final.seal.json');sf=record(sealraw);require(check['head']==sf['head']==head and check['catalog']==sf['catalog']==sha(catraw) and sf['checkpoint']==sha(checkraw),'CHECKPOINT_SEAL')
 require(read(B/'evidence/export-results.json')['exitCode']==0 and read(B/'evidence/export-results.json')['originalRegistryUnchanged'],'ORIGINAL_READONLY_EXPORT_RECEIPT');data(B/'evidence/export.stdout.txt');data(B/'evidence/export.stderr.txt');ok('actual_catalog_source_and_readonly_export',dict(catalogBytes=5853,catalogSha256=sha(catraw),head=head,originalRegistryFiles=13,originalSnapshotAllMatched=True,acceptedInputsVerified=688,executionManifestVerified=len(oldmanifest['files']),historicalManifestSelfPlaceholderExcluded=excluded,oldAuthorizationIsNotNewDeployment=True,newCatalogGenerated=False))
 policy=source(B/'src/com/videokit/spike/e4/E9BuildPolicy.java');packed=re.search(r'CATALOG_BASE64="([A-Za-z0-9_-]+)"',policy).group(1);require(unpack(packed)==catraw and 'ROLE="ACTIVATION"' in policy and 'GATE_ABI=1' in policy,'SOURCE_PINNED_ACTIVATION_POLICY')
 inputs=read(B/'evidence/final-build-inputs.json');require(len(inputs['files'])==166 and pin(B/'evidence/final-build-inputs.json')['sha256']=='c136acbd8730cdbb545c960e55234f66bc5d5310fcaca6cb850c669756c8de9e','EXACT166_BUILD_INPUTS')
 for row in inputs['files']:verify(row)
 builds=read(B/'evidence/build-results.json');require(len(builds['attempts'])==1 and builds['attempts'][0]['exitCode']==0 and builds['attempts'][0]['offline'] and builds['attempts'][0]['inputSnapshotSha256']==pin(B/'evidence/final-build-inputs.json')['sha256'],'ONE_OFFLINE_BUILD');require('BUILD SUCCESSFUL' in source(R/builds['attempts'][0]['log']),'ORIGINAL_BUILD_LOG')
 apk=read(B/'evidence/apk-audit.json');actual=[];signer='5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f'
 for row in apk['apks']:
  p=verify({k:row[k] for k in ['path','bytes','sha256']});b=data(p);require(v2_cert(b)==signer,'DIRECT_APK_V2_CERTIFICATE_DIGEST');log=source(R/row['signingReport']);require('Verified using v2 scheme (APK Signature Scheme v2): true' in log and signer in log,'ORIGINAL_SIGNATURE_VERIFICATION_LOG');actual.append(pin(p))
  if row['role']=='app-debug':
   with zipfile.ZipFile(io.BytesIO(b)) as z:
    dex=[z.read(n) for n in z.namelist() if re.fullmatch(r'classes[0-9]*\.dex',n)];require(any(packed.encode() in raw for raw in dex),'APK_DEX_ORIGINAL_CATALOG_LITERAL');libs=[n for n in z.namelist() if n.endswith('.so')];require(len(libs)==7,'SEVEN_NATIVE_APK_ENTRIES')
    for n in apk['nativeLibraries']:require(sha(z.read(n['entry']))==n['sha256'] and data(R/n['upstreamPath'])==z.read(n['entry']),'APK_NATIVE_ORIGINAL_BYTES')
 require([x['sha256'] for x in actual]==['2f323c16e896b0535e80cccce05bbcf3051224f0add279a51392312083e89f48','e644dce77be6ccb0e7f99d82f2479fc92238aad682bb022bb95835fc015d0bfb'],'EXACT_FINAL_APKS');badging=source(B/'evidence/app-debug-badging.txt');require("versionCode='15'" in badging and "versionName='D1-E11-ACTIVATION'" in badging,'APK_VERSION_BADGING');testmanifest=source(B/'evidence/test-manifest-xmltree.txt');require('E11ActivationInstrumentation' in testmanifest and 'E9MigrationInstrumentation' not in testmanifest,'NEW_TEST_MANIFEST_RUNNER_ONLY')
 lock=data(B/'app/gradle.lockfile');require(lock==data(R/'docs/coder/d1e10a/app/gradle.lockfile') and len([x for x in lock.decode().splitlines() if x and not x.startswith('#') and not x.startswith('empty=')])==35,'UNCHANGED35_LOCKED_COORDINATES')
 inherited=read(B/'evidence/native-and-strict-logic-inheritance.json')
 for pair in inherited['exactUnchanged']:require(data(verify(pair['current']))==data(verify(pair['baseline'])),'STRICT_FRAMEWORK_NATIVE_UNCHANGED')
 ok('built_APK_catalog_and_inheritance',dict(actualApks=actual,version=15,role='ACTIVATION',abi=1,builds=1,buildInputs=166,inputSnapshotSha256=pin(B/'evidence/final-build-inputs.json')['sha256'],certificateDigestDirectlyParsed=signer,cryptographicSigningVerification='Original pinned apksigner receipt; no signing tool rerun',native=7,maven=35,strictSixFramesEof1000us='UNCHANGED',licenseClearance=False,deviceRun=False))
 host=read(F/'evidence/host-revision-results.json');baseJar=verify(host['baseJar']);finalJar=verify(host['artifact']);require(pin(finalJar)['sha256']=='adb7b384ed305c925be7b2a670f33063e8d4309e085f1a6b7950f4b7125ebc27','EXACT_FINAL_JAR');changed=[];added=[]
 with zipfile.ZipFile(io.BytesIO(data(baseJar))) as old,zipfile.ZipFile(io.BytesIO(data(finalJar))) as new:
  oldNames=set(old.namelist());newNames=set(new.namelist());require(len(oldNames)==160 and len(newNames)==163 and not any(n.split('/')[-1].startswith(('OnceCheck','E11ProductionCheck','E11PublicEntryCheck')) for n in newNames),'PRODUCTION_JAR_CLASS_INVENTORY')
  for n in newNames:
   if n not in oldNames:added.append(n)
   elif old.read(n)!=new.read(n):changed.append(n)
  require(changed==['com/videokit/spike/e4/E9HostActivationSession.class'] and set(added)=={'com/videokit/spike/e4/E11DeploymentOnce.class','com/videokit/spike/e4/E11DeploymentOnce$IO.class','com/videokit/spike/e4/E11DeploymentOnce$Cut.class'},'EXACT_R1_CLASS_OVERRIDE')
  for n in changed+added:require(new.read(n)==data(F/'.classes'/n),'R1_JAR_ACTUAL_COMPILED_CLASS')
  for row in host['entries']:require(sha(new.read(row['entry']))==row['sha256'],'R1_JAR_ENTRY_PROVENANCE')
 binding=read(F/'release/candidate-binding-final.json');require(binding['hostJar']==pin(finalJar) and binding['requiredDeploymentConfigField']=='dispatchRecord' and all(binding[k] is None for k in ['sourceReview','deploymentDispatch','liveCurrentObservation','normalMp4Receipt','normalAviReceipt','approvedRelease']),'FINAL_BINDING_DRAFT_NO_AUTHORITY');template=read(F/'release/activation-trust-deploy.template.json');require(template['templateOnly'] and template['state']=='NOT_APPROVED_NOT_EXECUTABLE' and template['wireFields']['dispatchRecord'].endswith('/activation-deployment.once'),'NEW_DEPLOY_CONFIG_TEMPLATE')
 ok('final_R1_JAR_and_draft_bindings',dict(productionClasses=163,unchangedClasses=159,replaced=changed,added=sorted(added),jar=pin(finalJar),allCurrentAndroidInputsUnchanged=True,actualReleaseIssued=False,oldBaseJarNotDeploymentTool=True))
 once=contains(F/'tools/E11DeploymentOnce.java',['supervisor.retainAuthority(this,null,this::returned)','StandardOpenOption.CREATE_NEW','LinkOption.NOFOLLOW_LINKS','channel.force(true)','E11_ONCE_READBACK','if(!returned())','FileAlreadyExistsException knownRace','io.knownNoOpen=true','if(attempted)','activation-deployment.once','Files.isSymbolicLink(p)']);require(once.index('supervisor.retainAuthority(')<once.index('FileChannel.open(') and once.index('channel.force(true)')<once.index('if(!returned())'),'ONCE_IO_ORDER')
 entry=contains(F/'tools/E9HostActivationSession.java',['config.exact("kind","plan","planSha","authorization","review","registryPath","head","dispatchRecord")','Paths.get(config.get("dispatchRecord")).isAbsolute()','oncePath.startsWith(originalRoot)','once.record(','RESERVED_OUTCOME_NOT_ASSUMED','deployActivationDetached(']);require(entry.index('once.record(')<entry.index('E9HostDeployment.Processes processes='),'ONCE_BEFORE_INSTALLER');require('recordActivationRelease(' not in entry and 'sealFinal(' not in entry,'NO_ORIGINAL_REGISTRY_MUTATION_DEPLOY')
 htests=host['tests'];require(host['javaFixtureInvocations']==8 and htests['serial'][0]['simulatedDispatches']==1 and htests['serial'][1]['simulatedDispatches']==0 and sum(x['simulatedDispatches'] for x in htests['concurrent'])==1 and all(x['simulatedDispatches']==0 for x in htests['forceFailure']) and htests['unknown'][0]['originalReturned'] is False and htests['unknown'][0]['productionExitAllowed'] is False and htests['unknown'][1]['simulatedDispatches']==0,'R1_EIGHT_EXISTING_FIXTURE_RESULTS')
 for command in host['commands']:
  label_=command['label'];read(F/'evidence/checks'/(label_+'.command.json'));data(F/'evidence/checks'/(label_+'.stdout.txt'));data(F/'evidence/checks'/(label_+'.stderr.txt'));rawResult=read(F/'evidence/checks'/(label_+'.result.json'))
  mapped={'serial-first':htests['serial'][0],'serial-replay-new-jvm':htests['serial'][1],'race-0':htests['concurrent'][0],'race-1':htests['concurrent'][1],'force-failed':htests['forceFailure'][0],'force-replay':htests['forceFailure'][1],'close-unknown':htests['unknown'][0],'unknown-replay-new-jvm':htests['unknown'][1]};require(rawResult==mapped[label_],'R1_RAW_RESULT_SUMMARY_MATCH')
 teardown=read(F/'evidence/checks/unknown-fixture-teardown.json');require(teardown['originalCloseAck'] is False and teardown['productionExitAllowed'] is False,'UNKNOWN_FIXTURE_TERMINATION_NOT_ACK');ok('persistent_once_boundary_and_existing_R1_checks',dict(existingJvmInvocations=8,onlyOneConcurrentRecord=True,knownForceFailureReturnedNoInstall=True,unknownCloseRetainsCustodianNoInstall=True,recordBeforeInstall=True,recordPathBoundByConfig=True,parentPreexistsAndNoSymlink=True,originalRegistryReadonly=True,markerIsNotSuccessOrApproval=True,fixtureTerminationIsNotCloseAck=True,actualInstallerOrDeviceTest='NOT_RUN'))
 observer=contains(B/'src/com/videokit/spike/e4/E9CurrentObservation.java',['E5AAdmission.beginCurrentObservation()','platform.requireIdleOriginalHost()','E9LegacyState.lockOriginalGuards(files)','E9LegacyState.openAndValidate(files,true)','E9_CURRENT_ACTOR_CHANGED','E9LegacyState.ledger(files.read(ledger,131072))','files.closeReturnedResources()','if(files.returned())','ACTIVE.remove(this)','E5AAdmission.fromCurrentObservation(this,observationEpoch)']);require(observer.index('E5AAdmission.beginCurrentObservation()')<observer.index('synchronized(E9CurrentObservation.class)'),'EPOCH_INVALIDATION_BEFORE_CLASS_LOCK');require(observer.index('files.closeReturnedResources()')<observer.index('ACTIVE.remove(this)')<observer.index('E5AAdmission.fromCurrentObservation('),'GRANT_ONLY_AFTER_OWN_RETURN')
 contains(B/'src/com/videokit/spike/e4/E9Phase.java',['E9BuildPolicy.role().equals("ACTIVATION")','E9Catalog.fromTrustedRelease(raw,digest,environment)','E11_RELEASE_HEAD_BINDING','E9_MUTATING_ENTRY_DISABLED','E5AAdmission.requireCurrent()']);contains(B/'android/com/videokit/spike/e4/E9Runtime.java',['E5AAdmission.invalidateCurrent()','new E9CurrentObservation(','E9Phase.catalog()']);contains(B/'android/com/videokit/spike/e4/E11ActivationLifetime.java',['E9CurrentObservation.retained()==0','E4Session.retainedSessions()==0','E4Session.reservedEncoderSlots()==0','E5N2Recovery.retainedOperations()==0','E5AFinalObservation.retained()==0']);runner=contains(B/'app/src/androidTest/java/com/videokit/spike/e4/E11ActivationInstrumentation.java',['E11Selection.require(selected);super.onCreate(args)','E5AAdmission.invalidateCurrent()','if(!E11ActivationLifetime.canFinish())','super.finish(code,result)','PENDING_EXCEPTION_ORIGINAL_OWNERS_NO_FINISH']);require(runner.index('E5AAdmission.invalidateCurrent()')<runner.index('super.finish(code,result)'),'FINISH_INVALIDATES_FIRST')
 selection=contains(B/'src/com/videokit/spike/e4/E11Selection.java',['Set.of(MP4,AVI,CAPABILITY,CANCEL)','E11_TWO_DISTINCT_NORMAL_REPORTS','E11_CURRENT_NORMAL_RECEIPT_INDEX','E11_FIRST_NORMAL_NO_PRIOR_RECEIPTS','E11_AVI_ONLY_AFTER_MP4','r.get("scope").equals(value(args,"e11ScopeSha256"))','r.get("fullEof").equals("true")','r.get("ptsUs").equals("1000")','r.get("ownersReturned").equals("true")']);require('E5AAdmission.fromCurrentObservation' not in selection,'SELECTOR_DOES_NOT_GRANT');tests=source(B/'app/src/androidTest/java/com/videokit/spike/e4/E4DeviceTests.java');require('E9Runtime.observe' in tests and '@Before' in tests,'ACTUAL_TEST_CURRENT_OBSERVATION');ok('live_proof_selection_and_finish_static_boundary',dict(guardFenceAndFullLedgerRequired=True,ownOriginalReturnsBeforeEpochGrant=True,knownFailureReturnedRetiresWithoutGrant=True,unknownRetained=True,repeatedOrConcurrentObservationRevokes=True,exactMethods=4,normalReceiptSyntaxAndOrderOnly=True,externalReportAuthorityStillRequired=True,runnerUnknownBlocksPlatformFinish=True,AndroidExecution='NOT_RUN'))
 results=read(B/'evidence/targeted-check-results.json');require(results['groups']==12 and results['finalMappedAssertions']==154 and results['totalValidationInvocations']==13 and len(results['allInvocations'])==13,'TARGETED_COUNT')
 for row in results['allInvocations']:
  stdout=source(verify(row['stdout']));verify(row['stderr']);require('assertions='+str(row['assertions']) in stdout and 'PASS' in stdout,'TARGETED_RAW_LOG')
 require(sum(row['assertions'] for row in results['results'])==154,'MAPPED154_NOT_ALLRUN_SUM');sdk=read(B/'evidence/public-android-entry-check.json')
 for row in sdk['inputs']:verify(row)
 sdklog=source(B/'evidence/sdk-public/actual-public.stdout.txt');require('PASS SDK_PUBLIC assertions=14' in sdklog and 'AndroidRuntime=NOT_RUN' in sdklog,'SDK14_SCOPE');data(B/'evidence/sdk-public/actual-public.stderr.txt')
 ok('finite_existing_tests_and_coverage_limits',dict(groups=12,finalMappedAssertions=154,validationInvocations=13,sdkPublicAssertions=14,R1CrossJvmInvocations=8,candidateTestsRerun=0,platform='Windows UID/inode/fsync/deployment substitutes and SDK stubs',unknownCleanupNotOriginalAck=True,runnerFinishAndroidAndNativeFaults='NOT_RUN'))
 output('input-pins.json',dict(at=datetime.datetime.now().astimezone().isoformat(),files=list(INPUTS.values()),reviewScript=pin(__file__),requirements=pin(R/'docs/milestones/D1_E11_TESTER_REQUIREMENTS_V1.0.md'),newDeviceCalls=0,newBuilds=0,newCandidateTestRuns=0))
 output('independent-review-audit.json',dict(status='PASS_STATIC_LOCAL_FINAL_R1_CANDIDATE_REVIEW',at=datetime.datetime.now().astimezone().isoformat(),checks=CHECKS,inputFiles=len(INPUTS),finalSeal=pin(F/'evidence/e11-final-freeze.json'),finalArchive=final['archive'],readyForSeparateExplicitDeviceDispatchConsideration=True,deviceDeploymentAuthorized=False,newReleaseIssued=False,normalReceiptsCreated=False,newDeviceCalls=0,newBuilds=0,newCandidateTestRuns=0,blockingFindings=[],limitations=['actual Android installation/current observation/runner unknown finish NOT_RUN','two fresh independent normal reports absent','external human approval/revocation and normal report provenance remain trusted operator duties','filesystem directory/power-loss persistence not newly guaranteed','old accepted review manifest self 0B row is historical excluded placeholder, not evidence of a zero-byte actual manifest','D1 NOT_PASSED/M0 NOT_STARTED/P0 and long-term admission unchanged']))
 print(json.dumps(dict(status='PASS_STATIC_LOCAL_FINAL_R1_CANDIDATE_REVIEW',checks=len(CHECKS),inputFiles=len(INPUTS),candidateReruns=0,builds=0,deviceCalls=0)))
if __name__=='__main__':
 try:main()
 except Exception as err:output('review-failure-attempt-002.json',dict(status='BLOCKED_OR_FAIL_STATIC_REVIEW',error=repr(err),completedChecks=CHECKS,deviceCalls=0));raise
