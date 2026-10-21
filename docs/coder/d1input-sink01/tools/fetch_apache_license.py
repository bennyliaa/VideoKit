from pathlib import Path
import urllib.request,hashlib,json,datetime
B=Path(__file__).resolve().parents[1];D=B/'licenses';D.mkdir(exist_ok=False);url='https://www.apache.org/licenses/LICENSE-2.0.txt'
with urllib.request.urlopen(url,timeout=30) as r:data=r.read(32769);assert len(data)<=32768;receipt={'requestedUrl':url,'finalUrl':r.url,'status':r.status,'headers':dict(r.headers),'retrievedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
(D/'Apache-2.0.txt').write_bytes(data);(B/'evidence/apache-license-source.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8');print('OFFICIAL_APACHE_LICENSE_TEXT_RETAINED')
