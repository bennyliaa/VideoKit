package com.videokit.d1input;
import androidx.media3.common.Format;import androidx.media3.muxer.*;import java.nio.ByteBuffer;
/** Compiles against the REAL pinned Media3 1.9.3 muxer. No codec/container implementation.
 * Empty/generated host fixtures never constitute a compressed-media validation receipt. */
public final class MatureMuxerBinding {
 private final TemporaryOutput sink;private final FragmentedMp4Muxer original;private int track=-1,samples;private long last=-1;private boolean closeEntered;
 public MatureMuxerBinding(TemporaryOutput sink){this.sink=sink;original=com.videokit.spike.c14.E6Muxer.create(sink.channel());}
 public int addTrack(Format f)throws Exception{if(track>=0||!"video/avc".equals(f.sampleMimeType)||f.width!=256||f.height!=144||f.rotationDegrees!=0)throw new java.io.IOException("E4_MUX_TRACK_INVALID");track=original.addTrack(f);return track;}
 public void sample(int token,ByteBuffer data,BufferInfo info)throws Exception{if(closeEntered||track<0||token!=track||samples>=6||info.size<1||info.size>262144||data.remaining()<info.size||info.presentationTimeUs<0||info.presentationTimeUs>2000000||last>=0&&info.presentationTimeUs<=last)throw new java.io.IOException("E4_MUX_SAMPLE_BUDGET");original.writeSampleData(token,data,info);samples++;last=info.presentationTimeUs;}
 /** Original six-sample EOS/finalize helper; never build an unbounded new codec/container path. */
 public void finishWriter()throws Exception{if(closeEntered)throw new java.io.IOException("MUXER_ORIGINAL_CLOSE_UNPROVEN");closeEntered=true;com.videokit.spike.c14.E6Muxer.finish(original,track,samples,last);sink.channel().close();sink.finishWriter();}
}
