package com.videokit.spike.c06;

/** Adversarial metadata/sample rules; Android decoder execution is separately NOT_RUN. */
public final class ValidationSelfCheck {
    private static int passed;
    private static void reject(String label,Runnable r){try{r.run();throw new AssertionError(label);}catch(IllegalArgumentException expected){passed++;System.out.println("PASS "+label);}}
    private static OutputValidationRules.Track video(){return new OutputValidationRules.Track(true,"video/avc",256,144,3000000,3000000);}
    public static void main(String[] args){
        OutputValidationRules.Track v=video(),a=new OutputValidationRules.Track(false,"audio/mp4a-latm",0,0,3000000,3000000);
        for(long t=0;t<=2960000;t+=40000){v.sample(t,20,3000000);a.sample(t,8,3000000);}v.finish(3000000);a.finish(3000000);OutputValidationRules.tracks(1,1);passed++;System.out.println("PASS independent valid video/audio preset");
        reject("audio cannot satisfy empty video",()->{OutputValidationRules.Track empty=video();a.finish(3000000);empty.finish(3000000);});
        reject("wrong audio codec",()->new OutputValidationRules.Track(false,"audio/mpeg",0,0,3000000,3000000));
        reject("wrong video codec",()->new OutputValidationRules.Track(true,"video/hevc",256,144,3000000,3000000));
        reject("wrong height",()->new OutputValidationRules.Track(true,"video/avc",256,180,3000000,3000000));
        reject("wrong width",()->new OutputValidationRules.Track(true,"video/avc",320,144,3000000,3000000));
        reject("wrong duration",()->new OutputValidationRules.Track(true,"video/avc",256,144,6000000,3000000));
        reject("negative PTS",()->video().sample(-1,20,3000000));
        reject("nonmonotonic PTS",()->{OutputValidationRules.Track x=video();x.sample(40000,20,3000000);x.sample(20000,20,3000000);});
        reject("empty sample",()->video().sample(0,0,3000000));
        reject("truncated video",()->{OutputValidationRules.Track x=video();x.sample(0,20,3000000);x.finish(3000000);});
        reject("missing AAC or duplicate video",()->OutputValidationRules.tracks(2,0));
        System.out.println("RESULT assertions="+passed+" failures=0 Android_decode=NOT_RUN");
    }
}
