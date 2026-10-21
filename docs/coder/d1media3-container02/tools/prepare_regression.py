from pathlib import Path
B=Path(__file__).resolve().parents[1];assert not (B/'evidence/media3-container02-freeze.json').exists()
s=(B/'reference/IndependentContainerBoundaryCheck-original.java').read_text()
s=s.replace('IndependentContainerBoundaryCheck','ContainerB01Regression').replace('Tester-owned boundary evidence','Coder replay of exact tester boundary inputs').replace('PASS independent_container','PASS coder_replay_container')
s=s.replace('need(first.equals(timeout?"OUTPUT_TIMEOUT_PENDING":"OUTPUT_ORIGINAL_PENDING")&&h.reopenRPC==1&&!s.returned(),"original result retained but first error recorded");','need((timeout?"OUTPUT_TIMEOUT_PENDING".equals(first):first==null)&&h.reopenRPC==1&&!s.returned(),"true timeout sticky; pre-inspection return wait has no first failure");')
start=s.index('   if(!timeout){rejected(');end=s.index('\n   need(s.abort()',start)
s=s[:start]+'''   if(!timeout){need(s.firstFailure()==null,"same original returned; no cancellation/abort before continue");rejected(()->s.inspectHostMp4Structure(HostMp4Inspection.Container.FRAGMENTED_MP4),"OUTPUT_HOST_STRUCTURE_FAILED");need(h.reopenRPC==1&&"OUTPUT_HOST_STRUCTURE_FAILED".equals(s.firstFailure())&&HostInputFactory.admittedSources()==0,"continued once to actual platform boundary via same grant; no parse success");System.out.println("FIXED MC_B01 cancelOrAbortBeforeRetry=false hostOriginalReturned="+h.originalOperationsReturned()+" reopenRPC="+h.reopenRPC+" newInspectionBoundary=ACTUAL_PLATFORM_FAILURE_NOT_CONTAINER_PASS "+s.state());pass("MC_B01_same_original_return_then_first_inspection");}'''+s[end:]
s=s.replace('reproducedFindings=1','MC_B01_corrected_no_old_finding_claimed=true')
(B/'checks/com/videokit/d1input/ContainerB01Regression.java').write_text(s,encoding='utf-8')
for name in ['review_all.py','run_suites.py']:
 p=B/'tools'/name;s=p.read_text();marker="for mode,cp in [('source',source),('production',prod)]:" if name=='review_all.py' else 'for name,cls,extra in plan:'
 assert marker in s;s=s.replace(marker,"plan += [('mc-b01','ContainerB01Regression',[]),('inspection-orders','ContainerPendingOrderCheck',[])]\n"+marker);p.write_text(s,encoding='utf-8')
print('Exact tester inputs retained; corrected assertions distinguish first attempt from genuine timeout; new matrix added.')
