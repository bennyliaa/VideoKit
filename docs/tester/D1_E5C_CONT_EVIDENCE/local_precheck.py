"""Local tester script syntax/quote review, without executing any device/candidate command."""
from pathlib import Path
import ast,subprocess,shlex,json,hashlib
E=Path(__file__).resolve().parent
for name in ['common.py','execute_cont.py']:ast.parse((E/name).read_text(encoding='utf-8'))
tree=ast.parse((E/'common.py').read_text(encoding='utf-8'))
assigns={n.targets[0].id:n.value for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name)}
script=ast.literal_eval(assigns['SCRIPT'].func.value).replace('TASK',ast.literal_eval(assigns['TASK']))
cmd='run-as com.videokit.app sh -c '+shlex.quote(script)
assert shlex.split(cmd)==['run-as','com.videokit.app','sh','-c',script]
# Entire fixed private-state script uses Android commands already evidenced in N2: id/pwd/test/stat/sha256sum/cat/od/printf.
for forbidden in ['rm ','mv ','mkdir','install','am instrument','kill','chmod','>','>>']:
    assert forbidden not in script,forbidden
(E/'reviewed-private-state.sh').write_bytes(script.encode('utf-8'))
value=dict(pythonAst='PASS',wholeScriptQuoteRoundTrip='PASS',privateStateCommands=['id','pwd','test','stat','sha256sum','cat','od','printf'],roles='fixed exact original metadata and fixture stat only',mediaContentHash=False,scriptSha256=hashlib.sha256(script.encode()).hexdigest(),rootCheck='quoted whole fixed root-existence script; no scan or create',correctiveAttemptsUsed=0,deviceCalls=0)
with (E/'local-precheck.json').open('x',encoding='utf-8') as f:json.dump(value,f,indent=2);f.write('\n')
print(json.dumps(value))
