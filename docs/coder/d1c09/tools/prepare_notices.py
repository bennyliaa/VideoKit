from pathlib import Path
import hashlib,json,shutil,sys
root=Path(sys.argv[1]).resolve();base=root/'docs/coder/d1c09';src=base/'upstream/source/ffmpeg-8.0.3';assets=base/'notice-assets/licenses';assets.mkdir(parents=True,exist_ok=True)
for name in ['LICENSE.md','COPYING.LGPLv2.1','COPYING.LGPLv3','COPYING.GPLv2','COPYING.GPLv3']:shutil.copyfile(src/name,assets/name)
special=['libavcodec/jfdctfst.c','libavcodec/jfdctint_template.c','libavcodec/jrevdct.c','libavcodec/faandct.c','libavutil/adler32.c','libavutil/avsscanf.c']
for name in special:
 text=(src/name).read_text(encoding='utf-8');end=text.index('*/')+2;(assets/(Path(name).name+'.NOTICE.txt')).write_text(text[:end]+'\n',encoding='utf-8')
notice='''VideoKit D1 C09 local Debug CPU experiment — not a production/distribution approval.

FFmpeg 8.0.3 from https://ffmpeg.org/releases/ffmpeg-8.0.3.tar.xz
SHA-256 6136812ea6d4e68bdba27e33c2a94382711cdf4f8602ffef056ff792bd6f9818
Official detached signature verified with FCF986EA15E6E293A5644F10B4322F04D67658D8.
No local upstream modifications. LGPL-2.1-or-later aggregate build plus retained
IJG, ISC, Zlib and MIT notices for actually compiled files. Full license texts and
special original copyright/permission notices accompany this asset.

This software is based in part on the work of the Independent JPEG Group.
The jfdctfst.c, jfdctint_template.c and jrevdct.c files are unmodified relative to
the signed FFmpeg 8.0.3 archive; upstream modifications relative to IJG remain
identified in the corresponding retained full source files. No local additions
or deletions were made to those files. faandct, Adler-32 and avsscanf retain their
original ISC, Zlib and MIT notices and upstream attribution.

Complete corresponding source archive, generated configurations, build commands,
object/header license maps, unstripped shared libraries and source delta are in
the same C09 frozen project delivery under docs/coder/d1c09. Dynamic linking does
not by itself close distribution or replacement obligations. This experiment
does not restrict LGPL-permitted modification/debugging/reverse engineering.
Production host SDK, replacement/relink materials for external recipients,
EULA/store/patent requirements and distribution remain separately unapproved.

MPEG4 requires H263 decoder/parser transitively; they are compiled and registered,
but the adapter only accepts AVI/MPEG4-part2 or MP4/H264 input. No encoders, network
or file protocols, hardware decoders, GPL/nonfree/version3 or external codec libs.
Media3 1.9.3 continues as the existing Apache-2.0 Android playback/export adapter;
this finite CPU experiment does not replace Flutter App or independent Kit design.
'''
(assets/'NOTICE-C09.txt').write_text(notice,encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
mapping=json.loads((base/'evidence/ffmpeg-object-source-license-map.json').read_text(encoding='utf-8'))
sbom={'bomFormat':'CycloneDX','specVersion':'1.6','version':1,'metadata':{'component':{'type':'application','name':'VideoKit D1 C09 local Debug experiment','version':'D1-20261016-C09'}},'components':[{'type':'library','name':'FFmpeg','version':'8.0.3','purl':'pkg:generic/ffmpeg@8.0.3','hashes':[{'alg':'SHA-256','content':sha(base/'upstream/ffmpeg-8.0.3.tar.xz')}],'licenses':[{'expression':'LGPL-2.1-or-later AND IJG AND ISC AND MIT AND Zlib'}],'properties':[{'name':'scope','value':'debug only; full object/header map ffmpeg-object-source-license-map.json'}]}], 'properties':[{'name':'app-coordinate-source','value':'app/gradle.lockfile; inherited graph unchanged, dependency report captured with concentrated build'},{'name':'NDK','value':'30.0.16248370 Android API31 system libc/libm and JNI headers; not third-party runtime codec dependency'},{'name':'release','value':'no CPU libraries/classes/services/notices included; verify actual release artifact separately'}]}
(base/'evidence/c09-sbom.cdx.json').write_text(json.dumps(sbom,indent=2),encoding='utf-8')
print('Complete licenses, six special notices, IJG attribution and SBOM prepared')
