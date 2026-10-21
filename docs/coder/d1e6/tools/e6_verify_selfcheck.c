#include "../native/e6_verify.h"
__declspec(dllimport) void __stdcall ExitProcess(unsigned int);
static unsigned failures,count;
#define CHECK(x) do {count++;if(!(x))failures++;}while(0)
void main(void){
    int64_t t[6]={0,208333,416667,625000,833333,1000000};
    for(int i=0;i<6;i++)CHECK(e6_frame_predicate(i,256,144,t[i],t)==E6_OK);
    CHECK(e6_frame_predicate(5,256,144,1041667,t)==E6_PTS);
    CHECK(e6_frame_predicate(5,256,144,1001000,t)==E6_OK);
    CHECK(e6_frame_predicate(5,256,144,1001001,t)==E6_PTS);
    CHECK(e6_frame_predicate(6,256,144,1200000,t)==E6_EXTRA_FRAME);
    CHECK(e6_frame_predicate(0,255,144,0,t)==E6_DIMENSIONS);
    CHECK(e6_frame_predicate(-1,256,144,0,t)==E6_EXTRA_FRAME);
    CHECK(e6_eof_predicate(6,1,1)==E6_OK);
    CHECK(e6_eof_predicate(5,1,1)==E6_INCOMPLETE_EOF);
    CHECK(e6_eof_predicate(7,1,1)==E6_INCOMPLETE_EOF);
    CHECK(e6_eof_predicate(6,0,1)==E6_INCOMPLETE_EOF);
    CHECK(e6_eof_predicate(6,1,0)==E6_INCOMPLETE_EOF);
    if(count!=17)failures++;
    ExitProcess(failures?1:0);
}
