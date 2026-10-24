"""Finite qualification child; report only canonical context hash/key names."""
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
from host_context import snapshot
if sys.argv[1:] not in (['ok'],['fail']):raise ValueError('FIXED_QUAL_MODE')
print(json.dumps(snapshot()),flush=True)
raise SystemExit(0 if sys.argv[1]=='ok' else 7)
