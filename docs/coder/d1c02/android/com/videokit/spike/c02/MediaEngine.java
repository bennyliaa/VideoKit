package com.videokit.spike.c02;

import android.content.Context;
import androidx.media3.common.C;
import androidx.media3.common.MediaItem;
import androidx.media3.common.util.Clock;
import androidx.media3.datasource.DataSource;
import androidx.media3.datasource.DataSourceBitmapLoader;
import androidx.media3.exoplayer.ExoPlayer;
import androidx.media3.exoplayer.source.DefaultMediaSourceFactory;
import androidx.media3.transformer.DefaultAssetLoaderFactory;
import androidx.media3.transformer.DefaultDecoderFactory;
import androidx.media3.transformer.Transformer;
import java.util.Map;

public final class MediaEngine {
    public static final String MP4="vkspike://source/mp4",MKV="vkspike://source/mkv",AVI="vkspike://source/avi",SRT="vkspike://subtitle/srt";
    private static DataSource.Factory factory(AsyncReadBridge.Runtime runtime,LeaseRegistry leases,long generation,Map<String,AsyncReadBridge.Provider> routes){return ()->new RoutingDataSource(runtime,leases,generation,routes);}
    public static ExoPlayer player(Context context,AsyncReadBridge.Runtime runtime,LeaseRegistry leases,long generation,Map<String,AsyncReadBridge.Provider> routes){
        return new ExoPlayer.Builder(context).setMediaSourceFactory(new DefaultMediaSourceFactory(factory(runtime,leases,generation,routes))).build();
    }
    public static MediaItem item(String uri,boolean externalSrt){
        MediaItem.Builder item=new MediaItem.Builder().setUri(uri);
        if(externalSrt)item.setSubtitleConfigurations(java.util.List.of(new MediaItem.SubtitleConfiguration.Builder(android.net.Uri.parse(SRT)).setMimeType("application/x-subrip").setLanguage("zh").setLabel("SRT").setSelectionFlags(C.SELECTION_FLAG_DEFAULT).build()));
        return item.build();
    }
    public static Transformer transformer(Context context,AsyncReadBridge.Runtime runtime,LeaseRegistry leases,long generation,Map<String,AsyncReadBridge.Provider> routes,AuthorizedSink sink,Transformer.Listener listener){
        DataSource.Factory source=factory(runtime,leases,generation,routes);
        DefaultAssetLoaderFactory assets=new DefaultAssetLoaderFactory(context,new DefaultDecoderFactory.Builder(context).build(),Clock.DEFAULT,new DefaultMediaSourceFactory(source),new DataSourceBitmapLoader(context));
        return new Transformer.Builder(context).setAssetLoaderFactory(assets).setMuxerFactory(sink.muxers()).setVideoMimeType("video/avc").setAudioMimeType("audio/mp4a-latm").addListener(listener).build();
    }
}
