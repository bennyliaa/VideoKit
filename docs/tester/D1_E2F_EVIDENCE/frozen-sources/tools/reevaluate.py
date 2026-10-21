"""Explicit bounded offline entry. Defaults to Inspect; no actual run option."""
import argparse
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True

TOOLS = Path(__file__).absolute().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--reevaluate', action='store_true')
    parser.add_argument('--read-only', action='store_true')
    parser.add_argument('--expected-original-seal')
    args = parser.parse_args()
    if not args.reevaluate:
        print(json.dumps({'scope':'EVIDENCE_REEVALUATION_INSPECT','status':'NOT_RUN',
                          'actualExecutionAllowed':False,'originalEvidenceWrites':0,'outputCreated':False}))
        return 0
    from evidence_io import load_original_bundle, SEAL_SHA, require
    from e2f_wrapper import evaluate_bound_bundle
    require(args.expected_original_seal == SEAL_SHA, 'EXPECTED_ORIGINAL_SEAL_REQUIRED')
    bundle = load_original_bundle()
    result = evaluate_bound_bundle(bundle)
    data = (json.dumps(result, sort_keys=True, indent=2, ensure_ascii=True)+'\n').encode('ascii')
    require(len(data) <= 1048576, 'REEVALUATION_RECEIPT_LIMIT')
    if not args.read_only:
        base = TOOLS.parent
        require(not (base/'evidence/freeze-summary.json').exists(), 'FROZEN_E2F_PACKAGE_READ_ONLY')
        output = base/'reevaluation'
        output.mkdir(exist_ok=False)
        with open(output/'evidence-reevaluation.json', 'xb', buffering=0) as stream:
            require(stream.write(data) == len(data), 'REEVALUATION_EXACT_WRITE_REQUIRED')
        print(json.dumps({'scope':result['scope'],'decision':result['decision'],'accepted':result['accepted'],
                          'originalResult':result['originalResult'],'readerUsage':result['readerUsage'],
                          'output':'reevaluation/evidence-reevaluation.json','newActualAttempts':0}))
    else:
        print(data.decode('ascii'), end='')
    return 0 if result['accepted'] else 2


if __name__ == '__main__':
    sys.exit(main())
