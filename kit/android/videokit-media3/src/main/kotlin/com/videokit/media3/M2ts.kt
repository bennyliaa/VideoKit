package com.videokit.media3

/**
 * m2ts (BDAV) adapter (15 §2.2, S2 to confirm): an m2ts file is a sequence of 192-byte packets, each a 4-byte
 * arrival time code followed by a 188-byte MPEG-TS packet. Media3's `TsExtractor` reads 188-byte packets only, so
 * the data source presents the *logical* TS stream (the prefixes removed) and maps every logical offset to the
 * physical file offset. Positions and seeks of the extractor are logical; nothing is copied or cached on disk.
 */
internal object M2ts {
    const val PACKET_SIZE = 192
    const val TS_PACKET_SIZE = 188
    const val PREFIX_SIZE = PACKET_SIZE - TS_PACKET_SIZE
    private const val SYNC_BYTE: Byte = 0x47

    /** Bytes [isM2ts] wants to look at: the sync bytes of the first two packets. */
    const val SNIFF_BYTES = PACKET_SIZE + PREFIX_SIZE + 1

    /** Whether [header] (the first [length] bytes of the file) looks like m2ts rather than plain TS. */
    fun isM2ts(header: ByteArray, length: Int): Boolean {
        if (length < SNIFF_BYTES) return false
        val m2tsSync = header[PREFIX_SIZE] == SYNC_BYTE && header[PACKET_SIZE + PREFIX_SIZE] == SYNC_BYTE
        // Plain TS has its sync byte at 0 and 188; an m2ts prefix (arrival time code) rarely does both.
        val tsSync = header[0] == SYNC_BYTE && header[TS_PACKET_SIZE] == SYNC_BYTE
        return m2tsSync && !tsSync
    }

    /** Physical file offset of logical TS offset [logical]. */
    fun physicalOffset(logical: Long): Long {
        require(logical >= 0) { "negative offset" }
        return (logical / TS_PACKET_SIZE) * PACKET_SIZE + PREFIX_SIZE + logical % TS_PACKET_SIZE
    }

    /** Logical TS length of a physical file of [physical] bytes (a truncated last packet keeps its TS bytes). */
    fun logicalLength(physical: Long): Long {
        require(physical >= 0) { "negative length" }
        val tail = physical % PACKET_SIZE
        return (physical / PACKET_SIZE) * TS_PACKET_SIZE + (tail - PREFIX_SIZE).coerceAtLeast(0L)
    }
}

/**
 * The logical TS view of an m2ts host source over a [HostReader]: reads stop at every 188-byte packet boundary and
 * skip the 4-byte prefix of the next packet.
 */
internal class M2tsReader(private val reader: HostReader) {
    private var logical = 0L
    private var remaining = HostReader.UNKNOWN

    /** Opens the logical range at [position] with [length] bytes ([HostReader.UNKNOWN] = to the end). */
    fun open(position: Long, length: Long): Long {
        logical = position
        val physicalAvailable = reader.open(M2ts.physicalOffset(position), HostReader.UNKNOWN)
        val logicalAvailable = if (physicalAvailable == HostReader.UNKNOWN) {
            HostReader.UNKNOWN
        } else {
            // Physical end of the source, counted back in the logical stream.
            M2ts.logicalLength(M2ts.physicalOffset(position) + physicalAvailable) - position
        }
        remaining = when {
            length != HostReader.UNKNOWN && logicalAvailable != HostReader.UNKNOWN -> minOf(length, logicalAvailable)
            length != HostReader.UNKNOWN -> length
            else -> logicalAvailable
        }
        return remaining
    }

    fun read(target: ByteArray, offset: Int, length: Int): Int {
        if (length == 0) return 0
        if (remaining == 0L) return HostReader.END
        val inPacket = (logical % M2ts.TS_PACKET_SIZE).toInt()
        var wanted = minOf(length, M2ts.TS_PACKET_SIZE - inPacket)
        if (remaining != HostReader.UNKNOWN) wanted = minOf(wanted.toLong(), remaining).toInt()
        val read = reader.read(target, offset, wanted)
        if (read == HostReader.END) {
            remaining = 0L
            return HostReader.END
        }
        logical += read
        if (remaining != HostReader.UNKNOWN) remaining -= read
        // Crossed into the next packet: skip its arrival time code.
        if (logical % M2ts.TS_PACKET_SIZE == 0L && remaining != 0L) reader.skip(M2ts.PREFIX_SIZE)
        return read
    }

    fun close() {
        reader.close()
        remaining = HostReader.UNKNOWN
    }
}
