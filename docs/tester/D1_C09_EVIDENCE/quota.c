/* Independent VideoKit allocator quota for FFmpeg's existing --malloc-prefix hook.
 * No codec algorithm changes. Fixed bookkeeping, no tracking allocations. */
#define _POSIX_C_SOURCE 200112L
#include <stdlib.h>
#include <stdint.h>
#include <errno.h>
#include <pthread.h>
#include <string.h>
#define CAP (64u*1024u*1024u)
#define BLOCKS 4096
typedef struct {void *ptr;size_t size;} Record;
static Record records[BLOCKS];
static pthread_mutex_t lock=PTHREAD_MUTEX_INITIALIZER;
static size_t current,peak,count;
static int find(void *p){for(int i=0;i<BLOCKS;i++)if(records[i].ptr==p)return i;return -1;}
static void *allocate(size_t alignment,size_t size,int *error){
    if(!size)size=1;
    pthread_mutex_lock(&lock);int slot=find(NULL);void *p=NULL;int code=ENOMEM;
    if(slot>=0 && size<=CAP-current){code=posix_memalign(&p,alignment,size);if(!code){records[slot]=(Record){p,size};current+=size;count++;if(current>peak)peak=current;}}
    pthread_mutex_unlock(&lock);*error=code;return p;
}
int vk_c09_posix_memalign(void **p,size_t alignment,size_t size){int error;void *result=allocate(alignment,size,&error);if(!error)*p=result;return error;}
void *vk_c09_malloc(size_t size){int error;void *p=allocate(64,size,&error);if(error)errno=error;return p;}
void *vk_c09_memalign(size_t alignment,size_t size){int error;void *p=allocate(alignment,size,&error);if(error)errno=error;return p;}
void vk_c09_free(void *p){
    if(!p)return;pthread_mutex_lock(&lock);int slot=find(p);
    if(slot<0){pthread_mutex_unlock(&lock);abort();}
    size_t size=records[slot].size;free(p);records[slot]=(Record){0};current-=size;count--;pthread_mutex_unlock(&lock);
}
void *vk_c09_realloc(void *p,size_t size){
    if(!p)return vk_c09_malloc(size);
    if(!size)size=1;
    pthread_mutex_lock(&lock);int slot=find(p);void *next=NULL;
    /* Charge both old and new while copying; never release the old pointer on failure. */
    if(slot>=0 && count<BLOCKS && size<=CAP-current && !posix_memalign(&next,64,size)){
        size_t old=records[slot].size;size_t transient=current+size;if(transient>peak)peak=transient;
        memcpy(next,p,old<size?old:size);free(p);records[slot]=(Record){next,size};current=transient-old;
    }
    pthread_mutex_unlock(&lock);if(!next)errno=ENOMEM;return next;
}
size_t vk_c09_current(void){pthread_mutex_lock(&lock);size_t value=current;pthread_mutex_unlock(&lock);return value;}
size_t vk_c09_peak(void){pthread_mutex_lock(&lock);size_t value=peak;pthread_mutex_unlock(&lock);return value;}
/* Executed only by explicit device test; five small-policy allocations prove aggregate denial. */
int vk_c09_probe(void){
    if(vk_c09_current()!=0)return -1;
    void *p[4]={0};int result=-2;
    for(int i=0;i<4;i++){p[i]=vk_c09_malloc(16u*1024u*1024u);if(!p[i])goto cleanup;}
    void *excess=vk_c09_malloc(1);if(excess){vk_c09_free(excess);goto cleanup;}
    void *resize=vk_c09_realloc(p[0],1);if(resize){p[0]=resize;goto cleanup;}
    if(vk_c09_current()!=CAP)goto cleanup;
    vk_c09_free(p[0]);p[0]=vk_c09_malloc(1);if(!p[0])goto cleanup;result=0;
cleanup:
    for(int i=0;i<4;i++)vk_c09_free(p[i]);
    return vk_c09_current()==0?result:-3;
}
