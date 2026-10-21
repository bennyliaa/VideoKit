package com.videokit.spike.e4;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;

/** Future source preparation only, after real final facts and independent review. No E9 invocation. */
public final class E9ActivationPolicyExport {
    public static void export(E9Registry registry,Path newFolder)throws Exception{
        if(!registry.trust.environment.equals("DEVICE_HA1Q6WXR"))throw new IOException("E9_SYNTHETIC_CATALOG_CANNOT_BECOME_RELEASE_POLICY");
        registry.requireDeploymentQuiet();E9Catalog catalog=registry.finalCatalog();
        // Build input is the already reviewed final catalog. APK hashes enter a separate release
        // record only after the future build; requiring that record here would create a cycle.
        E9Record.digest(registry.trust.review);
        if(Files.exists(newFolder,LinkOption.NOFOLLOW_LINKS))throw new IOException("E9_EXPORT_NEW_DIRECTORY_ONLY");Files.createDirectory(newFolder);
        String source="package com.videokit.spike.e4;\npublic final class E9BuildPolicy {\n"+
            " public static final String ROLE=\"ACTIVATION\",CATALOG_SHA=\""+catalog.record.hash()+"\",CATALOG_BASE64=\""+E9Record.pack(catalog.record.bytes())+"\",SOURCE_ENVIRONMENT=\"DEVICE_HA1Q6WXR\";\n"+
            " public static final String CATALOG_HEAD=\""+catalog.record.get("head")+"\";\n"+
            " public static final int GATE_ABI=1; public static String role(){return ROLE;} public static String catalogDigest(){return CATALOG_SHA;} private E9BuildPolicy(){}\n}\n";
        Files.write(newFolder.resolve("E9BuildPolicy.java"),source.getBytes(StandardCharsets.US_ASCII),StandardOpenOption.CREATE_NEW);Files.write(newFolder.resolve("final.acceptance.json"),catalog.record.bytes(),StandardOpenOption.CREATE_NEW);
    }
    private E9ActivationPolicyExport(){}
}
