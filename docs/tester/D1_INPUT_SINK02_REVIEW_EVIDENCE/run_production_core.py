exec((__import__('pathlib').Path(__file__).resolve().parent/'run_checks.py').read_text().split("run('tester-compile'")[0])
D=E/'production-core';D.mkdir(exist_ok=False)
run('production-core',[str(J/'java.exe'),'-Xmx256m','-cp',prod,'com.videokit.d1input.InputSinkCheck',str(D)])
