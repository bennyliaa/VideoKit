package com.videokit.spike.c13;

import android.graphics.Bitmap;
import android.graphics.PointF;
import android.media.FaceDetector;
import android.os.Looper;

/** Offline platform alternative, not an identity recognizer or accepted quality backend. */
public final class PlatformFaceProbe {
    public static int detect(Bitmap frame){
        if(Looper.myLooper()==Looper.getMainLooper())throw new IllegalStateException("MAIN_THREAD_AI_REJECTED");
        int width=Math.min(256,frame.getWidth()) & ~1;int height=Math.max(2,frame.getHeight()*width/frame.getWidth());height=Math.min(256,height);
        if(width<2)throw new IllegalArgumentException("FRAME_BOUNDS");
        Bitmap scaled=Bitmap.createScaledBitmap(frame,width,height,true);Bitmap rgb=scaled.copy(Bitmap.Config.RGB_565,false);
        try{FaceDetector detector=new FaceDetector(width,height,4);FaceDetector.Face[] faces=new FaceDetector.Face[4];return detector.findFaces(rgb,faces);}
        finally{rgb.recycle();if(scaled!=frame)scaled.recycle();}
    }
}
