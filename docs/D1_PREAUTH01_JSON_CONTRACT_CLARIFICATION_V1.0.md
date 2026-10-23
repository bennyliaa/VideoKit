# PREAUTH01 JSON字节契约澄清

2026-10-23；负责人针对独立B观察O1裁定。原报告/观察及源码不改，本说明澄清测试要求中未充分区分的两种载荷。

- **预授权template**：批准绑定收到的完整UTF-8原字节SHA，不要求所有等价JSON只能有一种空白排版。仍严格拒绝重复/大小写重复字段、额外字段、不合法类型/数字/UTC及源/动作/预算等语义失配。固定原批准hash而改pretty字节，必须PREAUTH_EXTERNAL_HASH；明确以合成fixture批准pretty字节的新hash且语义有效时，允许接收。O1的这一行为符合当前字节绑定契约，不裁新增产品源码缺陷，也不冒称pretty应被语义拒绝。
- **CLI policy**：沿现有CONTRACT的明确要求使用canonical规范字节，不能用template的排版许可替policy放宽。独立B仍需实际或准确纯入口验证此项，不把此前未运行的CLI当已证。
- 任何template hash都只是受信启动输入，不证明批准人身份；本说明不授权真实LIVE，不允许caller自算hash冒充负责人真实批准。真实执行仍需新批准确外部批准。

原B192明确纯用例与1观察分列保留；本说明不把其变为已完成的9个runtime组，不改变旧FAIL/UNKNOWN/once、原90/30/15/10及只读动作/字节预算。
