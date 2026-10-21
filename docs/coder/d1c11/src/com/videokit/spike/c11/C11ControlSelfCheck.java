package com.videokit.spike.c11;
import java.io.IOException;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;
/** Focused regression for Android instance alphabet and bounded main-queue waiting. */
public final class C11ControlSelfCheck {
    private static int passed;
    private static void check(boolean yes,String label){if(!yes)throw new AssertionError(label);passed++;System.out.println("PASS "+label);}
    public static void main(String[] args)throws Exception{
        String id="01234567-89ab-4cde-8fab-0123456789ab",name=TaskNames.instance("task",id);
        check(name.matches("[a-zA-Z0-9_.]+") && !name.contains("-"),"Android12 instance alphabet excludes UUID hyphens");
        check(!name.equals(TaskNames.instance("task","01234567-89ab-4cde-8fab-0123456789ac")),"distinct UUID instances remain distinct");
        try{TaskNames.instance("task","1-1-1-1-1");throw new AssertionError();}catch(IllegalArgumentException expected){check(true,"noncanonical or injected task ID rejected");}
        AtomicBoolean ran=new AtomicBoolean();List<Runnable> queued=new ArrayList<>();
        try{BoundedDispatch.run(queued::add,()->ran.set(true),10);throw new AssertionError();}catch(IOException e){check("MAIN_LOOPER_TIMEOUT".equals(e.getMessage()),"unresponsive dispatch yields stable bounded timeout");}
        queued.get(0).run();check(!ran.get(),"timed-out queued operation cannot run later");
        BoundedDispatch.run(Runnable::run,()->ran.set(true),1000);check(ran.get(),"responsive dispatch executes normally");
        try{BoundedDispatch.run(Runnable::run,()->{throw new IllegalArgumentException("test");},1000);throw new AssertionError();}catch(IOException e){check(e.getCause() instanceof IllegalArgumentException,"original main-operation cause retained");}
        System.out.println("RESULT control_assertions="+passed+" failures=0 Android_device=NOT_RUN");
    }
}
