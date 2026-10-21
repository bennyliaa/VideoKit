package com.videokit.spike.e4;
import java.nio.file.*;import java.util.*;
/** Pure binding check; never invokes the approved dispatch entry. */
public final class KBindingCheck {
 public static void main(String[] a)throws Exception{byte[] raw=Files.readAllBytes(Paths.get(a[0]));E9Record r=E9Record.parse(raw,2048);r.exact("kind","scope","serial","review","budget","requests");if(!r.get("kind").equals("e13jFixedReadOnlyRelease")||!r.get("scope").equals("116c978327fc2240dbe04a9ead566165d231b88d14166776e03938a40b76aaef")||!r.get("serial").equals("HA1Q6WXR")||!r.get("review").equals("f9e5a63acf2aea2fc51c9c71ec50ceba5ed080cdded46676cd7fd9cec6374583")||!r.get("budget").equals("262144")||!r.get("requests").equals("2")||!Arrays.equals(r.bytes(),raw))throw new AssertionError("release not exact");var f=E13JReadOnly.class.getDeclaredField("APPROVED_REQUEST_SHA");f.setAccessible(true);if(!r.hash().equals(f.get(null)))throw new AssertionError("actual final class strategy SHA mismatch");System.out.println("PASS_EXACT_TYPED_RELEASE_AND_FINAL_CLASS_CONSTANT sha="+r.hash()+" dispatchInvocations=0 actual5037Connections=0");}
}
