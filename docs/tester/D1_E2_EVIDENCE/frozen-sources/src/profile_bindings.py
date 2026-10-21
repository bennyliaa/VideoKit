"""Explicit IO geometry. No path-name inference, file access or execution grant."""
import copy
from gcore import need

def synthetic_profile():
    return dict(schema=1,kind='SYNTHETIC',lengths={'L':131072,'C':4096,'Z':0},boundary=65536,
                inputs={'L':'L.bin','C':'C.bin','Z':'Z.bin'})

def real_profile(bundle):
    inputs=bundle['inputs']['inputs']
    return dict(schema=1,kind='REAL_IO',lengths={key:inputs[key]['historical']['bytes'] for key in ('L','C','Z')},
                boundary=2147483648,inputs={key:inputs[key]['path'] for key in ('L','C','Z')})

def boundary_for(profile):
    need(profile['kind'] in ('SYNTHETIC','REAL_IO'),'PROFILE_KIND')
    expected=65536 if profile['kind']=='SYNTHETIC' else 2147483648
    need(profile['boundary']==expected,'PROFILE_BOUNDARY')
    return expected

def require_synthetic(profile=None):
    value=copy.deepcopy(profile if profile is not None else synthetic_profile())
    need(value.get('kind')=='SYNTHETIC','REAL_EXECUTION_DISABLED_E2_ADMISSION')
    need(value==synthetic_profile(),'SYNTHETIC_PROFILE_BINDING_MISMATCH')
    return value
