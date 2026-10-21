exec((__import__('pathlib').Path(__file__).resolve().parent/'run_checks.py').read_text().split("run('tester-compile'")[0])
run('additional-compile',[str(J/'javac.exe'),'--release','11','-encoding','UTF-8','-cp',cp,'-d',str(C),str(E/'ReadbackReturnCheck.java'),str(E/'LateCancelledAckCheck.java')])
for mode,path in [('source',cp),('production',prod)]:
 for cls in ['ReadbackReturnCheck','LateCancelledAckCheck']:
  run(cls.lower()+'-'+mode,[str(J/'java.exe'),'-Xmx256m','-cp',path,'com.videokit.d1input.'+cls])
