package com.videokit.spike.e4;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
/** Production E13BindingOwner; only Context bind/unbind and callback scheduling are substituted. */
public final class E13ABindingCheck {
    static int assertions;
    static void ok(boolean value){assertions++;if(!value)throw new AssertionError("binding assertion "+assertions);}
    static void waitFor(CountDownLatch latch)throws Exception {ok(latch.await(3000,TimeUnit.MILLISECONDS));}
    static void join(Thread thread)throws Exception {thread.join(3000);ok(!thread.isAlive());}
    static final class Platform implements E13BindingOwner.Port<Object> {
        final Object connection=new Object();int binds,unbinds;boolean accepted=true;String error="NONE";
        CountDownLatch bindEntered,bindAllow,unbindEntered,unbindAllow;
        public boolean bind(Object actual)throws Exception {ok(actual==connection);binds++;if(bindEntered!=null){bindEntered.countDown();waitFor(bindAllow);}if(error.equals("SECURITY"))throw new SecurityException("SUBSTITUTE_AFTER_DISPATCHER_REGISTRATION");if(error.equals("OTHER"))throw new IllegalStateException("SUBSTITUTE_RETURNED_EXCEPTION");return accepted;}
        public void unbind(Object actual)throws Exception {ok(actual==connection);unbinds++;if(unbindEntered!=null){unbindEntered.countDown();waitFor(unbindAllow);}if(error.equals("UNBIND"))throw new IllegalArgumentException("SUBSTITUTE_UNBIND_ACK_UNPROVEN");}
    }
    public static void main(String[] args)throws Exception {
        String mode=args[0];Platform p=new Platform();E13BindingOwner<Object> owner=new E13BindingOwner<>(p.connection,p);
        ok(!owner.returned() && !E13BindingOwner.allReturned());
        switch(mode){
        case "FALSE":p.accepted=false;owner.bind();ok(owner.bindReturned()&&!owner.accepted());owner.close();break;
        case "SECURITY":p.error="SECURITY";owner.bind();ok(owner.bindReturned() && owner.bindError().equals(SecurityException.class.getName()));owner.close();break;
        case "OTHER_EXCEPTION":p.error="OTHER";owner.bind();ok(owner.bindReturned() && owner.bindError().equals(IllegalStateException.class.getName()));owner.close();break;
        case "TRUE_CALLBACK":{
            owner.bind();AtomicInteger called=new AtomicInteger();ok(owner.callback(called::incrementAndGet));ok(called.get()==1);owner.close();break;
        }
        case "BIND_IN_FLIGHT":{
            p.bindEntered=new CountDownLatch(1);p.bindAllow=new CountDownLatch(1);Thread original=new Thread(owner::bind);original.start();waitFor(p.bindEntered);owner.close();owner.close();ok(!owner.bindReturned() && p.unbinds==0 && !owner.returned());p.bindAllow.countDown();join(original);break;
        }
        case "UNBIND_IN_FLIGHT":{
            owner.bind();p.unbindEntered=new CountDownLatch(1);p.unbindAllow=new CountDownLatch(1);Thread original=new Thread(owner::close);original.start();waitFor(p.unbindEntered);owner.close();owner.close();ok(p.unbinds==1 && !owner.returned() && !E13BindingOwner.allReturned());p.unbindAllow.countDown();join(original);break;
        }
        case "CALLBACK_IN_FLIGHT":{
            owner.bind();CountDownLatch entered=new CountDownLatch(1),allow=new CountDownLatch(1);Thread original=new Thread(()->owner.callback(()->{entered.countDown();try{waitFor(allow);}catch(Exception e){throw new RuntimeException(e);}}));original.start();waitFor(entered);owner.close();ok(p.unbinds==1 && !owner.returned() && !E13BindingOwner.allReturned());allow.countDown();join(original);break;
        }
        case "LATE_CALLBACK":{
            owner.bind();owner.close();AtomicInteger adopted=new AtomicInteger();ok(!owner.callback(adopted::incrementAndGet));ok(adopted.get()==0);break;
        }
        case "UNBIND_EXCEPTION":{
            owner.bind();p.error="UNBIND";owner.close();owner.close();owner.close();ok(p.unbinds==1 && !owner.returned() && !E13BindingOwner.allReturned());ok(owner.unbindError().equals(IllegalArgumentException.class.getName()));
            System.out.println("PASS_EXPECTED_UNPROVEN_ORIGINAL_KEPT assertions="+assertions+" "+owner.state()+" platformSubstituteOnly=true noAndroidBindingExists=true");return;
        }
        default:throw new IllegalArgumentException("exact finite binding case required");
        }
        owner.close();ok(p.binds==1 && p.unbinds==1);ok(owner.returned() && E13BindingOwner.allReturned());ok(!owner.callback(()->{throw new AssertionError("must not adopt late endpoint");}));
        System.out.println("PASS_PRODUCTION_BINDING_OWNER "+mode+" assertions="+assertions+" "+owner.state()+" platformSubstituteOnly=true");
    }
}
