import java.io.*;
import java.nio.*;
import java.nio.channels.*;
import java.nio.file.*;
import java.util.*;
import androidx.media3.common.Format;
import androidx.media3.muxer.*;
import com.videokit.spike.c14.E6Muxer;
/** Uses actual cached 1.9.3 muxer and production E6 helper; no Android parser/decoder claim. */
public final class E6MuxerReplay {
    public static void main(String[] args)throws Exception {
        List<byte[]> csd=new ArrayList<>();List<byte[]> frames=new ArrayList<>();int[] flags=new int[6];
        try(DataInputStream in=new DataInputStream(Files.newInputStream(Path.of(args[0])))){
            int count=in.readInt();if(count<1 || count>4)throw new IOException();
            for(int i=0;i<count;i++){int n=in.readInt();if(n<1 || n>65536)throw new IOException();csd.add(in.readNBytes(n));}
            for(int i=0;i<6;i++){flags[i]=in.readInt();int n=in.readInt();if(n<1 || n>262144)throw new IOException();frames.add(in.readNBytes(n));}
            if(in.read()!=-1)throw new IOException();
        }
        long[] pts={0,208333,416667,625000,833333,1000000};
        Format format=new Format.Builder().setSampleMimeType("video/avc").setWidth(256).setHeight(144).setFrameRate(5).setInitializationData(csd).build();
        for(int which=0;which<2;which++){
            Path out=Path.of(args[1],which==0?"old-boundary.mp4":"e6-single-fragment.mp4");
            WritableByteChannel ch=FileChannel.open(out,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE);
            FragmentedMp4Muxer m=which==0?new FragmentedMp4Muxer.Builder(ch).setFragmentDurationMs(200).setSampleCopyingEnabled(true).build():E6Muxer.create(ch);
            int track=m.addTrack(format);
            for(int i=0;i<6;i++)m.writeSampleData(track,ByteBuffer.wrap(frames.get(i)),new BufferInfo(pts[i],frames.get(i).length,flags[i]));
            if(which==0)m.close();else E6Muxer.finish(m,track,6,pts[5]);
            System.out.println("MUXER_REPLAY "+out.getFileName()+" bytes="+Files.size(out)+" actualMedia3=1.9.3 actualE6Helper="+(which==1));
        }
    }
}
