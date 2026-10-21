package com.videokit.spike.e4;
import java.util.*;
/** Exact previously accepted legacy baseline, NOT a migration approval or actor-final catalog. */
public final class E9LegacyProfile {
    public static final String POLICY="D1-E8A-LEGACY-N2-TERMINAL-ACCEPTANCE-V2";
    public static final String FENCE="662e9ecd-bede-42e6-bb58-ce81d668ff44";
    public static final String PREFIX_SHA="f32b1a35689fff1ffae230f2efcd10fbf42adc8c3e2d3e74892d2d8c7da98aba";
    public static final int PREFIX_BYTES=1011;public static final long MIN_CONSUMED=107218;
    public static final SortedMap<String,String> IMMUTABLE;
    static {TreeMap<String,String> m=new TreeMap<>();
        m.put("e4a_output_budget/N2-e5-recovery/identity.before","46b6dd034b8c852bce046d9e1b89d36f7be5538753c505408ebed99c968e8873");
        m.put("e4a_output_budget/N2-e5-recovery/journal.before","a0eccece0d94a6eb9f8554ce7dde127493b26fd1935c1fac0c0cb9e9d1a39e98");
        m.put("e4a_output_budget/N2-e5-recovery/lease.before","160829abef2ebb9f1ee2950aa0ea9d69389fac9cedde3b3cf980ed2de71432e9");
        m.put("e4a_output_budget/N2-e5-recovery/ledger.before","4a8f0409aee7bf91576927b932ad390bf941c465ac303200e6f2bdcdb7d900eb");
        m.put("e4a_output_budget/N2-e5-recovery/recovery.owner","91944886001df30b3a50c1b0b4382ba259cac2c2342d2c8f2da988484c62f30c");
        m.put("e4a_output_budget/N2-e5-recovery/proof.txt","0bc78f5a6c54a17f065a997785c7d077512682864062594ccab8c3185438a0c6");
        m.put("e4a_output_budget/N2-e5-recovery/guard.identity","c2b0936fbb6114548d27df00d7521deb5397457ecbea9399be418a133569e113");
        m.put("e4a_output_budget/identity.anchor","2b5624333ada8407460c3ef45fd38d21b562b3617736043846d563e198e8aa36");
        m.put("e4a_output_budget/N2-e5-recovery.complete","fc14064f847a87b92d3227f614f97749fffdca00af8fbbd1e5b4720ff363f37d");
        m.put("e4a_output_budget/operation.pending.N2-e5-aborted","e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");
        m.put("e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.identity","46b6dd034b8c852bce046d9e1b89d36f7be5538753c505408ebed99c968e8873");
        m.put("e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.journal","a872941459a317d98144335e561d6df0a397cc602365720066047ff83b8e50bf");
        m.put("e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494.lease","3a012de046eae6a636b4e2a28a622f16aac190e1a4fa056e774ac977cb57c104");
        IMMUTABLE=Collections.unmodifiableSortedMap(m);
    }
    public static E9Record proposal()throws java.io.IOException {
        return new E9Record(E9Record.map("kind","descriptor","policy",POLICY,"task",E5N2Recovery.TASK,"budget",E5N2Recovery.BUDGET,"oldAttempt","8c6673b7-38a5-4a24-838d-ca8466d8b75f","fence",FENCE,"prefixSha",PREFIX_SHA,"prefixBytes","1011","consumed","107218","archive",archiveHash(),"scope","TERMINAL_LEGACY_NO_MEDIA_MUTATION","schema","2","ownerId","64522:20304:10221","leaseId","64522:20385:10221","oldEpoch","5131975343750146374","oldGeneration","1","oldService",E5N2Recovery.SERVICE,"oldCloseACK","FALSE"),4096);
    }
    public static String archiveHash(){StringBuilder b=new StringBuilder();for(Map.Entry<String,String> e:IMMUTABLE.entrySet())b.append(e.getKey()).append(' ').append(e.getValue()).append('\n');return E9Record.sha(b.toString().getBytes(java.nio.charset.StandardCharsets.US_ASCII));}
    private E9LegacyProfile(){}
}
