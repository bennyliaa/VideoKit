package com.videokit.spike.e4;

import java.io.IOException;
import java.util.*;

/** Actual bounded file transaction. This class never appends media R/S or changes a legacy fence. */
public final class E9MigrationTransaction implements E9MigrationRun.Operations {
    public interface IdentitySource {E9Actor sample()throws Exception;boolean returned();int owned();String recoveryDigest();}
    private final E9OwnedFiles files;private final IdentitySource identity;private E9Record device;private boolean commitEntered,commitReturned;
    public E9MigrationTransaction(E9OwnedFiles files,IdentitySource identity){this.files=files;this.identity=identity;}
    public E9Actor identify()throws Exception{return identity.sample();}public boolean identityReturned(){return identity.returned();}public int identityOwned(){return identity.owned();}
    public boolean commitReturned(){return !commitEntered||commitReturned&&files.returned();}public int commitOwned(){return files.registered();}
    public String deviceDigest(){return device==null?"ABSENT":device.hash();}public String deviceRecord(){return device==null?"ABSENT":E9Record.pack(device.bytes());}
    public String recoveryDigest(){return identity.recoveryDigest();}
    public static E9Record commitRecord()throws IOException{return new E9Record(E9Record.map("kind","commit","descriptor",E9LegacyProfile.proposal().hash(),"payload",E9LegacyProfile.proposal().hash(),"policy",E9LegacyProfile.POLICY),256);}
    private void directory(String rel,String parent)throws Exception{if(files.exists(rel))files.directory(rel);else{files.mkdirNew(rel);files.sync(parent);}}
    private void names(String rel,Set<String> allowed,int max)throws Exception{for(String name:files.entries(rel,max))if(!allowed.contains(name))throw new IOException("E9_UNEXPECTED_CONTROL_ENTRY");}
    public void commit(E9Actor actor,String reserve,E9Record binding,E9MigrationRun.Stage stage)throws Exception{
        E9Phase.requireMigrationPair(actor.app,actor.test);if(commitEntered)throw new IOException("E9_TRANSACTION_ONCE");commitEntered=true;Throwable first=null;
        try{
            if(!identity.returned()||!actor.hash().equals(binding.get("actor"))||!reserve.equals(binding.hash()))throw new IOException("E9_TRANSACTION_BINDING");
            E9LegacyState.lockOriginalGuards(files);E4Owned<E9OwnedFiles.Handle> ledger=E9LegacyState.openAndValidate(files,true);
            String base="e4a_output_budget/legacy-acceptance",scope=base+"/"+actor.migration,actors=scope+"/actors";
            stage.at("DIRECTORIES_CREATING");directory(base,"e4a_output_budget");names(base,Set.of(actor.migration),1);directory(scope,base);names(scope,Set.of("actors","n2-v2.acceptance","n2-v2.commit"),3);directory(actors,scope);names(actors,Set.of("0001.intent","0002.intent"),2);
            String firstIntent=actors+"/0001.intent",ownIntent=actors+"/000"+actor.ordinal+".intent",payload=scope+"/n2-v2.acceptance",commit=scope+"/n2-v2.commit";
            boolean havePayload=files.exists(payload),haveCommit=files.exists(commit),haveFirst=files.exists(firstIntent);
            byte[] firstRaw=null;
            if(actor.ordinal==1){if(haveFirst||havePayload||haveCommit||files.exists(actors+"/0002.intent"))throw new IOException("E9_FIRST_ACTOR_EXISTING_TRANSACTION");}
            else {
                if(files.exists(ownIntent))throw new IOException("E9_RECOVERY_ALREADY_USED");
                if(haveFirst){firstRaw=files.read(firstIntent,2048,true);E9Record raw=E9Record.parse(firstRaw,2048);E9Actor predecessor=E9Actor.fromIntent(firstRaw,raw.get("reserve"));if(!predecessor.hash().equals(binding.get("predecessor"))||!E9Record.sha(firstRaw).equals(binding.get("predecessorIntent"))||predecessor.ordinal!=1||!predecessor.migration.equals(actor.migration))throw new IOException("E9_PREDECESSOR_INTENT");}
                else if(!binding.get("predecessorIntent").equals("ABSENT")||havePayload||haveCommit)throw new IOException("E9_MISSING_PREDECESSOR_INTENT");
            }
            byte[] acceptance=E9LegacyProfile.proposal().bytes(),commitBytes=commitRecord().bytes();
            // Validate every existing object before the first new actor2 write. Never overwrite a partial object.
            if(havePayload&&!Arrays.equals(files.read(payload,4096,true),acceptance))throw new IOException("E9_PAYLOAD_NOT_EXACT");
            if(haveCommit&&(!havePayload||!Arrays.equals(files.read(commit,256,true),commitBytes)))throw new IOException("E9_COMMIT_NOT_EXACT");
            stage.at("INTENT_CREATING");byte[] intent=actor.intent(reserve);files.create(ownIntent,intent,2048);files.sync(actors);
            stage.at("PAYLOAD_CREATING");if(!havePayload)files.create(payload,acceptance,4096);files.sync(scope);
            stage.at("COMMIT_CREATING");if(!haveCommit)files.create(commit,commitBytes,256);files.sync(scope);
            stage.at("COMMITTED_UNRETURNED");E9LegacyState.ledger(files.read(ledger,131072));files.force(ledger);
            files.sync("e4a_output_budget/N2-e5-recovery");files.sync("e4a_outputs");files.sync("e4a_output_budget");
            String intent1=actor.ordinal==1?E9Record.sha(intent):firstRaw==null?"ABSENT":E9Record.sha(firstRaw),intent2=actor.ordinal==2?E9Record.sha(intent):"ABSENT";
            device=new E9Record(E9Record.map("kind","device","migration",actor.migration,"descriptor",actor.descriptor,"intent1",intent1,"intent2",intent2,"payload",E9Record.sha(acceptance),"commit",E9Record.sha(commitBytes)),2048);
        }catch(Throwable t){first=t;throw t;}
        finally{try{files.closeReturnedResources();}catch(Throwable t){if(first!=null)first.addSuppressed(t);else if(t instanceof Exception)throw (Exception)t;else throw (Error)t;}finally{commitReturned=files.returned();}}
    }
}
