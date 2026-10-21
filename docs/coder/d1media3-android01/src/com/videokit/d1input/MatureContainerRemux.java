package com.videokit.d1input;
import java.io.IOException;import java.nio.ByteBuffer;import java.util.Arrays;import androidx.media3.common.C;import androidx.media3.muxer.BufferInfo;
/** Existing six-sample binding only; no re-encoding, synthetic NAL or product READY. */
public final class MatureContainerRemux {
 public static HostMp4Inspection.Evidence writeAndInspect(HostMp4Inspection.Evidence input,TemporaryOutput output)throws Exception {
  if(input==null||!HostMp4Inspection.KIND.equals(input.kind)||!input.fullReadEof||!input.extractorEof||input.tracks.size()!=1)throw new IOException("MP4_REMUX_INPUT_UNPROVEN");
  HostMp4Inspection.Track track=input.tracks.get(0);
  if(!"video/avc".equals(track.format.sampleMimeType)||track.format.width!=256||track.format.height!=144||track.format.rotationDegrees!=0||track.format.drmInitData!=null||track.samples.size()!=6||track.format.initializationData.isEmpty()||(track.samples.get(0).flags&C.BUFFER_FLAG_KEY_FRAME)==0)throw new IOException("MP4_CAPTURE_FORMAT");
  int configBytes=0;for(byte[] config:track.format.initializationData){if(config.length==0||config.length>65536-configBytes)throw new IOException("MP4_CAPTURE_CONFIG");configBytes+=config.length;}
  // Validate every encoded capture and timestamp before creating the writer.
  long last=-1;for(HostMp4Inspection.Sample sample:track.samples){if(sample.timeUs<0||sample.timeUs>2000000||sample.timeUs<=last||sample.size<1||sample.size>262144||(sample.flags&(C.BUFFER_FLAG_ENCRYPTED|C.BUFFER_FLAG_END_OF_STREAM))!=0||sample.encodedCopy().length!=sample.size)throw new IOException("MP4_REMUX_INPUT_UNPROVEN");last=sample.timeUs;}
  MatureMuxerBinding binding=new MatureMuxerBinding(output);int token=binding.addTrack(track.format);
  for(HostMp4Inspection.Sample sample:track.samples)binding.sample(token,ByteBuffer.wrap(sample.encodedCopy()),new BufferInfo(sample.timeUs,sample.size,sample.flags));
  binding.finishWriter();HostMp4Inspection.Evidence reopened=output.inspectHostMp4Structure(HostMp4Inspection.Container.FRAGMENTED_MP4);
  if(reopened.tracks.size()!=1){output.rejectHostStructure();throw new IOException("MP4_REOPEN_TRACK_MISMATCH");}HostMp4Inspection.Track actual=reopened.tracks.get(0);
  if(!"video/avc".equals(actual.format.sampleMimeType)||actual.format.width!=256||actual.format.height!=144||actual.format.rotationDegrees!=0||actual.samples.size()!=6){output.rejectHostStructure();throw new IOException("MP4_REOPEN_TRACK_MISMATCH");}
  // Conservative oracle: the same library's Annex-B sample output and exact CSD
  // arrays, integer microsecond PTS. No undeclared prefix/timescale tolerance.
  if(actual.format.initializationData.size()!=track.format.initializationData.size()){output.rejectHostStructure();throw new IOException("MP4_REOPEN_CONFIG_MISMATCH");}
  for(int i=0;i<track.format.initializationData.size();i++)if(!Arrays.equals(actual.format.initializationData.get(i),track.format.initializationData.get(i))){output.rejectHostStructure();throw new IOException("MP4_REOPEN_CONFIG_MISMATCH");}
  for(int i=0;i<6;i++)if(actual.samples.get(i).timeUs!=track.samples.get(i).timeUs||actual.samples.get(i).size!=track.samples.get(i).size||!actual.samples.get(i).sha256.equals(track.samples.get(i).sha256)){output.rejectHostStructure();throw new IOException("MP4_REOPEN_SAMPLE_MISMATCH");}
  return reopened;
 }
 private MatureContainerRemux(){}
}
