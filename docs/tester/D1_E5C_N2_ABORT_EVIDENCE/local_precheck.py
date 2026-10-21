"""Tester script local-only review; no candidate/device invocation."""
from common import *
import ast
tree=ast.parse((E/'execute_abort.py').read_text())
assigns={n.targets[0].id:n.value for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name)}
post=ast.literal_eval(assigns['POST'].func.value).replace('TASK',TASK)
for text in [SCRIPT,post]:
    assert shlex.split('run-as com.videokit.app sh -c '+shlex.quote(text))==['run-as','com.videokit.app','sh','-c',text]
    for bad in ['rm ','mv ','mkdir','install','am instrument','kill','chmod','>','>>']:assert bad not in text,bad
assert 'test "$total" -le 16384' in post and 'test "$n" -le 4096' in post
save('local-precheck.json',dict(pythonAst='PASS',bothWholeScriptQuoteRoundTrips='PASS',commands='Previously supported Android id/pwd/test/stat/sha256sum/cat/od/printf and fixed arithmetic only',postMetadataBytesCap=16384,postIndividualMetadataCap=4096,outputRead='PRODUCTION_ONLY_MAX_2MiB_NO_INDEPENDENT_MEDIA_HASH',deviceCalls=0))
print('PASS local syntax/quoting/readonly path and bounds review; no device call')
