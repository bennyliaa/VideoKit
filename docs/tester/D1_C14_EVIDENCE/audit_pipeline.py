"""Review recorded pipeline evidence and mappings; never executes a device command."""
import json,pathlib,re
B=pathlib.Path(__file__).resolve().parent;rows=json.loads((B/'tablet/results.json').read_text(encoding='utf-8'));review=[]
positive={'pipelineMp4RealFramesVideoOnly','pipelineAviRealFramesVideoOnly','pipelineReadyResponseLossSameToken'}
for row in rows:
 if row['group']!='pipeline' or 'attempt' not in row:continue
 o=B/'tablet'/row['attempt'];s=(o/'post/host.log').read_text(encoding='utf-8',errors='replace');events=[]
 for line in s.splitlines():
  fields=dict(re.findall(r'(\w+)=([^\s]+)',line))
  if fields.get('stage','').startswith(('PIPE_','CPU_OUTPUT_')):events.append(fields)
 def group(stage):return [f for f in events if f['stage']==stage]
 src=group('PIPE_SOURCE_FRAME');ins=group('PIPE_ENCODE_INPUT');samples=group('PIPE_ENCODE_SAMPLE');verified=group('CPU_OUTPUT_FRAME_VERIFIED');eof=group('CPU_OUTPUT_FULL_EOF_VERIFIED');content=group('PIPE_CONTENT_FRAME');visual=group('PIPE_VISUAL_CHECK');ready=group('PIPE_READY');ledgers={}
 for f in group('PIPE_LEDGER'):ledgers[f['export']]=f
 problems=[]
 for f in group('PIPE_LEDGER'):
  if int(f['queue_peak'])>2 or int(f['frame_consumers'])>1 or int(f['encoder_output_slots'])>1:problems.append('PIPE_RUNTIME_BUDGET_EXCEEDED')
 for f in ledgers.values():
  if any(f[k]!='true' for k in ['source_released','codec_released','writer_released','frames_released','resources_released']) or f['encoder_output_slots']!='0' or f['frame_consumers']!='0':problems.append('FINAL_RESOURCES_UNPROVEN')
 mappings=[]
 if row['method'] in positive:
  if [len(src),len(ins),len(samples),len(verified),len(content),len(eof),len(visual),len(ready)]!=[6,6,6,6,6,1,1,1]:problems.append('PIPE_POSITIVE_COUNTS_INCOMPLETE')
  else:
   first=int(src[0]['pts_us'])
   for i,(a,b,c,d,z) in enumerate(zip(src,ins,samples,verified,content),1):
    match=all(a[x]==b[y] for x,y in [('task','source_task'),('epoch','source_epoch'),('pid','source_pid'),('uid','source_uid'),('pts_us','source_pts'),('raw','raw'),('time_base','time_base'),('rgba_sha','rgba_sha')])
    match=match and all(int(f['sequence'])==i for f in [a,b,c,d,z]) and int(b['pts_us'])==int(a['pts_us'])-first and abs(int(c['pts_us'])-int(b['pts_us']))<=1000 and abs(int(d['pts_us'])-int(c['pts_us']))<=1000 and int(z['pts_us'])==int(d['pts_us'])
    if not match:problems.append('FRAME_MAPPING_UNPROVEN:'+str(i))
    mappings.append(dict(sequence=i,source=a,encoderInput=b,encoderSample=c,isolatedDecoded=d,content=z,matched=match))
   f=visual[0]
   if int(eof[0]['frames'])!=6 or eof[0]['audio_tracks']!='0' or int(f['frames'])!=6 or f['full_eof']!='true' or float(f['max_luma_mae'])>24 or float(f['source_distinction'])<4 or float(f['output_distinction'])<2:problems.append('CONTENT_OR_EOF_UNPROVEN')
   if ready[0]['audio_present']!='false' or int(ready[0]['output_bytes'])>2097152 or any(f['status']!='READY' for f in ledgers.values()):problems.append('READY_OUTPUT_UNPROVEN')
 elif row['method']!='pipelineOwnerRecoveryFencesIncompleteWriting':
  if ready or any(f['status']!='ABORTED' for f in ledgers.values()):problems.append('NEGATIVE_READY_OR_PENDING')
 if row['result']=='PASS':assert not problems,(row['method'],problems)
 review.append(dict(method=row['method'],result=row['result'],problems=problems,counts=dict(source=len(src),inputs=len(ins),samples=len(samples),verified=len(verified),content=len(content),eof=len(eof)),mapping=mappings,visual=visual,finalLedgers=ledgers,allPipelineLedgers=group('PIPE_LEDGER'),errors=group('PIPE_FAILURE'),ready=ready,encoder=group('PIPE_ENCODER_OPEN'),arrayBudget=dict(conservativeReachableRgbaArrays=8,bytes=1179648,yuvBytes=55296,independentRuntimeArrayPeakMeasured=False)))
(B/'pipeline-review.json').write_text(json.dumps(review,indent=2),encoding='utf-8');print(str(len(review))+' executed pipeline methods reviewed; recorded PASS mappings/resources checked')
