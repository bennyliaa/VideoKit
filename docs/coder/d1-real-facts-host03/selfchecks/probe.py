"""Bounded no-SDK probe only; never a facts producer."""
import sys,json
mode=sys.argv[1];assert len(sys.argv)==2
if mode=='ok':print(json.dumps(dict(schema='HOST01_PROBE_RETURN_V1',value='ok')))
elif mode=='fail':print('EXPECTED_PROBE_EXIT_7');raise SystemExit(7)
elif mode=='empty':pass
elif mode=='bad':print('{bad-json')
elif mode=='over':sys.stdout.buffer.write(b'x'*270000)
else:raise ValueError('FIXED_PROBE_MODE')
