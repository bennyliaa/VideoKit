"""File-only post replay repair; no worker, Gate, capture or scope rerun."""
from pathlib import Path
R=Path(__file__).resolve().parent
text=(R/'post_audit.py').read_text()
text=text.replace("save(R/'host-context-case-analysis.json',context)","save(R/'host-context-case-analysis-v2.json',context)")
text=text.replace("models=ns['matrix'](fp,item['policy'],item['template'],item['pins'])", "ns['datetime']=ModelDateTime;models=ns['matrix'](fp,item['policy'],item['template'],item['pins'])")
exec(compile(text,'<file-only-post-v2>', 'exec'),dict(__name__='__main__',__file__=str(__file__)))
