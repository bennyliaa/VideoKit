package com.videokit.spike.e4;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.atomic.AtomicLong;
/** E13 original-return notification only. Listeners only wake the original finisher. */
public final class E13ReturnEvents {
 public interface Listener {void changed();}
 private static final CopyOnWriteArrayList<Listener> listeners=new CopyOnWriteArrayList<>();
 private static final AtomicLong version=new AtomicLong();
 public static synchronized void subscribe(Listener l){if(listeners.size()>=1)throw new IllegalStateException("E13_ONE_RUNNER_SUBSCRIPTION");listeners.addIfAbsent(l);}
 public static void unsubscribe(Listener l){listeners.remove(l);}
 public static long version(){return version.get();}
 public static void returned(){version.incrementAndGet();for(Listener l:listeners)l.changed();}
 private E13ReturnEvents(){}
}
