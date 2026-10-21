# INPUT_SINK04 既有返回字段与终态边界 V1.0

候选D1-20261021-INPUT-SINK04。仅强化已有端口契约及结果消费，不新增资源/验证计数框架或宿主协议字段；不是M0最终API。

## 结果消费顺序

同原动作准入后才改变一次进入标记。原结果返回后依次核类型、既有字段、允许状态转换，再写ACK/receipt/业务事实；错误结果按同一原stage失败消费。null stage表示原调用已经进入但没有可观察stage，保留INVOCATION_UNKNOWN，不改回NOT_ADMITTED、不盲重试。

直接原future首次get、晚observe的ExecutionException/CancellationException保持B03规则；已消费终局不反复抛私有错误，WRITE UNKNOWN每原调用一次。READY/ABORT/QUERY观察原stage时以Object接收并先检查，避免错误类型触发泛型桥转换异常、把view永久留在pending。coordinator自身也做同样的类型/状态-token检查，不能把null交给后续解引用。

firstFailure先登记稳定错误再完成失败view。协议坏值用OUTPUT_INVALID_HOST_RESULT，已有WRITE非法count、reopen/validator错误沿用既有稳定code。先前timeout/失败优先，不被晚坏值或准确业务终态覆盖。错误不携带原私有message/cause。

## 已定义字段

| 阶段 | 接受条件 | 拒绝/保管条件 |
|---|---|---|
| grant | 原opaqueTask符合已有1..64字符格式；必需能力存在；捕获一次原task | getter异常脱敏；null/格式/能力不符在owner准入前拒绝。 |
| WRITE | Integer ACK，1..同原请求count；原offset/extent/budget准入检查保持 | null/负数/0/超count/溢出值/错类型不增加SDK确认下界/callerPos，登记原请求UNKNOWN一次。实际宿主可能已写，不称为实际0B。 |
| FLUSH/CLOSE | 完成stage的Void值为null | 非null值/错类型是失败；null stage为调用UNKNOWN。writer物理返回另有原证明，不能从ACK推出。 |
| REOPEN | Provider及Handle非null；已知length合法，null表示未知；完整EOF字节量与extent相符，顺序模式摘要相符 | 负数/超大或错length、非法read count、错误内容、缺Provider/Handle失败；源归还仍由原registry/workers决定，不能伪造close。 |
| VALIDATE | 原task、精确extent、已计算sha、既有kind及structurallyValid都正确 | null/type、错task/hash/kind、负数或溢出bytes、false receipt不成为validated，不重验证补绿。 |
| READY | String非空、至少一个非Character.isWhitespace字符、不含ISO控制字符；已有有效token须一致 | 空/null/blank/control/错类型不能成为READY；不新造token编码/密码学/长度协议。 |
| COMMIT | null Void ACK，准确原Commit对象及原task/token | 非null/type/null-stage保持业务UNKNOWN；线程返回不是未执行/已成功证明，readonly准确事实可在原归还后收敛。 |
| ABORT | null Void ACK | 坏ACK不能证明ABORTED；准确原QUERY/原authority另行仲裁，不重RPC。 |
| QUERY/terminal authority | Status及state非null；READY需要上述有效token，其他状态token必须null；兼容已有终态 | null/type/state-null/状态-token不匹配、已知token替换、READY/ABORTED互相覆盖、已知终态倒退WRITING均拒绝。 |
| COMMIT authority | 同原对象非阻塞读取准确task/token的UNKNOWN/CONFIRMED_COMMITTED/CONFIRMED_NOT_APPLIED | null/抛错不成为成功；UNKNOWN继续保管。未定义额外returned task/token字段，不能假装已验证其内部账本。 |

WRITING/UNKNOWN配null token是合法非终态响应，不是协议坏值，但不足以证明可以释放。cleanup无法确认终态时保持UNKNOWN/既有失败；不重QUERY。默认UNKNOWN accessor不会擦除已被有效原QUERY/ACK确认的终态；坏的矛盾authority也不得改写该终态。

## 业务未知与资源真实归还

非法READY/QUERY/terminal authority使当前终态证明不足。保持既有真实ACK/token、首错和字节UNKNOWN，同时以原owner内的未决状态挡住完整返回；准确、兼容、同原task的终态证明到来后才收敛。该未决位不是新释放ledger；仍只有原OWNERS、原registry和原coordinator线程决定资源归还。

所有host/validator/commit/reopen读回原任务未返时不接纳readonly终态，原查询ACK早到而同一查询尾段未返时也不能跨门。准确原authority确认ABORTED/READY/COMMITTED/NOT_APPLIED后，仍须原writer、原registry/workers、原coordinator callback/executor/thread真实返回。失败历史不清，NOT_APPLIED不称为SDK回滚/ABORTED。

本批原两QUERY复现的宿主真实记录均ABORTED，但其坏QUERY响应本身不能证明该事实。默认authority UNKNOWN时SDK保持未返；测试最后只开放该原宿主真实ABORTED记录完成清理，不反射改SDK、删除keeper或退出JVM代替归还。

## 适用矩阵和不能验证的字段

[返回值矩阵](D:/CodexProjects/VideoKit/docs/coder/d1input-sink04/return-value-matrix.json)含88项返回值、33项状态/授权和原2项QUERY回归；[阶段异常矩阵](D:/CodexProjects/VideoKit/docs/coder/d1input-sink04/phase-exception-matrix.json)保留九阶段×七异常结果；[既有字段映射](D:/CodexProjects/VideoKit/docs/coder/d1input-sink04/host-return-boundary-map.json)列出不适用分支。

- Void成功的null合法，Status/Provider/Validation/token的null不合法，不能统一把null当同一结果。
- 只有WRITE有字节ACK/caller position/UNKNOWN reservation，只有COMMIT有发布结果三态；不能给别的阶段捏造字段。
- Status没有返回task/output/授权ID；只用准确捕获task参数和相同原端口绑定。不能凭空添加返回nonce、授权签名或输出ID。
- Provider/Handle没有返回物理file/FD/source ID。完整长度、EOF/内容和顺序摘要能核内容约束，不能证明同一个物理FD/授权持久化；相同内容的另一物理源无法由这些字段区分。
- CommitOutcome枚举没有返回task/token载荷；SDK只能保证准确参数、相同保留对象、原物理返回门。宿主内部持久化账本/跨进程真实业务不在本批证明范围。
- token仍是不透明String，未定义密码学格式、编码、到期与新长度阈值。本批不证明token本身真实授权能力。
- 随机输出模式没有独立提供的最终期望摘要；保留原能力/extent/readback及受控验证资格，不扩写为实际媒体或物理身份成功。

同原gate、尾段和authority暂不可用矩阵分别记录；非法结果可能伴随真实副作用，不能退款UNKNOWN或因校验拒绝推导回滚。真实Android FD/fsync/codec/muxer/容器、业务发布仍NOT_RUN，D1未过、M0未启。
