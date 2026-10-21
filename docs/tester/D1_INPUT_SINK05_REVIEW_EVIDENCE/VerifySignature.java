import com.android.apksig.ApkVerifier;
import java.io.File;
import java.security.MessageDigest;
public class VerifySignature {
 public static void main(String[] args)throws Exception {
  ApkVerifier.Result r=new ApkVerifier.Builder(new File(args[0])).build().verify();
  if(!r.isVerified()||!r.isVerifiedUsingV2Scheme()||r.getSignerCertificates().size()!=1)throw new AssertionError(r.getErrors().toString());
  byte[] hash=MessageDigest.getInstance("SHA-256").digest(r.getSignerCertificates().get(0).getEncoded());StringBuilder s=new StringBuilder();for(byte b:hash)s.append(String.format("%02x",b&255));
  if(!s.toString().equals("5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f"))throw new AssertionError("signer mismatch");
  System.out.println("PASS independent_apksig_library_v2 certificateSha256="+s+" SDKCommand=false runtimeMedia=NOT_RUN");
 }
}
