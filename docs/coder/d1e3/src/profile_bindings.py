"""Pure exact geometry; a profile is data and never an execution grant."""
import copy
from pathlib import PureWindowsPath

REAL_LENGTHS={'L':3212959911,'C':4096,'Z':0}
REAL_INPUTS={'L':'D:/CodexProjects/VideoKit/test_media/03_large_files/large_video_over_2GiB.mkv',
             'C':'D:/CodexProjects/VideoKit/test_media/04_corrupted_files/corrupted_video.mp4',
             'Z':'D:/CodexProjects/VideoKit/test_media/04_corrupted_files/empty_video.mkv'}
REAL_BOUNDARY=2147483648
REAL_WINDOWS=(2147418112,2147450880,2147483648,3212894375)

def need(value,reason):
    if not value:raise ValueError(reason)

def synthetic_profile():
    return dict(schema=1,kind='SYNTHETIC',lengths={'L':131072,'C':4096,'Z':0},boundary=65536,
                inputs={'L':'L.bin','C':'C.bin','Z':'Z.bin'})

def build_real_profile(inputs_document):
    items=inputs_document['inputs']
    value=dict(schema=1,kind='REAL_IO',lengths={key:items[key]['historical']['bytes'] for key in ('L','C','Z')},
               boundary=REAL_BOUNDARY,inputs={key:items[key]['path'] for key in ('L','C','Z')})
    return validate_real_profile(value)

def real_profile(bundle):return build_real_profile(bundle['inputs'])

def validate_real_profile(profile):
    need(type(profile) is dict and set(profile)=={'schema','kind','lengths','boundary','inputs'},'REAL_PROFILE_SCHEMA')
    need(type(profile['schema']) is int and profile['schema']==1 and profile['kind']=='REAL_IO','REAL_PROFILE_KIND')
    need(type(profile['boundary']) is int and profile['boundary']==REAL_BOUNDARY,'REAL_BOUNDARY_MISMATCH')
    need(profile['lengths']==REAL_LENGTHS and all(type(n) is int for n in profile['lengths'].values()),'REAL_LENGTHS_MISMATCH')
    need(type(profile['inputs']) is dict and set(profile['inputs'])==set(REAL_INPUTS) and
         all(type(value) is str for value in profile['inputs'].values()),'EXACT_R2_INPUT_PATHS_REQUIRED')
    normalized={key:PureWindowsPath(value).as_posix() for key,value in profile['inputs'].items()}
    need(normalized==REAL_INPUTS,'EXACT_R2_INPUT_PATHS_REQUIRED')
    result=copy.deepcopy(profile);result['inputs']=normalized;return result

def validate_geometry(profile):
    value=validate_real_profile(profile) if profile.get('kind')=='REAL_IO' else require_synthetic(profile)
    b=value['boundary'];length=value['lengths']['L']
    windows=(b-65536,b-32768,b,length-65536)
    need(all(type(offset) is int and 0<=offset<=length-65536 for offset in windows),'WINDOW_GEOMETRY')
    if value['kind']=='REAL_IO':need(windows==REAL_WINDOWS,'REAL_WINDOWS_MISMATCH')
    return {'B':b,'offsets':list(windows),'requestBytes':65536,
            'shortReadContract':'POSITIVE_SHORT_READ_IS_UNFILLED_NOT_PROVIDER_VIOLATION',
            'shortRequestedBytes':sum(65536-n for n in range(4))+4,'shortRequestCalls':5,
            'nextUnfilledRequestBytes':65532,'nextRequestAdmitted':False}

def boundary_for(profile):
    if profile.get('kind')=='REAL_IO':return validate_real_profile(profile)['boundary']
    return require_synthetic(profile)['boundary']

def require_synthetic(profile=None):
    value=copy.deepcopy(profile if profile is not None else synthetic_profile())
    need(value.get('kind')=='SYNTHETIC','REAL_EXECUTION_REQUIRES_TYPED_E3_PERMIT')
    need(value==synthetic_profile(),'SYNTHETIC_PROFILE_BINDING_MISMATCH')
    return value

def profile_for_engine(profile,permit,root):
    value=copy.deepcopy(profile if profile is not None else synthetic_profile())
    if value.get('kind')=='SYNTHETIC':return require_synthetic(value)
    value=validate_real_profile(value)
    # Importing the pure profile module cannot construct a backend or read IO.
    need(permit is not None and type(permit) is not dict,'REAL_PROFILE_REQUIRES_ORIGINAL_RUNTIME_PERMIT')
    try:from e3_admission import RuntimePermit
    except ImportError as error:raise ValueError('REAL_PROFILE_REQUIRES_ORIGINAL_RUNTIME_PERMIT') from error
    need(type(permit) is RuntimePermit and permit.binds(root,value),'REAL_PROFILE_REQUIRES_ORIGINAL_RUNTIME_PERMIT')
    return value
