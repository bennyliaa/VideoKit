package com.videokit.d1input;

import androidx.media3.common.*;
import androidx.media3.common.util.ParsableByteArray;
import androidx.media3.datasource.DataSpec;
import androidx.media3.extractor.*;
import androidx.media3.extractor.mp4.*;
import java.io.*;
import java.security.*;
import java.util.*;

/** Finite D1 MP4 experiment using the actual pinned extractors. This is NOT an
 * isolated validator, a decoder, or permission to READY/COMMIT. Caller retains
 * the original factory until its original workers have physically returned.
 * Byte/callback limits do not prove Media3's internal allocation bounds. */
public final class HostMp4Inspection {
 public static final String KIND="HOST_MEDIA3_MP4_STRUCTURE_V1";
 public static final long INPUT_LIMIT=8L*1024*1024;
 public enum Container { MP4, FRAGMENTED_MP4 }
 public static final class Sample {
  public final long timeUs;public final int flags,size;public final String sha256;
  private final byte[] encoded;
  Sample(long t,int f,byte[] b,boolean capture){timeUs=t;flags=f;size=b.length;sha256=hex(digest().digest(b));encoded=capture?b:null;}
  /** Copy of a proven bounded captured sample; never synthesizes an encoded frame. */
  public byte[] encodedCopy(){if(encoded==null)throw new IllegalStateException("ENCODED_CAPTURE_NOT_ADMITTED");return encoded.clone();}
 }
 public static final class Track {
  public final int id,type;public final Format format;public final List<Sample> samples;
  Track(Port p){id=p.id;type=p.type;format=p.format;samples=List.copyOf(p.samples);}
 }
 public static final class Evidence {
  public final String kind=KIND,sha256;public final long bytes,physicalBytesRead;
  public final List<Track> tracks;public final int extractorSeeks,seekReplaySamples;
  public final boolean fullReadEof,extractorEof,seekable;public final long durationUs;
  Evidence(String hash,long bytes,Reader r,Output o,int seeks,int replay){sha256=hash;this.bytes=bytes;physicalBytesRead=r.readBytes;List<Track> copy=new ArrayList<>();for(Port p:o.tracks.values())copy.add(new Track(p));tracks=List.copyOf(copy);extractorSeeks=seeks;seekReplaySamples=replay;fullReadEof=true;extractorEof=true;seekable=o.seek!=null&&o.seek.isSeekable();durationUs=o.seek==null?C.TIME_UNSET:o.seek.getDurationUs();}
 }
 static final class Reader implements DataReader {
  final HostDataSource ds;long readBytes;
  Reader(HostDataSource ds){this.ds=ds;}
  public int read(byte[] b,int off,int len)throws IOException{
   if(len==0)return 0;if(readBytes>=INPUT_LIMIT)throw new IOException("MP4_INPUT_BYTE_BUDGET");
   int count=(int)Math.min(Math.min(65536L,len),INPUT_LIMIT-readBytes);
   int n=ds.read(b,off,count);if(n>0){readBytes+=n;if(readBytes>INPUT_LIMIT)throw new IOException("MP4_INPUT_BYTE_BUDGET");}return n;
  }
 }
 /** Capability and scope rejection precede DataSource creation/open and library construction.
  * seekUs=-1 means scan only. A nonnegative time requests one real SeekMap replay.
  * capture=true accepts only a single six-sample AVC256x144 stream, without adaptation. */
 public static Evidence inspect(HostInputFactory factory,Container container,boolean mp4ReadCapability,long seekUs,boolean capture)throws IOException {
  Objects.requireNonNull(factory);factory.worker.requireWorker();
  requireAdmission(container,mp4ReadCapability,seekUs);
  Extractor extractor=null;HostDataSource ds=null;
  try {
   extractor=container==Container.MP4?new Mp4Extractor():new FragmentedMp4Extractor();
   ds=factory.createDataSource();Reader reader=new Reader(ds);MessageDigest hash=digest();byte[] block=new byte[65536];long bytes=0;
   long announced=ds.open(new DataSpec(factory.uri()));if(announced>INPUT_LIMIT)throw new IOException("MP4_INPUT_BYTE_BUDGET");int n;
   while((n=reader.read(block,0,block.length))!=-1){bytes+=n;hash.update(block,0,n);}
   if(bytes==0||announced>=0&&announced!=bytes)throw new IOException("MP4_INPUT_TRUNCATED");ds.close();
   Output output=new Output(capture);extractor.init(output);Scan scan=new Scan(factory,ds,reader,extractor,bytes);
   scan.open(0);if(!extractor.sniff(scan.input))throw new IOException("MP4_CONTAINER_MISMATCH");scan.input.resetPeekPosition();scan.drain();
   output.complete();int replay=0;
   if(seekUs>=0){
    if(output.seek==null||!output.seek.isSeekable()||output.seek.getDurationUs()<0||seekUs>output.seek.getDurationUs())throw new IOException("MP4_SEEK_UNSUPPORTED");
    SeekPoint point=output.seek.getSeekPoints(seekUs).first;scan.position(point.position);output.replay=true;extractor.seek(point.position,point.timeUs);scan.drain();replay=output.replaySamples;
   }
   return new Evidence(hex(hash.digest()),bytes,reader,output,scan.seeks,replay);
  }catch(IOException e){throw e;}catch(Throwable t){throw Failures.io(t,"MP4_PLATFORM_OR_STRUCTURE_UNAVAILABLE");}
  finally {try{if(extractor!=null)extractor.release();}finally{if(ds!=null)ds.close();}}
 }
 public static void requireAdmission(Container c,boolean capability,long seekUs)throws IOException{
  if(!capability||c==null)throw new IOException("MP4_CAPABILITY_UNSUPPORTED");
  if(seekUs< -1||seekUs>2000000)throw new IOException("MP4_SEEK_BOUNDS");
 }
 private static final class Scan {
  final HostInputFactory f;final HostDataSource ds;final Reader reader;final Extractor extractor;final long bytes;DefaultExtractorInput input;int seeks,steps;
  Scan(HostInputFactory f,HostDataSource d,Reader r,Extractor e,long bytes){this.f=f;ds=d;reader=r;extractor=e;this.bytes=bytes;}
  void open(long at)throws IOException{long remaining=ds.open(new DataSpec(f.uri(),at,-1));input=new DefaultExtractorInput(reader,at,remaining<0?-1:at+remaining);}
  void position(long at)throws IOException{if(at<0||at>bytes||at>INPUT_LIMIT||++seeks>16)throw new IOException("MP4_SEEK_BOUNDS");ds.close();open(at);}
  void drain()throws IOException{PositionHolder p=new PositionHolder();while(++steps<=4096){int result=extractor.read(input,p);if(result==Extractor.RESULT_END_OF_INPUT)return;if(result==Extractor.RESULT_SEEK)position(p.position);else if(result!=Extractor.RESULT_CONTINUE)throw new IOException("MP4_EXTRACTOR_RESULT");}throw new IOException("MP4_EXTRACTOR_STEP_BUDGET");}
 }
 private static final class Output implements ExtractorOutput {
  final Map<Integer,Port> tracks=new LinkedHashMap<>();final boolean capture;boolean ended,replay;SeekMap seek;int replaySamples;
  Output(boolean capture){this.capture=capture;}
  public TrackOutput track(int id,int type){Port p=tracks.get(id);if(p!=null){if(p.type!=type)throw bad("MP4_TRACK_CHANGED");return p;}if(ended||tracks.size()>=2||capture&&!tracks.isEmpty())throw bad("MP4_TRACK_BUDGET");p=new Port(this,id,type);tracks.put(id,p);return p;}
  public void endTracks(){ended=true;}
  public void seekMap(SeekMap map){seek=Objects.requireNonNull(map);}
  void complete(){if(!ended||tracks.isEmpty())throw bad("MP4_NO_TRACKS");for(Port p:tracks.values())if(p.format==null||p.samples.isEmpty()||p.pending.size()!=0||capture&&p.samples.size()!=6)throw bad("MP4_INCOMPLETE_SAMPLES");}
 }
 private static final class Port implements TrackOutput {
  final Output owner;final int id,type;Format format;final List<Sample> samples=new ArrayList<>();final ByteArrayOutputStream pending=new ByteArrayOutputStream();final byte[] scratch=new byte[65536];long last=-1;
  Port(Output o,int id,int type){owner=o;this.id=id;this.type=type;}
  public void format(Format f){if(format!=null&&!format.equals(f))throw bad("MP4_FORMAT_CHANGED");if(!"video/avc".equals(f.sampleMimeType)&&!"audio/mp4a-latm".equals(f.sampleMimeType))throw bad("MP4_TRACK_UNSUPPORTED");if(owner.capture&&(!"video/avc".equals(f.sampleMimeType)||f.width!=256||f.height!=144||f.rotationDegrees!=0))throw bad("MP4_CAPTURE_FORMAT");format=f;}
  private void budget(int len,int part){if(part!=SAMPLE_DATA_PART_MAIN||len<0||len>262144-pending.size())throw bad("MP4_SAMPLE_BUDGET");}
  public int sampleData(DataReader r,int length,boolean allowEnd,int part)throws IOException{budget(length,part);int n=r.read(scratch,0,Math.min(length,scratch.length));if(n<0){if(!allowEnd)throw new EOFException();return -1;}if(n==0)throw new IOException("MP4_ZERO_SAMPLE_READ");pending.write(scratch,0,n);return n;}
  public void sampleData(ParsableByteArray b,int length,int part){budget(length,part);int left=length;while(left>0){int n=Math.min(left,scratch.length);b.readBytes(scratch,0,n);pending.write(scratch,0,n);left-=n;}}
  public void sampleMetadata(long time,int flags,int size,int offset,CryptoData crypto){
   if(crypto!=null||offset!=0||size<1||size!=pending.size()||time<0)throw bad("MP4_SAMPLE_BOUNDARY");
   if(owner.replay){if(++owner.replaySamples>1024)throw bad("MP4_REPLAY_BUDGET");pending.reset();return;}
   if(samples.size()>=512||owner.capture&&(samples.size()>=6||time>2000000||last>=0&&time<=last))throw bad("MP4_SAMPLE_BUDGET");
   samples.add(new Sample(time,flags,pending.toByteArray(),owner.capture));pending.reset();last=time;
  }
 }
 private static IllegalStateException bad(String code){return new IllegalStateException(code);}
 private static MessageDigest digest(){try{return MessageDigest.getInstance("SHA-256");}catch(NoSuchAlgorithmException e){throw new AssertionError(e);}}
 private static String hex(byte[] b){StringBuilder s=new StringBuilder();for(byte v:b)s.append(String.format(Locale.ROOT,"%02x",v&255));return s.toString();}
 private HostMp4Inspection(){}
}
