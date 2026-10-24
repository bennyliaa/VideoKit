package android.net;
/** Explicit JVM Android platform port for opaque URI equality only. Not a Media3 replacement. */
public final class Uri {
 public static final Uri EMPTY=new Uri("");private final String value;private Uri(String v){value=v;}
 public static Uri parse(String s){return new Uri(s);}public String toString(){return value;}
 public boolean equals(Object o){return o instanceof Uri&&value.equals(((Uri)o).value);}public int hashCode(){return value.hashCode();}
}
