package com.videokit.spike.e4;
import java.nio.file.*;
/** Source-reviewed location and future disposition pin. No CLI/env override and no current release. */
final class E13GuardLocation {
 static final Path ROOT=Paths.get("D:/CodexProjects/VideoKit/docs/tester/VideoKit-device-custody/HA1Q6WXR");
 static final String DISPOSITION_SHA="ABSENT";
 static String dispositionSha(){return DISPOSITION_SHA;}
 static Thread returnCustodian(Runnable body,String id){Thread t=new Thread(body,"e13-original-claim-return-"+id);t.setDaemon(false);return t;}
 private E13GuardLocation(){}
}
