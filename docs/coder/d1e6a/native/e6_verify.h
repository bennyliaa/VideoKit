#ifndef VIDEOKIT_E6_VERIFY_H
#define VIDEOKIT_E6_VERIFY_H
#include <stdint.h>
/* Original exact six-frame, dimensions, 1000us inclusive PTS and full EOF requirements. */
enum { E6_OK=0,E6_DIMENSIONS=1,E6_EXTRA_FRAME=2,E6_PTS=3,E6_MISSING_PTS=4,
       E6_DEMUX=5,E6_SEND=6,E6_RECEIVE=7,E6_DRAIN=8,E6_INCOMPLETE_EOF=9 };
static inline int e6_frame_predicate(int accepted,int width,int height,int64_t pts,const int64_t *timeline){
    if(width!=256 || height!=144)return E6_DIMENSIONS;
    if(accepted<0 || accepted>=6)return E6_EXTRA_FRAME;
    if(pts<0 || pts>2000000)return E6_PTS;
    int64_t difference=pts-timeline[accepted];
    if(difference>1000 || difference< -1000)return E6_PTS;
    return E6_OK;
}
static inline int e6_eof_predicate(int accepted,int demux_eof,int decoder_eof){
    return accepted==6 && demux_eof && decoder_eof?E6_OK:E6_INCOMPLETE_EOF;
}
#endif
