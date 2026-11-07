package com.videokit.testkit.internal

/**
 * Minimal JSON writer/reader for Fake edit project snapshots (versioned JSON, 08 §2.1). Values are
 * `Map<String, Any?>`, `List<Any?>`, `String`, `Long`, `Double`, `Boolean` and `null`.
 * Floats are written with their shortest representation so they round-trip exactly.
 */
internal object MiniJson {
    fun write(value: Any?): String = StringBuilder().also { writeValue(it, value) }.toString()

    fun parse(text: String): Any? {
        val reader = Reader(text)
        val value = reader.readValue()
        reader.skipWhitespace()
        if (!reader.atEnd()) throw IllegalArgumentException("trailing characters at ${reader.position}")
        return value
    }

    private fun writeValue(out: StringBuilder, value: Any?) {
        when (value) {
            null -> out.append("null")

            is String -> writeString(out, value)

            is Boolean -> out.append(value)

            is Int, is Long -> out.append(value.toString())

            is Float -> out.append(if (value.isFinite()) value.toString() else throw IllegalArgumentException("non-finite"))

            is Double -> out.append(if (value.isFinite()) value.toString() else throw IllegalArgumentException("non-finite"))

            is Map<*, *> -> {
                out.append('{')
                value.entries.forEachIndexed { index, (key, item) ->
                    if (index > 0) out.append(',')
                    writeString(out, key as String)
                    out.append(':')
                    writeValue(out, item)
                }
                out.append('}')
            }

            is List<*> -> {
                out.append('[')
                value.forEachIndexed { index, item ->
                    if (index > 0) out.append(',')
                    writeValue(out, item)
                }
                out.append(']')
            }

            else -> throw IllegalArgumentException("unsupported type ${value.typeName()}")
        }
    }

    private fun writeString(out: StringBuilder, value: String) {
        out.append('"')
        value.forEach { ch ->
            when (ch) {
                '"' -> out.append("\\\"")
                '\\' -> out.append("\\\\")
                '\n' -> out.append("\\n")
                '\r' -> out.append("\\r")
                '\t' -> out.append("\\t")
                else -> if (ch < ' ') out.append("\\u").append(ch.code.toString(16).padStart(4, '0')) else out.append(ch)
            }
        }
        out.append('"')
    }

    private class Reader(private val text: String) {
        var position = 0

        fun atEnd(): Boolean = position >= text.length

        fun skipWhitespace() {
            while (!atEnd() && text[position].isWhitespace()) position++
        }

        fun readValue(): Any? {
            skipWhitespace()
            if (atEnd()) throw IllegalArgumentException("unexpected end")
            return when (val ch = text[position]) {
                '{' -> readObject()
                '[' -> readArray()
                '"' -> readString()
                't' -> literal("true", true)
                'f' -> literal("false", false)
                'n' -> literal("null", null)
                else -> if (ch == '-' || ch.isDigit()) readNumber() else throw IllegalArgumentException("unexpected '$ch' at $position")
            }
        }

        private fun literal(word: String, value: Any?): Any? {
            if (!text.startsWith(word, position)) throw IllegalArgumentException("expected $word at $position")
            position += word.length
            return value
        }

        private fun readObject(): Map<String, Any?> {
            position++
            val result = LinkedHashMap<String, Any?>()
            skipWhitespace()
            if (peek() == '}') {
                position++
                return result
            }
            while (true) {
                skipWhitespace()
                val key = readString()
                skipWhitespace()
                expect(':')
                result[key] = readValue()
                skipWhitespace()
                when (next()) {
                    ',' -> continue
                    '}' -> return result
                    else -> throw IllegalArgumentException("expected , or } at $position")
                }
            }
        }

        private fun readArray(): List<Any?> {
            position++
            val result = ArrayList<Any?>()
            skipWhitespace()
            if (peek() == ']') {
                position++
                return result
            }
            while (true) {
                result += readValue()
                skipWhitespace()
                when (next()) {
                    ',' -> continue
                    ']' -> return result
                    else -> throw IllegalArgumentException("expected , or ] at $position")
                }
            }
        }

        private fun readString(): String {
            expect('"')
            val out = StringBuilder()
            while (true) {
                val ch = next()
                when (ch) {
                    '"' -> return out.toString()

                    '\\' -> when (val escaped = next()) {
                        '"', '\\', '/' -> out.append(escaped)

                        'n' -> out.append('\n')

                        'r' -> out.append('\r')

                        't' -> out.append('\t')

                        'b' -> out.append('\b')

                        'f' -> out.append('\u000C')

                        'u' -> {
                            if (position + 4 > text.length) throw IllegalArgumentException("bad unicode escape")
                            out.append(text.substring(position, position + 4).toInt(16).toChar())
                            position += 4
                        }

                        else -> throw IllegalArgumentException("bad escape at $position")
                    }

                    else -> out.append(ch)
                }
            }
        }

        private fun readNumber(): Any {
            val start = position
            if (peek() == '-') position++
            while (!atEnd() && (text[position].isDigit() || text[position] in ".eE+-")) position++
            val token = text.substring(start, position)
            return if (token.any { it in ".eE" }) token.toDouble() else token.toLong()
        }

        private fun peek(): Char = if (atEnd()) throw IllegalArgumentException("unexpected end") else text[position]

        private fun next(): Char = peek().also { position++ }

        private fun expect(ch: Char) {
            if (next() != ch) throw IllegalArgumentException("expected '$ch' at ${position - 1}")
        }
    }
}
