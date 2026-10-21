exec((__import__('pathlib').Path(__file__).resolve().parent/'run_additional.py').read_text().split("run('independent-compile-final'")[0])
run('host-sample-compile',[str(J/'javac.exe'),'--release','11','-encoding','UTF-8','-cp',cp,'-d',str(C),str(E/'IndependentHostResults.java')])
for mode in ['source','production']:run('host-samples-'+mode,[str(J/'java.exe'),'-Xmx256m','-cp',(str(jar)+';' if mode=='production' else '')+cp,'com.videokit.d1input.IndependentHostResults'])
