package com.videokit.spike.c14;
import androidx.media3.muxer.FragmentedMp4Muxer;
import androidx.media3.muxer.BufferInfo;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.WritableByteChannel;

/** Six bounded samples span <=2s. Keep their adjacent PTS together; no fragment-boundary extrapolation. */
public final class E6Muxer {
    public static final int FRAGMENT_MS=3000;
    public static FragmentedMp4Muxer create(WritableByteChannel channel){
        return new FragmentedMp4Muxer.Builder(channel).setFragmentDurationMs(FRAGMENT_MS).setSampleCopyingEnabled(true).build();
    }
    public static void finish(FragmentedMp4Muxer muxer,int track,int count,long last)throws Exception {
        if(count!=6 || last<0 || last>2000000 || track<0)throw new IOException("E6_MUX_INCOMPLETE");
        // EOS supplies the final sample's duration only; it is an empty metadata marker, never a seventh frame.
        muxer.writeSampleData(track,ByteBuffer.allocate(0),new BufferInfo(last+200000,0,4));
        muxer.close();
    }
    private E6Muxer(){}
}
