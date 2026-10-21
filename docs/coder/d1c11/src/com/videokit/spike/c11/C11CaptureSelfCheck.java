package com.videokit.spike.c11;
/** Independent frame contract counterexamples; formal dual-track rule is tested for non-regression. */
public final class C11CaptureSelfCheck {
    private static int assertions;
    private static void check(boolean value,String label){if(!value)throw new AssertionError(label);assertions++;System.out.println("PASS "+label);}
    private static void reject(Runnable body,String label){try{body.run();throw new AssertionError(label);}catch(IllegalArgumentException expected){check(true,label);}}
    public static void main(String[] args){
        FrameCaptureRules.tracks(1,0);check(true,"video-only capture accepted by its own contract");
        reject(()->FrameCaptureRules.tracks(0,1),"audio-only never a frame");reject(()->FrameCaptureRules.tracks(0,0),"empty capture rejected");reject(()->FrameCaptureRules.tracks(2,0),"multiple video tracks rejected");reject(()->FrameCaptureRules.tracks(1,1),"dual-track result cannot masquerade as video-only capture");
        reject(()->OutputValidationRules.tracks(1,0),"formal edit still rejects video-only output");OutputValidationRules.tracks(1,1);check(true,"formal edit dual-track contract unchanged");
        OutputValidationRules.Track healthy=new OutputValidationRules.Track(true,"video/avc",256,144,3000000,3000000);healthy.sample(0,4,3000000);healthy.sample(2900000,4,3000000);healthy.finish(3000000);check(true,"capture inherits strict video sample/time accounting");
        reject(()->new OutputValidationRules.Track(true,"video/hevc",256,144,3000000,3000000),"wrong capture video codec rejected");
        reject(()->new OutputValidationRules.Track(true,"video/avc",320,180,3000000,3000000),"wrong capture dimensions rejected");
        reject(()->new OutputValidationRules.Track(true,"video/avc",256,144,2000000,3000000),"truncated capture duration rejected");
        reject(()->new OutputValidationRules.Track(true,"video/avc",256,144,3000000,3000000).finish(3000000),"zero capture samples rejected");
        reject(()->new OutputValidationRules.Track(true,"video/avc",256,144,3000000,3000000).sample(-1,8,3000000),"negative capture PTS rejected");
        reject(()->new OutputValidationRules.Track(true,"video/avc",256,144,3000000,3000000).sample(0,0,3000000),"empty sample rejected");
        reject(()->new OutputValidationRules.Track(true,"video/avc",256,144,3000000,3000000).sample(0,1048577,3000000),"sample memory budget enforced");
        reject(()->healthy.sample(2900000,4,3000000),"duplicate capture PTS rejected");
        check(CaptureInputKind.fromRoute("vkspike://source/avi")==CaptureInputKind.AVI,"AVI route cannot select MP4 control parser");
        check(CaptureInputKind.fromRoute("vkspike://source/mp4")==CaptureInputKind.MP4,"MP4 control explicitly selects MP4 parser");
        reject(()->CaptureInputKind.fromRoute("vkspike://source/mkv"),"uncontracted capture format rejected without removing playback support");
        reject(()->CaptureInputKind.fromRoute(null),"missing capture source cannot fall back to MP4");
        FrameWindow plan=FrameWindow.at(10000000);check(plan.startMs==9000 && plan.endMs==12000 && plan.startMs*1000+plan.localUs==10000000,"AVI source ten-second request preserved");
        CodecProbeState probe=new CodecProbeState();probe.record("PROBE_LEASE_ACQUIRED");probe.record("PROBE_CODEC_CREATE_BEGIN");check(!probe.explainedOutcome("WORKER_DIED",false),"missing App trace remains unclassified despite actual native-call stage");
        System.out.println("RESULT c11_capture_assertions="+assertions+" failures=0 Android_frame_codec=NOT_RUN");
    }
}
