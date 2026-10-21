"""C06 fixture/APK plan only. This utility deliberately performs no device commands."""
from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parents[4];base=root/'docs/coder/d1c06'
summary=json.loads((base/'evidence/freeze-summary.json').read_text(encoding='utf-8'))
for r in summary['artifacts']:
 p=root/r['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
print(json.dumps({'candidate':'D1-20261005-C06','state':'PLAN_ONLY_NO_DEVICE_ACTION','artifacts':summary['artifacts'],'required_review':'Coordinator selects candidate after C02/C03 data preservation review; inspect authorized package/data/space before any replacement. Use frozen device appendix. No automatic install-r, push, cleanup or ADB.'},indent=2))
