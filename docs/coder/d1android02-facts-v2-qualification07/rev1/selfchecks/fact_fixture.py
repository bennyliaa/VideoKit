"""Fixed OFFLINE facts data producer, no SDK or arbitrary program."""
import sys,hashlib
from pathlib import Path
if sys.argv[1:]==['COMPLETE']:
 raw=b'GI_FACTS_V1\nGI_ITEM|model|0|1000|1000|8\nTB138FC\n\nGI_ITEM|api|0|1000|1000|3\n31\n\nGI_ITEM|firmware|0|1000|1000|33\nSYNTHETIC_FIXTURE_FIRMWARE_API31\n\nGI_ITEM|user|0|1000|1000|2\n0\n\nGI_ITEM|system|0|1000|1000|72\npackage:com.zui.launcher uid:10012\npackage:com.fixture.system uid:10065\n\nGI_ITEM|role|0|1000|1000|192\nROLE STATE (dumpsys role):\n{\n  user_states={\n    user_id=0\n    version=1\n    packages_hash=FIXTURE_HASH\n    roles={\n      name=android.app.role.HOME\n      holders=com.zui.launcher\n    }\n  }\n}\n\nGI_ITEM|home|0|1000|1000|27\ncom.zui.launcher/.Launcher\n\nGI_FACTS_END\n'
elif len(sys.argv)==4 and sys.argv[1]=='RAW_FILE':
 p=Path(sys.argv[2])
 if p.name!='fixture-facts.raw' or not p.is_absolute():raise SystemExit('FACT_FIXTURE_RAW_PATH')
 with p.open('rb') as f:raw=f.read(139265)
 if not 1<=len(raw)<=139264 or hashlib.sha256(raw).hexdigest()!=sys.argv[3]:raise SystemExit('FACT_FIXTURE_RAW_BYTES')
else:raise SystemExit('EXACT_FIXTURE_ONLY')
sys.stdout.buffer.write(raw)
