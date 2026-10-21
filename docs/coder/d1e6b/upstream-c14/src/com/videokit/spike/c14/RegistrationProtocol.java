package com.videokit.spike.c14;
/** Fixed primitive registration wire format. Framework metadata flags do not make a call one-way. */
public final class RegistrationProtocol {
    public static final int REGISTER=1,FAILURE=2,MAGIC=0x564b5232,VERSION=1,BYTES=16,MAX_INPUT=512;
    public static final int OK=0,DUPLICATE=1,RETIRED=2,ONEWAY=10,CODE=11,DESCRIPTOR=12,INPUT=13,SESSION=14,IDENTITY=15,ENDPOINT=16,DUPLICATE_IDENTITY=17,OVERFLOW=18,CALLBACK=19,TRANSACT_FALSE=20,REPLY_LENGTH=21,REPLY_MAGIC=22,REPLY_VERSION=23,REPLY_TRAILING=24,REPLY_ENUM=25,REPLY_GENERATION=26,TRANSPORT=27,MISSING=28;
    public static final class Rejected extends RuntimeException {public final int code;public Rejected(int code){super(name(code));this.code=code;}}
    public static boolean synchronous(int flags){return (flags&1)==0;}
    public static boolean error(int code){return code>=ONEWAY && code<=MISSING;}
    public static void identity(int pid,int uid,int hostPid,int hostUid){if(pid<=0 || pid==hostPid || uid<=0 || uid==hostUid || uid%100000<90000)throw new Rejected(IDENTITY);}
    public static int validateReply(int bytes,int magic,int version,int result,int generation){
        if(bytes<BYTES)throw new Rejected(REPLY_LENGTH);if(bytes>BYTES)throw new Rejected(REPLY_TRAILING);
        if(magic!=MAGIC)throw new Rejected(REPLY_MAGIC);if(version!=VERSION)throw new Rejected(REPLY_VERSION);
        if(result!=OK && result!=DUPLICATE && result!=RETIRED && !error(result))throw new Rejected(REPLY_ENUM);
        if((result<ONEWAY && (generation<=0 || generation>WorkerGenerations.MAX_WORKERS)) || (error(result) && generation!=0))throw new Rejected(REPLY_GENERATION);
        if(error(result))throw new Rejected(result);return result;
    }
    public static String name(int code){switch(code){case OK:return "CPU_REG_OK";case DUPLICATE:return "CPU_REG_DUPLICATE";case RETIRED:return "CPU_REG_RETIRED";case ONEWAY:return "CPU_REG_ONEWAY";case CODE:return "CPU_REG_CODE";case DESCRIPTOR:return "CPU_REG_DESCRIPTOR";case INPUT:return "CPU_REG_INPUT";case SESSION:return "CPU_REG_SESSION";case IDENTITY:return "CPU_REG_IDENTITY";case ENDPOINT:return "CPU_REG_ENDPOINT";case DUPLICATE_IDENTITY:return "CPU_REG_DUPLICATE_IDENTITY";case OVERFLOW:return "CPU_REG_OVERFLOW";case CALLBACK:return "CPU_REG_CALLBACK";case TRANSACT_FALSE:return "CPU_REG_TRANSACT_FALSE";case REPLY_LENGTH:return "CPU_REG_REPLY_LENGTH";case REPLY_MAGIC:return "CPU_REG_REPLY_MAGIC";case REPLY_VERSION:return "CPU_REG_REPLY_VERSION";case REPLY_TRAILING:return "CPU_REG_REPLY_TRAILING";case REPLY_ENUM:return "CPU_REG_REPLY_ENUM";case REPLY_GENERATION:return "CPU_REG_REPLY_GENERATION";case TRANSPORT:return "CPU_REG_TRANSPORT";case MISSING:return "CPU_REG_MISSING";default:return "CPU_REG_UNKNOWN";}}
    private RegistrationProtocol(){}
}
