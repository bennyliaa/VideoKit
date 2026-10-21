from pathlib import Path
import hashlib,json
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent;OLD=R/'docs/tester/D1_FIXTURE_SIX01_QUALIFIER_PREPARATION/Six01ContainerQualifier.java'
b=OLD.read_bytes();assert hashlib.sha256(b).hexdigest()=='a757ecc7587c9a02ce817152f092659863ff3370e6e594bef5acbe4a08ad3544'
s=b.decode('utf8');s=s.replace('Six01ContainerQualifier','Six01ContainerQualifier02').replace('SIX01_QUALIFIER_PREPARATION_COMPILED_NOT_YET_AUTHORIZED_TO_READ','SIX01_QUALIFIER02_FIX_PREPARED_WHOLE_METADATA_BLOCKED').replace('six01-original-readonly-qualifier','six01-qualifier02-original-readonly')
s=s.replace('volatile Map<String,Object> observation;','volatile Map<String,Object> observation;volatile Map<String,Object> dataReferenceObservation;')
line=next(x for x in s.splitlines() if 'DataRefBox refs=' in x)
replacement='''    DataRefBox refs=NodeBox.findFirstPath(trak,DataRefBox.class,Box.path("mdia.minf.dinf.dref"));
    dataReferenceObservation=map();DataReferencePolicy.inspect(refs,entry.getDrefInd(),dataReferenceObservation);
    // Mandatory original dref container version/flags and declared entry_count
    // are discarded by the frozen DataRefBox API. Never serialize parsed boxes
    // or substitute actual child count to manufacture these original facts.
    DataReferencePolicy.requireOriginalContainerMetadata(dataReferenceObservation);'''
s=s.replace(line,replacement)
s=s.replace('if(!pending&&joined)r.put("actualContainerObservation",observation);','if(!pending&&joined){r.put("actualContainerObservation",observation);r.put("actualDataReferenceChildObservation",dataReferenceObservation);}')
assert s.count('DataReferencePolicy.requireOriginalContainerMetadata')==1 and 'instanceof UrlBox' not in s and 'Six01ContainerQualifier()' not in s
target=E/'Six01ContainerQualifier02.java';assert not target.exists();target.write_text(s,encoding='utf8')
(E/'source-derivation.json').write_text(json.dumps(dict(base=str(OLD),baseSha256=hashlib.sha256(b).hexdigest(),newSource=str(target),newSourceSha256=hashlib.sha256(target.read_bytes()).hexdigest(),edits=['class/receipt/thread name02','volatile partial dref child observation only after original worker joins','UrlBox-only gate replaced with typed DataReferencePolicy','mandatory overall BLOCKED on missing original dref container header metadata'],otherGuardsUnchanged=True,oldSourceChanged=False,mediaReads=0),indent=2),encoding='utf8')
print('SOURCE02_PREPARED_WITH_MANDATORY_HEADER_API_GAP; no compile/runtime/media')
