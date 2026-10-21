# D1 E6B MP4 单项独立审证 V1.0

2026-10-17，HA1Q6WXR/TB138FC/API31/user0，version8/D1-E6B。batch D1-E4A-E6B-NORMAL-TABLET-20261017。结论 **PASS，仅 MP4 单项**。该文件不是两个正常结果的联合 receipt，不得用于 cancel 准入。

依据本批 `D1_E6B_NORMAL_EVIDENCE/normalMp4SixRealFrames-*` 原始 instrumentation/logcat/post-state 和独立审证 JSON：JUnit 单测通过，2.699s；本 host 原最终观察 FRESH_OBSERVATION_ADMITTED。

task/output：fbe4330b111b4b05a93c467413eb8d34 / fbe4330b-111b-4b05-a93c-467413eb8d34，host11353/codec11374 UID10221，epoch968264325322937788，generation1，service de9431fb-d89b-4bd7-804a-0304e699fa1f。

六源/六输入/六编码 samples/完整六 accepted，输出 PTS 0/208333/416667/625000/833333/1000000us，与实际源相对时间线最大差0us。独立 validator task72f1f659d51a4a618c337ef1c116e978、PID11532/UID99061、mode11/phaseVERIFIED；E6_NATIVE_OK/site0、packets6/decoded6/accepted6、demux_eof1/decoder_eof1/drain1，readAt1/53567字节。末帧 source task e01967ce6909476ca219e22158ae34fc/mode10，与验证器分离。

六帧实际 thumbnail/content/mapping 原严格门与完整 EOF 通过，最大 luma MAE1.3194444444444444，源区分度19.479166666666668/输出区分度19.520833333333332。七 CPU 原始账本 actual_death/source_released/slot_released=true，pending_calls/operations/consumers/failed_closes=0；源句柄关闭、remote native/live/unknown=0，codec/sink/lease/frames 归还；callback8进8返、无未知/失败，CONTROL0、ACTUAL_OWNERS_RETURNED、originalOwnerReturned=true。READY 不仅由 native OK 推断。

输出53567字节，device64522/inode4176，生产 SHA256 6877567a65c7811131fe38d17bb642fa906bcb0c10fa38c3ba636c70dcaafb5e。journal READY3，稳定 budget730a73e1-50e1-4198-a515-047104f00e31 唯一 R/S READY53567；原53651消费保留，合计107218，reserved0/无pending；链式账本 SHA256 f32b1a35689fff1ffae230f2efcd10fbf42adc8c3e2d3e74892d2d8c7da98aba。

原始 instrumentation SHA256 06d37744d73db58fa42b98c6dce7ed66caf87d82b6ce9bff6163981d953205f4；logcat36382d913d8c211cbfee48ba6d2c68c5159079cf7eb24e3239b59c1b7ba5f683；post-state24e435658438429ffc91c164e52d8bca1ff51721be71d576a4e93d32c5d38a8b。Tester 无额外媒体读取/输出导出、产品重跑0。具体每任务实际计数保留在独立审证 JSON。

该结果支持 E5C-REG-F01 在 E6B/本平板/本 MP4 六帧链路范围关闭；AVI、能力及 cancel 不由该结果推断。D1 NOT_PASSED/M0 NOT_STARTED。
