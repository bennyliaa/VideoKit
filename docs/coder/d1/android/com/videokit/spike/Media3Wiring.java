package com.videokit.spike;

import android.content.Context;
import androidx.media3.common.C;
import androidx.media3.common.util.Clock;
import androidx.media3.datasource.DataSource;
import androidx.media3.datasource.DataSourceBitmapLoader;
import androidx.media3.exoplayer.ExoPlayer;
import androidx.media3.exoplayer.source.DefaultMediaSourceFactory;
import androidx.media3.muxer.Mp4Muxer;
import androidx.media3.muxer.Muxer;
import androidx.media3.muxer.MuxerException;
import androidx.media3.transformer.DefaultAssetLoaderFactory;
import androidx.media3.transformer.DefaultDecoderFactory;
import androidx.media3.transformer.Transformer;
import com.google.common.collect.ImmutableList;
import java.io.FileOutputStream;
import java.io.IOException;

/** Compile-checked wiring; actual playback/export requires authorized Android devices. */
public final class Media3Wiring {
    public interface AuthorizedOutput { FileOutputStream openSeekableTemporary() throws IOException; }
    public static ExoPlayer player(Context context,HostDataSource.Factory host) {
        return new ExoPlayer.Builder(context).setMediaSourceFactory(
            new DefaultMediaSourceFactory((DataSource.Factory)()->new HostDataSource(host))).build();
    }
    public static Transformer transformer(Context context,HostDataSource.Factory host,AuthorizedOutput output) {
        DataSource.Factory sources=()->new HostDataSource(host);
        DefaultAssetLoaderFactory assets=new DefaultAssetLoaderFactory(context,
            new DefaultDecoderFactory.Builder(context).build(),Clock.DEFAULT,
            new DefaultMediaSourceFactory(sources),new DataSourceBitmapLoader(context));
        // The factory receives Media3's path argument but does not use it to open a file.
        // All writes use the output descriptor explicitly authorized by the host Sink.
        Muxer.Factory muxers=new Muxer.Factory(){
            private boolean opened;
            public synchronized Muxer create(String ignoredPath)throws MuxerException {
                if(opened)throw new MuxerException("D1_SINGLE_OUTPUT_ONLY",new IOException("REOPEN_REJECTED"));
                opened=true;
                try{return new Mp4Muxer.Builder(output.openSeekableTemporary()).build();}
                catch(IOException e){throw new MuxerException("OUTPUT_OPEN_FAILED",e);}
            }
            public ImmutableList<String> getSupportedSampleMimeTypes(int type){
                if(type==C.TRACK_TYPE_VIDEO)return ImmutableList.of("video/avc");
                if(type==C.TRACK_TYPE_AUDIO)return ImmutableList.of("audio/mp4a-latm");
                return ImmutableList.of();
            }
        };
        return new Transformer.Builder(context).setAssetLoaderFactory(assets).setMuxerFactory(muxers).build();
    }
}
