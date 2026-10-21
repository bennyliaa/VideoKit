package org.jcodec.containers.mp4.boxes;

import java.nio.ByteBuffer;

/**
 * This class is part of JCodec ( www.jcodec.org )
 * This software is distributed under FreeBSD License
 * 
 * @author The JCodec project
 *
 */
public class DataRefBox extends NodeBox {

    // VideoKit observation01: parse provenance only, no policy or write change.
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
        return "dref";
    }

    public static DataRefBox createDataRefBox() {
        return new DataRefBox(new Header(fourcc()));
    }

    public DataRefBox(Header atom) {
        super(atom);
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
        out.putInt(boxes.size());
        super.doWrite(out);
    }
    
    @Override
    public int estimateSize() {
        return 8 + super.estimateSize();
    }
}
