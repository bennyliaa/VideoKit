package com.videokit.spike.e4;
import android.media.*;
import java.io.*;
import java.util.*;
/** Adapted from frozen d1c14/android/com/videokit/spike/c14/EncoderCapabilities.java.
 * Only public fixed-format capabilities. No source, URI or arbitrary MediaFormat string logging. */
final class E4EncoderCapabilities {
    volatile String enumeratingName="NONE";
    private final Map<String,MediaCodecInfo.CodecCapabilities> capabilities=new HashMap<>();
    List<E4EncoderNegotiation.Candidate> enumerate(java.util.function.Consumer<String> phase)throws Exception{
        phase.accept("ENUMERATE");MediaCodecInfo[] infos=new MediaCodecList(MediaCodecList.REGULAR_CODECS).getCodecInfos();if(infos.length>128)throw new IOException("PIPE_ENCODER_METADATA_BUDGET");List<E4EncoderNegotiation.Descriptor> descriptors=new ArrayList<>();
        for(MediaCodecInfo info:infos){if(!info.isEncoder() || info.isAlias())continue;String[] types=info.getSupportedTypes();if(types.length>32)throw new IOException("PIPE_ENCODER_METADATA_BUDGET");boolean avc=false;for(String type:types)avc|="video/avc".equalsIgnoreCase(type);if(!avc)continue;if(descriptors.size()>=16)throw new IOException("PIPE_ENCODER_METADATA_BUDGET");
            String name=info.getName(),canonical=info.getCanonicalName();E4EncoderNegotiation.identifier(name);E4EncoderNegotiation.identifier(canonical);enumeratingName=name;phase.accept("CAPABILITY");MediaCodecInfo.CodecCapabilities caps=info.getCapabilitiesForType("video/avc");
            if(caps.colorFormats==null || caps.profileLevels==null || caps.colorFormats.length>64 || caps.profileLevels.length>64)throw new IOException("PIPE_ENCODER_METADATA_BUDGET");int[] profiles=new int[caps.profileLevels.length*2];for(int i=0;i<caps.profileLevels.length;i++){profiles[2*i]=caps.profileLevels[i].profile;profiles[2*i+1]=caps.profileLevels[i].level;}
            MediaCodecInfo.VideoCapabilities v=caps.getVideoCapabilities();if(v==null)throw new IOException("PIPE_ENCODER_CAPABILITY_FAILED");int wa=v.getWidthAlignment(),ha=v.getHeightAlignment();
            boolean geometry=wa>0 && ha>0 && 256%wa==0 && 144%ha==0 && v.getBitrateRange().contains(600000) && v.areSizeAndRateSupported(256,144,5);
            E4EncoderNegotiation.Descriptor descriptor=new E4EncoderNegotiation.Descriptor(name,canonical,info.isHardwareAccelerated(),info.isSoftwareOnly(),info.isVendor(),geometry,caps.colorFormats,profiles);descriptors.add(descriptor);capabilities.put(name,caps);
        }
        return E4EncoderNegotiation.plan(descriptors);
    }
    static MediaFormat format(E4EncoderNegotiation.Candidate c){MediaFormat f=MediaFormat.createVideoFormat("video/avc",256,144);f.setInteger(MediaFormat.KEY_COLOR_FORMAT,c.color);f.setInteger(MediaFormat.KEY_BIT_RATE,600000);f.setInteger(MediaFormat.KEY_FRAME_RATE,5);f.setInteger(MediaFormat.KEY_I_FRAME_INTERVAL,1);if(c.baseline)f.setInteger(MediaFormat.KEY_PROFILE,MediaCodecInfo.CodecProfileLevel.AVCProfileBaseline);return f;}
    boolean supported(E4EncoderNegotiation.Candidate c){MediaCodecInfo.CodecCapabilities caps=capabilities.get(c.codec.name);return caps!=null && caps.isFormatSupported(format(c));}
}
