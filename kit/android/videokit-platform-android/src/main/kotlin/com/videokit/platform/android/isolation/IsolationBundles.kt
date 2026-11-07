package com.videokit.platform.android.isolation

import android.os.Bundle
import android.os.Message
import com.videokit.core.runtime.IsolationMessage
import com.videokit.core.runtime.IsolationMessageType

/** [IsolationMessage] ↔ `Message.data` (only primitives and byte arrays: nothing a worker could abuse). */
internal object IsolationBundles {
    private const val VERSION = "v"
    private const val TASK = "t"
    private const val GENERATION = "g"
    private const val SEQ = "s"
    private const val TYPE = "y"
    private const val CALL = "c"
    private const val NAME = "n"
    private const val OFFSET = "o"
    private const val LENGTH = "l"
    private const val PAYLOAD = "p"

    /** Intent extra: task id of the worker instance. */
    const val EXTRA_TASK = "com.videokit.isolation.TASK"

    /** Intent extra: generation of the worker instance. */
    const val EXTRA_GENERATION = "com.videokit.isolation.GENERATION"

    fun message(message: IsolationMessage): Message = Message.obtain().apply {
        data = Bundle().apply {
            putInt(VERSION, message.version)
            putString(TASK, message.taskId)
            putInt(GENERATION, message.generation)
            putLong(SEQ, message.seq)
            putString(TYPE, message.type.name)
            putLong(CALL, message.callSeq)
            putString(NAME, message.name)
            putLong(OFFSET, message.offset)
            putInt(LENGTH, message.length)
            putByteArray(PAYLOAD, message.payload)
        }
    }

    /** The protocol message of [message], or `null` when it is not one (it is then refused). */
    fun decode(message: Message): IsolationMessage? = try {
        val data = message.data
        val type = data.getString(TYPE)?.let { name -> IsolationMessageType.entries.firstOrNull { it.name == name } }
        if (type == null) {
            null
        } else {
            IsolationMessage(
                version = data.getInt(VERSION, -1),
                taskId = data.getString(TASK).orEmpty(),
                generation = data.getInt(GENERATION, -1),
                seq = data.getLong(SEQ, -1L),
                type = type,
                callSeq = data.getLong(CALL, -1L),
                name = data.getString(NAME),
                offset = data.getLong(OFFSET, 0L),
                length = data.getInt(LENGTH, 0),
                payload = data.getByteArray(PAYLOAD) ?: ByteArray(0),
            )
        }
    } catch (_: RuntimeException) {
        // A malformed parcel (BadParcelableException and friends).
        null
    }
}
