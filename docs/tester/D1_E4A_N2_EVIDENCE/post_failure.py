from common import *
try:
    new('post-failure-attempt.json',{'batch':BATCH,'scope':'READONLY_ORIGINAL_METADATA_NO_RESTART_NO_HASH_NO_PRODUCT_CALL'})
    prior=json.loads((E/'preflight-script.json').read_text());script=prior['script']
    task='86cafdb3-0fc4-447d-920b-b19c884bf494'
    for suffix in ('.identity','.journal'):
        path='files/e4a_outputs/'+task+suffix
        script+=f'printf "NEW_METADATA|{path}\\n"; if test -f {path} && test ! -L {path}; then /system/bin/toybox stat -c %s -- {path}; /system/bin/toybox od -An -tx1 -N 4096 -- {path}; else printf "UNAVAILABLE\\n"; fi\n'
    r,text=shell(script,'03-post-failure-private-state');assert r['originalExitCode']==0
    r,ps=shell('ps -u 10221 -o PID,PPID,UID,NAME; printf "PS_RC=%s\\n" "$?"; dumpsys activity instrumentation','04-post-instrumentation-state',False)
    new('post-failure-result.json',{'status':'READONLY_ORIGINAL_FACTS_RECORDED','deviceHashReads':0,'pendingPresent':'ORIGINAL_PENDING_PRESENT' in text,'retainedHostClientOwners':ep.retained_owners(),'productProtocolOwners':'UNKNOWN_NOT_RELEASED','nextEncoderAdmitted':False})
    print(text,flush=True);print(ps,flush=True)
finally:hold()
