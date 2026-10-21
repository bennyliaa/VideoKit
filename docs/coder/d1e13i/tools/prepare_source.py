from pathlib import Path
import json,hashlib,shutil
B=Path(__file__).resolve().parents[1];R=B.parents[2];H=R/'docs/coder/d1e13h';F=R/'docs/coder/d1e13f'
assert not (B/'tools/E13IIdentity.java').exists()
t=(H/'tools/E13GReadOnly.java').read_text();prefix=t[:t.index(' interface Runtime')];valid=t[t.index(' static void validateIdentity'):t.index(' /** Minimal single fixed service')];prefix=prefix.replace('public final class E13GReadOnly','final class E13IIdentity').replace(' static List<String> identityCommand(List<Identity> identities)',' static String identityScript(List<Identity> identities)').replace('return command(sh.toString());','return sh.toString();');(B/'tools/E13IIdentity.java').write_text(prefix+valid+' private E13IIdentity(){}\n}\n',encoding='utf-8')
(B/'artifacts').mkdir();manifest=json.loads((F/'evidence/host-jar-manifest.json').read_text());shutil.copyfile(R/manifest['jar']['path'],B/'artifacts/e13f-reviewed-base.jar')
for rel in ['docs/tester/D1_E13H_READONLY_ENTRY_REVIEW_REPORT_V1.0.md','docs/coder/d1e13h/evidence/local-probe-environment-history.json','docs/tester/D1_E13G_CURRENT_STATE_AND_DISPOSITION_PROPOSAL_V1.0.md']:shutil.copyfile(R/rel,B/'reference'/Path(rel).name)
rows=[];commit='1cf2f017d312f73b3dc53bda85ef2610e35a80e9'
for p in sorted((B/'reference/protocol').iterdir()):
 if p.name=='OVERVIEW.TXT' or p.name=='commit.json':continue
 raw=p.read_bytes();assert raw;rows.append(dict(path=p.relative_to(R).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),commit=commit))
(B/'evidence/protocol-source-manifest.json').write_text(json.dumps(dict(status='EXACT_OFFICIAL_SOURCE_BYTES',commit=commit,repository='https://android.googlesource.com/platform/packages/modules/adb',files=rows,failedOptionalOverviewFetch='HTTP NOT_FOUND; not protocol authority',serviceWhitelist=['host:transport:HA1Q6WXR','shell,v2,raw:<fixed inventory or strictly derived identity script>'],versionServiceUsed=False),indent=2)+'\n')
print('Prepared reviewed identity gates, unchanged F base and',len(rows),'official protocol files')
