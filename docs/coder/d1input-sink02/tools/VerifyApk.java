import com.android.apksig.ApkVerifier;
import java.io.File;
import java.security.MessageDigest;
/** Output-only verification through the already cached official Android apksig library. */
public final class VerifyApk {
    static String hex(byte[] value){StringBuilder s=new StringBuilder();for(byte b:value)s.append(String.format(java.util.Locale.ROOT,"%02x",b&255));return s.toString();}
    public static void main(String[] args)throws Exception {
        for(String p:args){
            ApkVerifier.Result r=new ApkVerifier.Builder(new File(p)).build().verify();
            if(!r.isVerified())throw new AssertionError("APK_SIGNATURE_REJECTED "+r.getErrors());
            if(r.getSignerCertificates().size()!=1)throw new AssertionError("SINGLE_DEBUG_SIGNER_REQUIRED");
            System.out.println("VERIFIED "+new File(p).getName()+" v2="+r.isVerifiedUsingV2Scheme()+" certificateSha256="+hex(MessageDigest.getInstance("SHA-256").digest(r.getSignerCertificates().get(0).getEncoded())));
        }
    }
}
