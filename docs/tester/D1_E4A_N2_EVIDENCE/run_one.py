from product_call import *
import re,datetime
allowed=['normalMp4SixRealFrames','normalAviSixRealFrames','capabilityDenialDoesNotOpenSource','cancelRejectsWrongEpochOversizeAndLateFrame']
method=sys.argv[1];assert method in allowed
assert (E/'preflight-result.json').exists()
extra=[]
if method==allowed[1]:assert json.loads((E/'normalMp4SixRealFrames-independent-review.json').read_text())['dependentEncoderAdmitted']
if method==allowed[3]:
    gate=json.loads((E/'cancel-admission.json').read_text());assert gate['admitted'] and gate['budgetIdentity']==BUDGET and len(gate['normalReceiptSha256'])==64
    extra=['-e','e4NormalReceiptSha256',gate['normalReceiptSha256']]
new(method+'-attempt.json',{'method':method,'batch':BATCH,'budget':BUDGET,'at':datetime.datetime.now().astimezone().isoformat(),'attempts':1,'deadlineSeconds':30 if method==allowed[3] else 60})
try:
    rr,stamp=shell('date +%s',method+'-start-clock',False);assert rr['originalExitCode']==0 and stamp.strip().isdigit()
    args=[ADB,'-s',SERIAL,'shell','-n','-T','-e','none','am','instrument','-w','-r','-e','class','com.videokit.spike.e4.E4DeviceTests#'+method,'-e','e4Case',method,'-e','e4Batch',BATCH,'-e','e4BudgetIdentity',BUDGET,*extra,'com.videokit.app.test/androidx.test.runner.AndroidJUnitRunner']
    r,text=instrument(args,method+'-instrumentation',30 if method==allowed[3] else 60)
    passed=r['status']=='PROCESS_IO_COMPLETE_ONLY' and 'OK (1 test)' in text and 'INSTRUMENTATION_CODE: -1' in text and 'FAILURES!!!' not in text
    rr,logs=call(['logcat','-d','-b','main','-b','system','-b','crash','-v','threadtime,epoch,uid','-T',stamp.strip()+'.000','VideoKitD1:I','AndroidRuntime:E','ActivityManager:I','TestRunner:I','*:S'],method+'-logcat',15,1048576)
    new(method+'-outer-result.json',{'method':method,'junit':'PASS' if passed else 'FAIL','requiresIndependentReview':True,'metadataLogCap':1048576,'retained':ep.retained_owners(),'originalProductOwnerClear':False,'nextEncoderAuthorized':False})
    print(text,flush=True)
finally:hold()
