package com.videokit.d1input;
import androidx.media3.extractor.*;
import androidx.media3.extractor.mp4.*;
import androidx.media3.muxer.*;
import java.nio.*;import java.nio.channels.*;
/** Actual admitted Media3 bytecode, unchanged baseline JVM platform ports only.
 * Missing platform classes are reported as NOT_RUN, never a successful container test. */
public final class Media3AvailabilityCheck {
 interface Attempt {void run()throws Exception;}
 static void attempt(String name,Attempt action){try{action.run();System.out.println(name+" CONSTRUCTED_ONLY");}catch(Throwable t){System.out.println(name+" NOT_RUN_PLATFORM "+t);t.printStackTrace(System.out);}}
 public static void main(String[] args){
  attempt("DefaultExtractorInput",()->new DefaultExtractorInput((b,o,n)->-1,0,-1));
  attempt("Mp4Extractor",()->new Mp4Extractor().release());
  attempt("FragmentedMp4Extractor",()->new FragmentedMp4Extractor().release());
  attempt("FragmentedMp4Muxer",()->new FragmentedMp4Muxer.Builder(new WritableByteChannel(){public int write(ByteBuffer b){int n=b.remaining();b.position(b.limit());return n;}public boolean isOpen(){return true;}public void close(){}}).build().close());
 }
}
