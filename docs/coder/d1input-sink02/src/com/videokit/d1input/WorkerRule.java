package com.videokit.d1input;
import java.io.IOException;
/** Platform thread policy. Android binding rejects the real main Looper; tests replace only this port. */
public interface WorkerRule {void requireWorker()throws IOException;}
