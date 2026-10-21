package com.videokit.spike.e4;

import java.io.IOException;
import java.nio.file.Path;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/** Activation's actual fresh proof. Catalog is historical authority; holders are always this host's. */
public final class E9CurrentObservation implements E5AAdmission.Proof {
    public interface Platform extends E9OwnedFiles.Port {void requireIdleOriginalHost()throws Exception;}
    private static final Set<E9CurrentObservation> ACTIVE=ConcurrentHashMap.newKeySet();
    private final E9Catalog.Trusted trust;private final E9OwnedFiles files;private final Platform platform;private boolean used,completed,failed;
    private String stage="NEW";public E9CurrentObservation(Path root,E9Catalog.Trusted trust,Platform platform){this.trust=Objects.requireNonNull(trust);this.platform=platform;files=new E9OwnedFiles(root,platform);}
    public Path budget(){return files.root.resolve("e4a_output_budget");}public int registered(){return files.registered();}public boolean actualReturnProven(){return completed&&!failed&&files.returned()&&!ACTIVE.contains(this);}
    public static int retained(){return ACTIVE.size();}
    private void exactNames(String path,Set<String> allowed,int max)throws Exception{Set<String> names=new HashSet<>(files.entries(path,max));if(!names.equals(allowed))throw new IOException("E9_CURRENT_CONTROL_INVENTORY");}
    public String observe(){
        synchronized(E9CurrentObservation.class){
            if(used||!ACTIVE.isEmpty()||E5N2Recovery.retainedOperations()!=0||E5AFinalObservation.retained()!=0)return "BLOCKED E9_PRIOR_OPERATION_PENDING";used=true;E5AAdmission.invalidateCurrent();ACTIVE.add(this);Throwable original=null;
            try{
                stage="CURRENT_HOST";platform.requireIdleOriginalHost();E9Catalog c=trust.catalog();
                stage="ORIGINAL_GUARDS";E9LegacyState.lockOriginalGuards(files);
                stage="LEGACY_AND_LEDGER";E4Owned<E9OwnedFiles.Handle> ledger=E9LegacyState.openAndValidate(files,true);
                String base="e4a_output_budget/legacy-acceptance",scope=base+"/"+c.record.get("migration"),actors=scope+"/actors";
                stage="EXACT_POLICY_INVENTORY";files.directory(base);files.directory(scope);files.directory(actors);exactNames(base,Set.of(c.record.get("migration")),1);exactNames(scope,Set.of("actors","n2-v2.acceptance","n2-v2.commit"),3);
                Set<String> intentNames=new HashSet<>();for(int i=1;i<=2;i++)if(!c.device.get("intent"+i).equals("ABSENT"))intentNames.add("000"+i+".intent");exactNames(actors,intentNames,2);
                stage="BOUND_DEVICE_POLICY";for(int i=1;i<=2;i++)if(!c.device.get("intent"+i).equals("ABSENT")){byte[] raw=files.read(actors+"/000"+i+".intent",2048,true);if(!E9Record.sha(raw).equals(c.device.get("intent"+i)))throw new IOException("E9_CURRENT_INTENT_CHANGED");E9Actor from=E9Actor.fromIntent(raw,c.reserves[i-1].hash());if(!from.hash().equals(c.actors[i-1].hash()))throw new IOException("E9_CURRENT_ACTOR_CHANGED");}
                if(!E9Record.sha(files.read(scope+"/n2-v2.acceptance",4096,true)).equals(c.device.get("payload"))||!E9Record.sha(files.read(scope+"/n2-v2.commit",256,true)).equals(c.device.get("commit")))throw new IOException("E9_CURRENT_POLICY_CHANGED");
                stage="CURRENT_LEDGER_AND_DURABILITY";E9LegacyState.ledger(files.read(ledger,131072));files.force(ledger);
                for(String rel:new String[]{actors,scope,base,"e4a_output_budget/N2-e5-recovery","e4a_outputs","e4a_output_budget"})files.sync(rel);
            }catch(Throwable t){original=t;failed=true;}
            try{files.closeReturnedResources();}catch(Throwable close){failed=true;if(original!=null)original.addSuppressed(close);else original=close;}
            if(original==null&&files.returned()){completed=true;ACTIVE.remove(this);E5AAdmission.fromCurrentObservation(this);return "FRESH_E9_OBSERVATION_ADMITTED retiredHistoryQueries=0 oldCloseACK=false originalOwnersReturned=true";}
            return "BLOCKED "+stage+":"+(original==null?"OWNER_UNKNOWN":E5Trace.safe(original.getClass().getSimpleName()+":"+original.getMessage()));
        }
    }
}
