"""Read-only offline package audit. Does not launch or sample anything."""
import argparse
import json
import sys
sys.dont_write_bytecode = True
from package_support import SourceReader, configuration, validate_receipts


def audit():
    reader=SourceReader();binding=configuration(reader);checks,result=validate_receipts(reader)
    return {'schema':1,'status':'PASS','scope':'E2F_READ_ONLY_OFFLINE_PACKAGE_AUDIT',
            'productionBinding':binding,'offlineAssertions':checks['assertions'],
            'reevaluationDecision':result['decision'],'originalResult':result['originalResult'],
            'originalEvidenceReadUsage':result['readerUsage'],'sourceReadUsage':reader.usage(),
            'newActualAttempts':0,'newActualPasses':0,'newG':0,'helpersStarted':0,
            'newOSMetricSamples':0,'compileInvocations':0,'originalEvidenceWrites':0,
            'fixtureBytes':0,'noInFlight':True,'D1':'NOT_PASSED','M0':'NOT_STARTED'}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--audit',action='store_true');args=parser.parse_args()
    print(json.dumps(audit() if args.audit else {'mode':'INSPECT_ONLY','newActualAttempts':0,'originalEvidenceWrites':0}))
