package com.videokit.d1present;
import java.security.MessageDigest;
/** Own generated PCM, fixed integer seed; no sampled audio, telemetry or external media. */
public final class PcmFixture {
    public static final int SEED=0x564b2026;
    public static final String SHA256="268d0e111f05ef5ad7ba405df6b78e5e8f6b3a43ebd926c48429d139a27da4ff";
    public static byte[] create(){
        byte[] out=new byte[Limits.PCM_BYTES];int state=SEED;
        for(int f=0;f<Limits.RATE*3;f++){
            // Integer triangular 400Hz wave, peak 256/32768, brief 10ms fade at each end.
            int phase=f%120;int wave=phase<60?phase:120-phase;
            int amplitude=(wave-30)*256/30;int ramp=Math.min(480,Math.min(f,Limits.RATE*3-1-f));
            amplitude=amplitude*Math.max(0,ramp)/480;
            state=state*1664525+1013904223; // Reproducible +/-1 LSB dither.
            short value=(short)(amplitude+((state>>>31)&1));
            int at=f*4;out[at]=(byte)value;out[at+1]=(byte)(value>>>8);out[at+2]=out[at];out[at+3]=out[at+1];
        }if(!sha(out).equals(SHA256))throw new IllegalStateException("PCM_FIXTURE_IDENTITY_CHANGED");return out;
    }
    public static String sha(byte[] b){try{byte[] h=MessageDigest.getInstance("SHA-256").digest(b);StringBuilder s=new StringBuilder();for(byte v:h)s.append(String.format(java.util.Locale.ROOT,"%02x",v&255));return s.toString();}catch(Exception e){throw new AssertionError(e);}}
    private PcmFixture(){}
}
