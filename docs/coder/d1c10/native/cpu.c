/* Independent VideoKit debug adapter. FFmpeg libraries remain dynamically linked. */
#include <jni.h>
#include <stdint.h>
#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/resource.h>
#include <string.h>
#include <libavformat/avformat.h>
#include <libavcodec/avcodec.h>
#include <libavutil/imgutils.h>
#include <libavutil/time.h>
#include <libswscale/swscale.h>
#define OUT_W 256
#define OUT_H 144
#define OUT_STRIDE (OUT_W * 4)
#define OUT_BYTES (OUT_STRIDE * OUT_H)
extern size_t vk_c09_current(void);
extern size_t vk_c09_peak(void);
extern int vk_c09_probe(void);
JNIEXPORT jint JNICALL Java_com_videokit_spike_c10_NativeCpu_quotaProbe(JNIEnv *e,jclass type){(void)e;(void)type;return vk_c09_probe();}
typedef struct {JNIEnv *env; jobject cb; jmethodID read, cancel, frame, stage; int64_t position,length,deadline,bytes; int reads;} Input;
static int stage(Input *s,int value){(*s->env)->CallVoidMethod(s->env,s->cb,s->stage,(jint)value);return (*s->env)->ExceptionCheck(s->env)?-1:0;}
static int interrupted(void *opaque) {
    Input *s=opaque;
    if(av_gettime_relative()>s->deadline || (*s->env)->ExceptionCheck(s->env))return 1;
    jboolean value=(*s->env)->CallBooleanMethod(s->env,s->cb,s->cancel);
    return value || (*s->env)->ExceptionCheck(s->env);
}
static int read_packet(void *opaque,uint8_t *target,int requested) {
    Input *s=opaque;JNIEnv *e=s->env;
    if(interrupted(s) || ++s->reads>8192 || s->bytes>64LL*1024*1024)return AVERROR_EXIT;
    if(s->position==s->length)return AVERROR_EOF;
    int count=requested<65536?requested:65536;
    if(count<1 || s->position<0 || s->position>s->length)return AVERROR(EINVAL);
    if(count>s->length-s->position)count=(int)(s->length-s->position);
    if(s->bytes+count>64LL*1024*1024)return AVERROR_EXIT;
    jbyteArray bytes=(*e)->CallObjectMethod(e,s->cb,s->read,(jlong)s->position,(jint)count);
    if((*e)->ExceptionCheck(e) || !bytes)return AVERROR(EIO);
    jsize n=(*e)->GetArrayLength(e,bytes);
    if(n<0 || n>count){(*e)->DeleteLocalRef(e,bytes);return AVERROR_INVALIDDATA;}
    if(n)(*e)->GetByteArrayRegion(e,bytes,0,n,(jbyte*)target);
    (*e)->DeleteLocalRef(e,bytes);
    if((*e)->ExceptionCheck(e))return AVERROR(EIO);
    s->position+=n;s->bytes+=n;return n?n:AVERROR_EOF;
}
static int64_t seek_input(void *opaque,int64_t offset,int whence) {
    Input *s=opaque;if(interrupted(s))return AVERROR_EXIT;
    whence &= ~AVSEEK_FORCE;
    if(whence==AVSEEK_SIZE)return s->length;
    int64_t origin=whence==SEEK_SET?0:whence==SEEK_CUR?s->position:whence==SEEK_END?s->length:-1;
    if(origin<0 || (offset>0 && origin>INT64_MAX-offset) || (offset<0 && offset < -origin))return AVERROR(EINVAL);
    int64_t next=origin+offset;if(next<0 || next>s->length)return AVERROR(EINVAL);
    s->position=next;return next;
}
JNIEXPORT jint JNICALL Java_com_videokit_spike_c10_NativeCpu_decode(JNIEnv *e,jclass type,jobject cb,jlong length,jlong target,jint kind) {
    (void)type;int result=-1,index=-1,opened=0;AVFormatContext *format=NULL;AVCodecContext *codec=NULL;
    AVIOContext *io=NULL;AVFrame *frame=NULL;AVPacket *packet=NULL;struct SwsContext *sws=NULL;uint8_t *rgba=NULL,*buffer=NULL;AVDictionary *options=NULL;
    if(length<1 || length>(1LL<<40) || target<0 || target>86400000000LL-2000000 || (kind!=1 && kind!=2))return -2;
    jclass cls=(*e)->GetObjectClass(e,cb);
    Input input={.env=e,.cb=cb,.length=length,.deadline=av_gettime_relative()+20000000};
    input.read=(*e)->GetMethodID(e,cls,"readAt","(JI)[B");input.cancel=(*e)->GetMethodID(e,cls,"isCancelled","()Z");input.frame=(*e)->GetMethodID(e,cls,"onFrame","([BJJIIIJIIIJJ)V");input.stage=(*e)->GetMethodID(e,cls,"onStage","(I)V");
    (*e)->DeleteLocalRef(e,cls);if((*e)->ExceptionCheck(e))return -3;
    /* Self-process metadata only, never a source path. Fail closed before demux/codec allocation.
       Limits bound additional address space, not RSS committed inside pre-existing ART reservations. */
    unsigned long long pages=0;FILE *statm=fopen("/proc/self/statm","r");
    if(!statm)return -4;int scanned=fscanf(statm,"%llu",&pages);fclose(statm);
    long page_size=sysconf(_SC_PAGESIZE);if(scanned!=1 || page_size<4096 || pages>(UINT64_MAX-201326592)/(unsigned long)page_size)return -4;
    uint64_t baseline=pages*(unsigned long)page_size,limit=baseline+201326592;
    struct rlimit prior;if(getrlimit(RLIMIT_AS,&prior)!=0 || (prior.rlim_max!=RLIM_INFINITY && limit>prior.rlim_max))return -4;
    struct rlimit bounded={(rlim_t)limit,(rlim_t)limit};if(setrlimit(RLIMIT_AS,&bounded)!=0)return -4;
    jclass budget_class=(*e)->GetObjectClass(e,cb);jmethodID budget=(*e)->GetMethodID(e,budget_class,"onBudget","(JJLjava/lang/String;)V");(*e)->DeleteLocalRef(e,budget_class);
    if((*e)->ExceptionCheck(e))return -4;
    jstring version=(*e)->NewStringUTF(e,av_version_info());if(!version)return -4;
    (*e)->CallVoidMethod(e,cb,budget,(jlong)baseline,(jlong)limit,version);(*e)->DeleteLocalRef(e,version);if((*e)->ExceptionCheck(e))return -4;
    av_max_alloc(16*1024*1024);
    buffer=av_malloc(65536);if(!buffer)goto cleanup;
    io=avio_alloc_context(buffer,65536,0,&input,read_packet,NULL,seek_input);if(!io)goto cleanup;buffer=NULL;
    format=avformat_alloc_context();if(!format)goto cleanup;
    format->pb=io;format->flags|=AVFMT_FLAG_CUSTOM_IO;format->interrupt_callback=(AVIOInterruptCB){interrupted,&input};
    format->probesize=131072;format->max_analyze_duration=1000000;format->max_probe_packets=64;format->max_streams=8;
    av_dict_set(&options,"format_whitelist",kind==1?"avi":"mov",0);
    const AVInputFormat *demux=av_find_input_format(kind==1?"avi":"mov");if(!demux)goto cleanup;
    if(avformat_open_input(&format,NULL,demux,&options)<0)goto cleanup;opened=1;
    if(stage(&input,1)<0)goto cleanup;
    /* Headers-only discovery: no implicit probe decoder can bypass max_pixels. */
    if(format->nb_streams>8)goto cleanup;
    for(unsigned i=0;i<format->nb_streams;i++)if(format->streams[i]->codecpar->codec_type==AVMEDIA_TYPE_VIDEO){index=(int)i;break;}
    if(index<0)goto cleanup;
    AVStream *stream=format->streams[index];enum AVCodecID id=stream->codecpar->codec_id;
    if(id!=(kind==1?AV_CODEC_ID_MPEG4:AV_CODEC_ID_H264) || stream->time_base.num<=0 || stream->time_base.den<=0
            || stream->codecpar->width<1 || stream->codecpar->height<1 || stream->codecpar->width>1920
            || stream->codecpar->height>1080 || (int64_t)stream->codecpar->width*stream->codecpar->height>1920LL*1080){stage(&input,6);goto cleanup;}
    if(stage(&input,2)<0)goto cleanup;
    const AVCodec *decoder=avcodec_find_decoder(id);if(!decoder)goto cleanup;
    codec=avcodec_alloc_context3(decoder);if(!codec || avcodec_parameters_to_context(codec,stream->codecpar)<0)goto cleanup;
    codec->thread_count=1;codec->max_pixels=1920LL*1080;
    if(avcodec_open2(codec,decoder,NULL)<0)goto cleanup;
    if(stage(&input,3)<0)goto cleanup;
    int64_t seek=av_rescale_q(target,(AVRational){1,1000000},stream->time_base);
    if(target>0 && av_seek_frame(format,index,seek,AVSEEK_FLAG_BACKWARD)<0)goto cleanup;
    if(stage(&input,4)<0)goto cleanup;
    avcodec_flush_buffers(codec);frame=av_frame_alloc();packet=av_packet_alloc();rgba=av_malloc(OUT_BYTES);
    if(!frame || !packet || !rgba)goto cleanup;
    for(int n=0;n<4096 && !interrupted(&input);n++) {
        int read=av_read_frame(format,packet);
        if(read<0){if(read!=AVERROR_EOF)goto cleanup;if(avcodec_send_packet(codec,NULL)<0)goto cleanup;}
        else if(packet->stream_index!=index){av_packet_unref(packet);continue;}
        else {int sent=avcodec_send_packet(codec,packet);av_packet_unref(packet);if(sent<0)goto cleanup;}
        for(;;){int got=avcodec_receive_frame(codec,frame);if(got==AVERROR(EAGAIN) || got==AVERROR_EOF)break;if(got<0)goto cleanup;
            int best=frame->pts==AV_NOPTS_VALUE;int64_t raw=best?frame->best_effort_timestamp:frame->pts;if(raw==AV_NOPTS_VALUE)goto cleanup;
            int64_t pts=av_rescale_q(raw,stream->time_base,(AVRational){1,1000000});
            if(frame->width<1 || frame->height<1 || frame->width>1920 || frame->height>1080 || (int64_t)frame->width*frame->height>1920LL*1080)goto cleanup;
            if(pts<target){av_frame_unref(frame);continue;}if(pts>target+2000000 || pts>86400000000LL)goto cleanup;
            sws=sws_getContext(frame->width,frame->height,(enum AVPixelFormat)frame->format,OUT_W,OUT_H,AV_PIX_FMT_RGBA,SWS_BILINEAR,NULL,NULL,NULL);if(!sws)goto cleanup;
            uint8_t *planes[4]={rgba,NULL,NULL,NULL};int strides[4]={OUT_STRIDE,0,0,0};
            if(sws_scale(sws,(const uint8_t *const*)frame->data,frame->linesize,0,frame->height,planes,strides)!=OUT_H)goto cleanup;
            struct rusage usage;if(getrusage(RUSAGE_SELF,&usage)!=0 || usage.ru_maxrss<1 || usage.ru_maxrss>262144)goto cleanup;
            if(stage(&input,5)<0)goto cleanup;
            jbyteArray bytes=(*e)->NewByteArray(e,OUT_BYTES);if(!bytes)goto cleanup;
            (*e)->SetByteArrayRegion(e,bytes,0,OUT_BYTES,(const jbyte*)rgba);
            size_t quota_current=vk_c09_current(),quota_peak=vk_c09_peak();
            if(!(*e)->ExceptionCheck(e))(*e)->CallVoidMethod(e,cb,input.frame,bytes,(jlong)pts,(jlong)raw,(jint)OUT_W,(jint)OUT_H,(jint)OUT_STRIDE,(jlong)usage.ru_maxrss,(jint)stream->time_base.num,(jint)stream->time_base.den,(jint)best,(jlong)quota_peak,(jlong)quota_current);
            (*e)->DeleteLocalRef(e,bytes);if((*e)->ExceptionCheck(e))goto cleanup;result=0;goto cleanup;
        }
        if(read==AVERROR_EOF)break;
    }
cleanup:
    av_dict_free(&options);sws_freeContext(sws);av_free(rgba);av_packet_free(&packet);av_frame_free(&frame);avcodec_free_context(&codec);
    if(opened)avformat_close_input(&format);else avformat_free_context(format);
    if(io){av_freep(&io->buffer);avio_context_free(&io);}av_free(buffer);
    return result;
}
