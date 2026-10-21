package com.videokit.spike.e4;

import java.io.IOException;

/** Shared entry guard. The prepare build cannot turn a commit/return receipt into activation. */
public final class E9Phase {
    public static void requireProduct()throws IOException {requireObservationRole();E5AAdmission.requireCurrent();}
    private static volatile E9Catalog.Trusted releaseCatalog;
    public static void requireObservationRole()throws IOException{catalog();}
    public static E9Catalog.Trusted catalog()throws IOException{
        if(!E9BuildPolicy.role().equals("ACTIVATION")||E9BuildPolicy.catalogDigest().equals("ABSENT"))throw new IOException("E9_PREPARE_PRODUCT_DISABLED");
        E9Catalog.Trusted value=releaseCatalog;if(value==null){synchronized(E9Phase.class){value=releaseCatalog;if(value==null){value=E9Catalog.fromTrustedRelease(E9Record.unpack(E9BuildPolicy.CATALOG_BASE64,16384),E9BuildPolicy.catalogDigest(),E9BuildPolicy.SOURCE_ENVIRONMENT);releaseCatalog=value;}}}return value;
    }
    public static void rejectLegacyRecovery()throws IOException{throw new IOException("E9_LEGACY_RECOVERY_ENTRY_DISABLED");}
    public static void requireMigrationPair(String app,String test)throws IOException{if(!E9BuildPolicy.role().equals("PREPARE"))throw new IOException("E9_MUTATING_ENTRY_DISABLED");E9Record.digest(app);E9Record.digest(test);}
    private E9Phase(){}
}
