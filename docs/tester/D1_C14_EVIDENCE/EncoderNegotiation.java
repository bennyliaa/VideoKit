package com.videokit.spike.c14;
import java.io.*;
import java.util.*;
import java.util.function.*;
/** Shared finite policy. Driver owns real codec references; timeout never proves release. */
public final class EncoderNegotiation {
    public static final int MAX_CODECS=16,MAX_ATTEMPTS=4,FLEX=0x7f420888;
    public static final long BUDGET_NS=12000000000L;
    public static final class Descriptor {
        public final String name,canonical;public final boolean hardware,software,vendor,geometry,baseline;private final int[] colors;
        public Descriptor(String name,String canonical,boolean hw,boolean sw,boolean vendor,boolean geometry,int[] colors,int[] profiles)throws IOException{
            identifier(name);identifier(canonical);if(colors==null || profiles==null || colors.length>64 || profiles.length>128 || profiles.length%2!=0)throw new IOException("PIPE_ENCODER_METADATA_BUDGET");
            this.name=name;this.canonical=canonical;hardware=hw;software=sw;this.vendor=vendor;this.geometry=geometry;this.colors=colors.clone();boolean base=false;for(int i=0;i<profiles.length;i+=2)base|=profiles[i]==1;baseline=base;
        }
        boolean has(int value){for(int color:colors)if(color==value)return true;return false;}
    }
    public static void identifier(String text)throws IOException{if(text==null || !text.matches("[A-Za-z0-9._-]{1,128}"))throw new IOException("PIPE_ENCODER_METADATA_BUDGET");}
    public static String diagnostic(String value){return value!=null && value.matches("android\\.media\\.MediaCodec\\.error_[A-Za-z0-9_-]{1,64}")?value:"UNAVAILABLE_PATTERN";}
    public static final class Candidate {
        public final Descriptor codec;public final int color,variant;public final boolean baseline;
        Candidate(Descriptor codec,int color,int variant,boolean baseline){this.codec=codec;this.color=color;this.variant=variant;this.baseline=baseline;}
        public String key(){return codec.canonical+":"+color+":"+baseline;}
    }
    private static Candidate variant(Descriptor d,int round){int[] order={21,19,FLEX};int preferred=0,alternate=0;for(int c:order)if(d.has(c)){if(preferred==0)preferred=c;else if(alternate==0)alternate=c;}if(preferred==0)return null;if(round==1)return new Candidate(d,preferred,1,false);if(alternate==0 && !d.baseline)return null;return new Candidate(d,alternate==0?preferred:alternate,2,d.baseline);}
    public static List<Candidate> plan(List<Descriptor> input)throws IOException{
        if(input==null || input.size()>MAX_CODECS)throw new IOException("PIPE_ENCODER_METADATA_BUDGET");List<Descriptor> all=new ArrayList<>();Set<String> unique=new HashSet<>();
        List<Descriptor> sorted=new ArrayList<>(input);sorted.sort(Comparator.comparing((Descriptor d)->d.software).thenComparing(d->!d.hardware).thenComparing(d->d.canonical).thenComparing(d->d.name));
        for(Descriptor d:sorted)if(d.geometry && variant(d,1)!=null && unique.add(d.canonical))all.add(d);
        List<Descriptor> selected=new ArrayList<>();if(!all.isEmpty()){Descriptor first=all.get(0);selected.add(first);for(Descriptor d:all)if(d.software!=first.software){selected.add(d);break;}if(selected.size()==1 && all.size()>1)selected.add(all.get(1));}
        List<Candidate> result=new ArrayList<>();Set<String> keys=new HashSet<>();for(int round=1;round<=2;round++)for(Descriptor d:selected){Candidate c=variant(d,round);if(c!=null && keys.add(c.key()))result.add(c);}return List.copyOf(result);
    }
    public interface Driver {
        boolean supported(Candidate c)throws Exception;void create(Candidate c)throws Exception;void configure(Candidate c)throws Exception;void start(Candidate c)throws Exception;void release()throws Exception;boolean released();
        void event(String stage,Candidate c,Throwable error,String outcome,boolean first);
    }
    public static final class Failure extends IOException {public final String phase;Failure(String code,String phase,Throwable cause){super(code,cause);this.phase=phase;}}
    private final Driver driver;private final BooleanSupplier cancel;private final LongSupplier clock;private final long began;
    private volatile String first;private String firstPhase;private Throwable firstCause;private volatile int attempts,proposals;private volatile Candidate selected;
    public EncoderNegotiation(Driver driver,BooleanSupplier cancel,LongSupplier clock){this.driver=driver;this.cancel=cancel;this.clock=clock;began=clock.getAsLong();}
    private String stop(){if(cancel.getAsBoolean())return "PIPE_CANCELLED";return clock.getAsLong()-began>=BUDGET_NS?"PIPE_ENCODER_NEGOTIATION_DEADLINE":null;}
    private void stopped(String phase)throws Failure{String code=stop();if(code!=null)throw new Failure(code,phase,null);}
    public Candidate run(List<Candidate> plan)throws Exception{
        if(plan==null || plan.size()>MAX_ATTEMPTS)throw new Failure("PIPE_ENCODER_ATTEMPT_BUDGET","CAPABILITY",null);
        for(Candidate c:plan){stopped("CAPABILITY");proposals++;boolean support;
            try{support=driver.supported(c);driver.event("CAPABILITY",c,null,support?"SUPPORTED":"NOT_SUPPORTED",false);}catch(Exception error){driver.event("CAPABILITY",c,error,"QUERY_FAILED",false);throw new Failure("PIPE_ENCODER_CAPABILITY_FAILED","CAPABILITY",error);}
            if(!support)continue;stopped("CREATE");if(!driver.released())throw new Failure("PIPE_CODEC_CLOSE_UNPROVEN","CLOSE",null);attempts++;String phase="CREATE";
            try{driver.event(phase,c,null,"BEGIN",false);driver.create(c);stopped(phase);phase="CONFIGURE";driver.event(phase,c,null,"BEGIN",false);driver.configure(c);stopped(phase);phase="START";driver.event(phase,c,null,"BEGIN",false);driver.start(c);stopped(phase);selected=c;driver.event(phase,c,null,"SELECTED",false);return c;}
            catch(Exception error){String code=error instanceof Failure?error.getMessage():"PIPE_ENCODER_"+phase+"_FAILED";boolean initial=first==null;if(initial){first=code;firstPhase=phase;firstCause=error;}driver.event(phase,c,error,"REJECTED",initial);
                try{driver.release();}catch(Exception cleanup){error.addSuppressed(cleanup);driver.event("CLOSE",c,cleanup,"UNPROVEN",false);throw new Failure(first,phase,firstCause);}
                if(!driver.released()){driver.event("CLOSE",c,null,"UNPROVEN",false);throw new Failure(first,phase,firstCause);}driver.event("CLOSE",c,null,"RELEASED",false);
                stopped(phase);if(phase.equals("CREATE") || error instanceof Failure)throw new Failure(first,phase,firstCause);
            }
        }
        if(first!=null)throw new Failure(first,firstPhase,firstCause);throw new Failure("PIPE_CAPABILITY_UNSUPPORTED","CAPABILITY",null);
    }
    public int attempts(){return attempts;}public int proposals(){return proposals;}public String firstError(){return first;}public Candidate selected(){return selected;}
}
