/* Independently authored D1-only JNI lease adapter. No third-party algorithm or model code. */
#include <jni.h>
#include <sys/file.h>
#include <errno.h>

static int bounded_flock(int fd, int operation) {
    if (fd < 0) return 2;
    for (int attempt = 0; attempt < 3; ++attempt) {
        if (flock(fd, operation | LOCK_NB) == 0) return 0;
        if (errno == EWOULDBLOCK || errno == EAGAIN) return 1;
        if (errno != EINTR) return 2;
    }
    return 2;
}
JNIEXPORT jint JNICALL Java_com_videokit_spike_c04_AndroidLease_tryLock
  (JNIEnv *env, jclass type, jint fd, jboolean exclusive) {
    (void)env; (void)type;
    return bounded_flock(fd, exclusive ? LOCK_EX : LOCK_SH);
}
JNIEXPORT jint JNICALL Java_com_videokit_spike_c04_AndroidLease_unlock
  (JNIEnv *env, jclass type, jint fd) {
    (void)env; (void)type;
    return bounded_flock(fd, LOCK_UN);
}
