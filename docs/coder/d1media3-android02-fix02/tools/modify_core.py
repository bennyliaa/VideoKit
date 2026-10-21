from pathlib import Path
B=Path(__file__).resolve().parents[1]
def edit(rel,a,b):
 p=B/rel;s=p.read_text();assert a in s,(rel,a[:60]);p.write_text(s.replace(a,b),encoding='utf-8')
H='src/com/videokit/d1input/HostMp4Inspection.java'
edit(H,' static final class Reader implements DataReader {',''' public interface Phases {void phase(String value);default int maxReadRequest(){return 65536;}}
 public static final Phases NO_PHASES=value->{};
 static final class Reader implements DataReader {''')
edit(H,'final HostDataSource ds;long readBytes;','final HostDataSource ds;final int maxRequest;long readBytes;')
edit(H,'Reader(HostDataSource ds){this.ds=ds;}','Reader(HostDataSource ds){this(ds,65536);}Reader(HostDataSource ds,int max){this.ds=ds;if(max<1||max>65536)throw new IllegalArgumentException("READ_REQUEST_CAP");maxRequest=max;}')
edit(H,'Math.min(65536L,len)','Math.min((long)maxRequest,len)')
edit(H,'  Objects.requireNonNull(factory);factory.worker.requireWorker();','  return inspect(factory,container,mp4ReadCapability,seekUs,capture,NO_PHASES);\n }\n public static Evidence inspect(HostInputFactory factory,Container container,boolean mp4ReadCapability,long seekUs,boolean capture,Phases phases)throws IOException {\n  Objects.requireNonNull(factory);factory.worker.requireWorker();')
edit(H,'Reader reader=new Reader(ds);','Reader reader=new Reader(ds,phases.maxReadRequest());')
edit(H,'   long announced=ds.open','   phases.phase("HASH");long announced=ds.open')
edit(H,'   scan.open(0);','   phases.phase("PARSE");scan.open(0);')
edit(H,'    SeekPoint point=output.seek','    phases.phase("SEEK");SeekPoint point=output.seek')
T='src/com/videokit/d1input/TemporaryOutput.java'
edit(T,'public HostMp4Inspection.Evidence inspectHostMp4Structure(HostMp4Inspection.Container container)throws IOException {enter();try{','public HostMp4Inspection.Evidence inspectHostMp4Structure(HostMp4Inspection.Container container)throws IOException {return inspectHostMp4Structure(container,HostMp4Inspection.NO_PHASES);}\n public HostMp4Inspection.Evidence inspectHostMp4Structure(HostMp4Inspection.Container container,HostMp4Inspection.Phases phases)throws IOException {enter();try{')
edit(T,'HostMp4Inspection.inspect(f,container,true,-1,false);','HostMp4Inspection.inspect(f,container,true,-1,false,phases);')
M='src/com/videokit/d1input/MatureContainerRemux.java'
edit(M,' public static HostMp4Inspection.Evidence writeAndInspect(HostMp4Inspection.Evidence input,TemporaryOutput output)throws Exception {',''' public static HostMp4Inspection.Evidence writeAndInspect(HostMp4Inspection.Evidence input,TemporaryOutput output)throws Exception {
  if(input==null)throw new IOException("MP4_REMUX_INPUT_UNPROVEN");throw new IOException("MUXER_JOB_KEEPER_REQUIRED");
 }
 public static HostMp4Inspection.Evidence writeAndInspect(HostMp4Inspection.Evidence input,TemporaryOutput output,MatureMuxerBinding binding,HostMp4Inspection.Phases reopenPhases)throws Exception {''')
edit(M,'  MatureMuxerBinding binding=new MatureMuxerBinding(output);int token=binding.addTrack(track.format);','  if(binding==null)throw new IOException("MUXER_JOB_KEEPER_REQUIRED");binding.allocate();int token=binding.addTrack(track.format);')
edit(M,'output.inspectHostMp4Structure(HostMp4Inspection.Container.FRAGMENTED_MP4);','output.inspectHostMp4Structure(HostMp4Inspection.Container.FRAGMENTED_MP4,reopenPhases);')
print('Same mature APIs with pre-registered binding and explicit hash/parse/seek phase hooks; old unowned mux entry rejects')
