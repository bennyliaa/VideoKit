"""Opt-in two-case check of self-authored 4 KiB files; never opens media."""
import argparse
import json
from pathlib import Path
import subprocess

BASE = Path(__file__).resolve().parent.parent


def new_json(path, value):
    data = json.dumps(value, sort_keys=True, separators=(',', ':')).encode('ascii') + b'\n'
    if len(data) > 32768:
        raise ValueError('OWNED_PROBE_RECEIPT_CAP')
    with path.open('xb') as stream:
        stream.write(data)


def check():
    if (BASE / 'evidence/e3-freeze.json').exists():
        raise ValueError('FROZEN_PACKAGE_READ_ONLY')
    new_json(BASE / 'evidence/native-probes-reservation.json',
             dict(schema=1, cases=2, fixtureBytes=8192, repeatAllowed=False,
                  scope='E3_SELF_OWNED_NATIVE_PROBE_RESERVATION'))
    folder = BASE / 'selfcheck'
    folder.mkdir(exist_ok=True)
    cases = []
    for mode in ('strict-success', 'strict-guard-mismatch'):
        root = folder / ('java-bridge-' + mode)
        root.mkdir()
        with (root / 'L.bin').open('xb') as stream:
            stream.write(bytes(range(256)) * 16)
        args = ['D:/Android/Android Studio/jbr/bin/java.exe', '--enable-preview',
                '--enable-native-access=ALL-UNNAMED', '--add-opens=java.base/java.io=ALL-UNNAMED',
                '-cp', str(BASE / 'artifacts/java-e3'), 'videokit.e1.JavaBridgeProbe',
                '--owned-file-probe', str(root), mode]
        with (root / 'stdout.json').open('xb') as out, (root / 'stderr.log').open('xb') as err:
            completed = subprocess.run(args, stdin=subprocess.DEVNULL, stdout=out, stderr=err, check=False)
        stdout = (root / 'stdout.json').read_bytes()
        stderr = (root / 'stderr.log').read_bytes()
        if len(stdout) > 16384 or len(stderr) > 4096:
            raise ValueError('OWNED_PROBE_OUTPUT_CAP')
        receipt = json.loads(stdout.decode('utf-8'))
        case = dict(mode=mode, exitCode=completed.returncode, processExitObserved=True,
                    stdoutBytes=len(stdout), stderrBytes=len(stderr), receipt=receipt)
        cases.append(case)
    passed = all(case['exitCode'] == 0 and case['receipt']['status'] == 'PASS' for case in cases)
    result = dict(schema=1, scope='E3_SELF_OWNED_NATIVE_INPUT_PROBES', status='PASS' if passed else 'FAIL',
                  cases=cases, nativeProbeAssertions=sum(case['receipt'].get('assertions', 0) for case in cases),
                  fixtureBytes=8192, realMediaBytesRead=0, realMediaStatCalls=0,
                  realPFRun=False, real61Run=False, newG=0, osMetricSamples=0,
                  helpersStarted=2, helperPurpose='Two explicit Java-only self-owned probes; no R or production driver.',
                  noInFlight=True, reservationConsumed=False, outputRootCreated=False)
    new_json(BASE / 'evidence/native-probes.json', result)
    print(json.dumps(result, sort_keys=True, separators=(',', ':')))
    return 0 if passed else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    options = parser.parse_args()
    if options.check:
        raise SystemExit(check())
    print('{"scope":"E3_SELF_OWNED_NATIVE_PROBE_INSPECT","status":"NOT_RUN"}')
