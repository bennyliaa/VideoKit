package com.videokit.spike.c10;

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
        return player(context,runtime,leases,generation,routes,new RoutingDataSource.Group());
    }
    public static ExoPlayer player(Context context,AsyncReadBridge.Runtime runtime,LeaseRegistry leases,long generation,Map<String,AsyncReadBridge.Provider> routes,RoutingDataSource.Group group){
        ExoPlayer p=new ExoPlayer.Builder(context).setReleaseTimeoutMs(1500).setMediaSourceFactory(new DefaultMediaSourceFactory(()->new RoutingDataSource(runtime,leases,generation,routes,group),new TracingExtractors())).build();
        p.setAudioAttributes(androidx.media3.common.AudioAttributes.DEFAULT,true);p.setHandleAudioBecomingNoisy(true);p.addAnalyticsListener(new AudioDiagnostics());return p;
    }
    public static MediaItem item(String uri,boolean externalSrt){
        MediaItem.Builder item=new MediaItem.Builder().setUri(uri);
        if(externalSrt)item.setSubtitleConfigurations(java.util.List.of(new MediaItem.SubtitleConfiguration.Builder(android.net.Uri.parse(SRT)).setMimeType("application/x-subrip").setLanguage("zh").setLabel("SRT").setSelectionFlags(C.SELECTION_FLAG_DEFAULT).build()));
        return item.build();
    }
    public static Transformer transformer(Context context,AsyncReadBridge.Runtime runtime,LeaseRegistry leases,long generation,Map<String,AsyncReadBridge.Provider> routes,AuthorizedSink sink,Transformer.Listener listener){
        return transformer(context,runtime,leases,generation,routes,sink,listener,null);
    }
    public static Transformer transformer(Context context,AsyncReadBridge.Runtime runtime,LeaseRegistry leases,long generation,Map<String,AsyncReadBridge.Provider> routes,AuthorizedSink sink,Transformer.Listener listener,RoutingDataSource.Group group){
        DataSource.Factory source=group==null?factory(runtime,leases,generation,routes):()->new RoutingDataSource(runtime,leases,generation,routes,group);
        DefaultAssetLoaderFactory assets=new DefaultAssetLoaderFactory(context,new DefaultDecoderFactory.Builder(context).build(),Clock.DEFAULT,new DefaultMediaSourceFactory(source),new DataSourceBitmapLoader(context));
        return new Transformer.Builder(context).setAssetLoaderFactory(assets).setMuxerFactory(sink.muxers()).setVideoMimeType("video/avc").setAudioMimeType("audio/mp4a-latm").addListener(listener).build();
    }
    public static Transformer captureTransformer(Context context,AsyncReadBridge.Runtime runtime,LeaseRegistry leases,long generation,Map<String,AsyncReadBridge.Provider> routes,VideoFrameSink sink,Transformer.Listener listener,RoutingDataSource.Group group,CaptureInputKind kind,CaptureFormatEvidence evidence){
        DataSource.Factory source=()->new RoutingDataSource(runtime,leases,generation,routes,group);
        androidx.media3.extractor.ExtractorsFactory typed=()->new androidx.media3.extractor.Extractor[]{captureExtractor(kind,stage->{evidence.record(stage);StageLog.event(stage,"source="+kind);})};
        DefaultAssetLoaderFactory assets=new DefaultAssetLoaderFactory(context,new CaptureDecoderFactory(new DefaultDecoderFactory.Builder(context).build()),Clock.DEFAULT,new DefaultMediaSourceFactory(source,new TracingExtractors(typed)),new DataSourceBitmapLoader(context));
        return new Transformer.Builder(context).setAssetLoaderFactory(assets).setMuxerFactory(sink.muxers()).setVideoMimeType("video/avc").addListener(listener).build();
    }
    public static FormatGuardExtractor captureExtractor(CaptureInputKind kind,java.util.function.Consumer<String> events){
        java.util.Objects.requireNonNull(kind);
        return new FormatGuardExtractor(kind==CaptureInputKind.AVI?new androidx.media3.extractor.avi.AviExtractor():new androidx.media3.extractor.mp4.Mp4Extractor(),events);
    }
}
