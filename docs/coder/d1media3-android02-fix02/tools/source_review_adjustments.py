from pathlib import Path
B=Path(__file__).resolve().parents[1]
p=B/'instrumentation/com/videokit/d1media3/android02/test/ExperimentJob.java';s=p.read_text();assert 'new MatureMuxerBinding(output);' in s;s=s.replace('new MatureMuxerBinding(output);','new MatureMuxerBinding(output,this::requireAdmission);').replace('length>ScopeJournal.STATUS_LIMIT){','length>ScopeJournal.STATUS_LIMIT-8192){');p.write_text(s,encoding='utf-8')
p=B/'instrumentation/com/videokit/d1media3/android02/test/Media3Instrumentation.java';s=p.read_text();a=s.index(' private static String bounded(String text)');b=s.index(' @Override public void finish',a);s=s[:a]+''' private static String bounded(String text){if(text.getBytes(StandardCharsets.UTF_8).length>ExperimentContract.RECEIPT_UTF8_MAX)throw new IllegalStateException("RECEIPT_BYTE_BUDGET");return text;}
'''+s[b:];p.write_text(s,encoding='utf-8')
print('Additional receipt headroom before runner fields; no silent history-dropping fallback; Job-bound muxer admission')
