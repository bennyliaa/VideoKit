from pathlib import Path
import json,hashlib,subprocess,datetime
R=Path('D:/CodexProjects/VideoKit'); E=Path(__file__).resolve().parent; B=R/'docs/coder/d1media3-container01'
P=Path('C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
targets=[str(R/'docs/tester/D1_INPUT_SINK05_REVIEW_EVIDENCE/media3-invalid-child'),str(B/'invalid-review-child'),str(E.parent/(E.name+'_FAKE')/'invalid-child'),str(E/'..'/'media3-invalid-escape'),'docs/tester/relative-invalid',str(E),str(E/'independent-001')]
runs=[]
for tool,flag in [('review_all.py','--output'),('local_check.py','--review-output')]:
 for i,t in enumerate(targets):
  target=Path(t);existed=target.exists();argv=[str(P),'-X','utf8','-B',str(B/'tools'/tool),flag,t]
  p=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=45)
  prefix=E/f'output-gate-{tool[:-3]}-{i}';prefix.with_suffix('.stdout').write_bytes(p.stdout);prefix.with_suffix('.stderr').write_bytes(p.stderr)
  row=dict(argv=argv,exitCode=p.returncode,targetExistedBefore=existed,targetExistsAfter=target.exists(),originalProcessReturned=True)
  assert p.returncode!=0 and (existed or not target.exists()),row
  runs.append(row)
(E/'output-gates.json').write_text(json.dumps(dict(result='PASS_14_REJECTIONS_NO_NEW_TARGET',runs=runs),indent=2),encoding='utf8')
old=[]
for name,manifest in [('D1_MEDIA3_CONTAINER01_PHASE_A_EVIDENCE','phase-a-evidence-manifest.json'),('D1_INPUT_SINK05_REVIEW_EVIDENCE','review-evidence-manifest.json')]:
 d=load(E.parent/name/manifest)
 assert sha(R/d['report'])==d['reportSha256']
 for r in d['evidenceFiles']:assert (R/r['path']).stat().st_size==r['bytes'] and sha(R/r['path'])==r['sha256'],r['path']
 old.append(dict(manifest=name+'/'+manifest,files=len(d['evidenceFiles']),reportSha256=d['reportSha256']))
d=load(B/'evidence/media3-container01-freeze.json')
for r in d['files']:assert (R/r['path']).stat().st_size==r['bytes'] and sha(R/r['path'])==r['sha256'],r['path']
s=load(E/'independent-001/summary.json');assert len(s['runs'])==56 and all(x['exitCode']==0 for x in s['runs']) and s['frozenCandidate']
for mode in ['source','production']:
 receipt=load(E/f'independent-boundaries-{mode}-1.json');assert receipt['exitCode']==0
 out=(E/f'independent-boundaries-{mode}-1.stdout').read_text();assert 'cancelOrAbortBeforeRetry=false' in out and 'independentBoundaryPasses=7 reproducedFindings=1 allActualThreadsReturned=true sourceKeepers0 outputKeepers0' in out
scope=load(B/'reference/approved-sample-scope.json');sample=R/scope['path'];assert sample.stat().st_size==scope['bytes'] and sha(sample)==scope['sha256']
(E/'post-review-preservation.json').write_text(json.dumps(dict(checkedUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),result='PASS',oldEvidence=old,candidateFilesUnchanged=len(d['files']),runnerExit0Count=56,independentDualPathFinal='7_PASS_1_REPRO_EACH',sampleAfter=dict(path=scope['path'],bytes=sample.stat().st_size,sha256=sha(sample)),sdkAdbGradleNetworkCalls=0),indent=2),encoding='utf8')
statuses=[('PASS_LIMITED','新使用两依赖身份、许可和 strict 本地材料核验；不证明平台执行'),('PASS_REFERENCE_ONLY','原参考视频权利记录、349102B/hash只读核对；无生成或改写'),('OPEN','参考视频320x180/含AAC/8秒，不符单AVC256x144六样本条件'),('PASS_LIMITED','capability/container/seek参数在provider和适配器分配前拒绝'),('NOT_RUN','真实Mp4Extractor构造平台链接失败，未提取轨道和样本'),('NOT_RUN','真实FragmentedMp4Extractor缺Parcelable，未提取'),('PASS_COMPONENT_ONLY','真实DefaultExtractorInput短读3+3+1；同容器样本结果未执行'),('PASS_COMPONENT_ONLY','未知长度/EOF/截断组件边界；同容器未知长度未执行'),('PASS_COMPONENT_ONLY','真实peek/reset短读位置及预算通过；sniff实际解析未执行'),('PASS_COMPONENT_ONLY','绝对位置5+remaining68=>end73；真实SeekMap/RESULT_SEEK未执行'),('PASS_BASELINE_ONLY','原范围和溢出拒绝回归；无真实稀疏容器解析'),('NOT_RUN','无真实损坏atom/sample解析；readFully EOF不替代此项'),('PASS_BASELINE_ONLY','原输入异常/脱敏回归；提取器内异常未执行'),('PASS_COMPONENT_ONLY','真实DefaultInput取消后迟到原read/close归还；实际inspect取消未执行'),('PASS_BASELINE_ONLY','原source close/UNKNOWN保留；实际提取器close未执行'),('PASS_RAW_READ_ONLY','源码/JAR各known/unknown完整原视频EOF/hash；parser EOF和尾部语义未执行'),('NOT_RUN','真实muxer轨道正反例未运行'),('NOT_RUN','真实合法编码样本/ByteBuffer muxer边界未运行'),('PARTIAL_STATIC_AND_PRIOR_GUARD','原E6六payload/EOS静态约束和阶段A五项负例保留；真实六样本未运行'),('OPEN','真实timescale/舍入/最终EOS时长oracle无正例证据'),('OPEN','无真实NAL表示/CSD转换及重提取比较'),('NOT_RUN','合格fixture缺口与真实muxer平台链接限制'),('PASS_BASELINE_ONLY','原partial ACK/物理写入/UNKNOWN回归；muxer整链未执行'),('PASS_COMPONENT_ONLY','同Reader跨close/reopen累计4+4MiB，下一读provider前拒绝；16MiB/槽位基线通过'),('PASS_BASELINE_ONLY','原flush/close异常及尾段回归；真实muxer finalize未执行'),('FAIL_MC_B01','新增inspect把原REOPEN暂待归还永久化；源码/JAR双复现；writer前置门静态保留'),('NOT_RUN','真实重开输出结构/六样本/CSD/PTS比较未运行'),('NOT_RUN','真实输出损坏/hash/track/sample差异解析未运行'),('PASS_BASELINE_ONLY','原source全局2/每源1/原任务归还回归；实际提取与重开组合未执行'),('PARTIAL_FAIL_MC_B01','既有response/observer/worker回归通过；新增inspect暂待归还错误见MC-B01'),('PASS_STATIC_AND_NEGATIVE_ONLY','结构类型与validated/READY分离；前置失败无发布；成功结构路径未运行'),('NOT_RUN','Android FD/fsync/codec、隔离内容、业务提交和播放均未执行')]
cases=load(E.parent/'D1_MEDIA3_CONTAINER01_PHASE_A_EVIDENCE/independent-cases.json')['cases'];assert len(cases)==len(statuses)==32
for c,(status,evidence) in zip(cases,statuses):c.update(status=status,phaseBEvidence=evidence)
(E/'independent-case-results.json').write_text(json.dumps(dict(overall='FAIL_NEW_P2_WITH_FUNCTIONAL_SCOPE_OPEN',cases=cases),ensure_ascii=False,indent=2),encoding='utf8')
print('PASS output gates14; preservation; final dual paths; MC01-32 mapped')
