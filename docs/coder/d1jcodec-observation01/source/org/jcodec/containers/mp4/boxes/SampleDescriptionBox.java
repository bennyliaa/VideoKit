package org.jcodec.containers.mp4.boxes;

import java.nio.ByteBuffer;

/**
 * This class is part of JCodec ( www.jcodec.org )
 * This software is distributed under FreeBSD License

 * @author The JCodec project
 *
 */
public class SampleDescriptionBox extends NodeBox {

    // VideoKit observation01: original consumed header, never builder defaults.
    private boolean originalParseObserved;
    private int originalVersionFlagsWord;
    private long originalDeclaredEntryCount;

    public boolean hasOriginalParseObservation() { return originalParseObserved; }
    private void requireOriginalParseObservation() {
        if (!originalParseObserved) throw new IllegalStateException("ORIGINAL_PARSE_NOT_OBSERVED");
    }
    public int getOriginalVersionFlagsWord() { requireOriginalParseObservation(); return originalVersionFlagsWord; }
    public int getOriginalVersion() { requireOriginalParseObservation(); return originalVersionFlagsWord >>> 24; }
    public int getOriginalFlags() { requireOriginalParseObservation(); return originalVersionFlagsWord & 0xffffff; }
    public long getOriginalDeclaredEntryCount() { requireOriginalParseObservation(); return originalDeclaredEntryCount; }

    public static String fourcc() {
        return "stsd";
    }

    public static SampleDescriptionBox createSampleDescriptionBox(SampleEntry[] entries) {
        SampleDescriptionBox box = new SampleDescriptionBox(new Header(fourcc()));
        for (int i = 0; i < entries.length; i++) {
            SampleEntry e = entries[i];
            box.boxes.add(e);
        }
        return box;
    }

    public SampleDescriptionBox(Header header) {
        super(header);
    }

    @Override
    public void parse(ByteBuffer input) {
        originalParseObserved = false;
        originalVersionFlagsWord = 0;
        originalDeclaredEntryCount = 0;
        originalVersionFlagsWord = input.getInt();
        originalDeclaredEntryCount = input.getInt() & 0xffffffffL;
        super.parse(input);
        originalParseObserved = true;
    }

    @Override
    public void doWrite(ByteBuffer out) {
        out.putInt(0);
        //even if there is no sample descriptors entry count can not be less than 1
        out.putInt(Math.max(1, boxes.size()));
        super.doWrite(out);
    }
    
    @Override
    public int estimateSize() {
        return 8 + super.estimateSize();
    }
}
