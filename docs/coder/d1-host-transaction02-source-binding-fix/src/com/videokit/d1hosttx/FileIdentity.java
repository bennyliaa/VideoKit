package com.videokit.d1hosttx;

import java.io.IOException;import java.nio.file.*;import java.nio.file.attribute.*;import java.util.UUID;

/** Identity evidence for this host's private generated files. JDK fileKey is
 * optional on Windows. If absent, keep a private hard-link witness and require
 * the filesystem's isSameFile result; NEVER substitute a hash or path equality.
 * These owned witnesses are metadata test artifacts, not open consumer handles. */
final class FileIdentity {
 private final Object key;private final Path witness;private final String recordId;
 private FileIdentity(Object key,Path witness,String id){this.key=key;this.witness=witness;recordId=id;}
 static FileIdentity capture(Path p)throws IOException {
  BasicFileAttributes a=attributes(p);Object k=a.fileKey();
  if(k!=null)return new FileIdentity(k,null,"JDK_FILE_KEY:"+k);
  Path anchor=p.resolveSibling(p.getFileName()+".hosttx-identity-"+UUID.randomUUID());
  Files.createLink(anchor,p);
  if(!Files.isSameFile(anchor,p))throw new IOException("FILE_IDENTITY_UNSUPPORTED");
  return new FileIdentity(null,anchor,"OWNED_HARDLINK_WITNESS:"+anchor.getFileName());
 }
 private static BasicFileAttributes attributes(Path p)throws IOException {
  BasicFileAttributes a=Files.readAttributes(p,BasicFileAttributes.class,LinkOption.NOFOLLOW_LINKS);
  if(!a.isRegularFile()||a.isSymbolicLink())throw new IOException("OUTPUT_GRANT_INVALID");return a;
 }
 void requireSame(Path p)throws IOException {
  BasicFileAttributes a=attributes(p);
  if(key!=null?!key.equals(a.fileKey()):!Files.isSameFile(witness,p))throw new IOException("OUTPUT_GRANT_INVALID");
 }
 String recordId(){return recordId;}
}
