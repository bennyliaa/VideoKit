plugins {
    id("com.android.application") version "9.4.1" apply false
    // AGP built-in Kotlin compiles with the Kotlin Gradle plugin on the classpath: the Kit's version (2.4.21), whose
    // metadata the bundled 2.2 compiler cannot read.
    id("org.jetbrains.kotlin.android") version "2.4.21" apply false
}
