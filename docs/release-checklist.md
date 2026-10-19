# 发布清单

## 发布标识

仓库和 Skill 名称：`distributed-system-audit`。

展示名：**Distributed Systems Audit / 分布式系统审计**。拟用首版：`v0.1.0`。许可证：[MIT](../LICENSE)。

本轮候选包名为 `dist/distributed-system-audit-v0.1.0-rc1.zip`，与双语 README 及 CI 的构建路径一致。历史 ZIP 不作为本轮交付；发布前必须将候选包解压后逐文件对照当前发布源文件，不能仅凭 ZIP 的 CRC 正常判断它是最新版。

审计规则面向通用的跨组件正确性与故障恢复；不绑定具体业务项目、框架、中间件、状态名、严重级别或部署流程。示例为合成材料，不作为生产证据。

## 本地检查

- [ ] 按 [README](../README.zh-CN.md) 安装维护依赖，执行静态检查、回归测试和打包命令。
- [ ] 将 ZIP 解压到临时目录，确认顶层目录名、入口、元数据、SOP 与源文件一致。
- [ ] 复核提交范围，排除凭据、真实业务日志、个人数据、IDE 文件和运行产物。
- [ ] 核对英文与中文 README 的标识、安装步骤、功能与验证边界一致。
- [ ] 按[行为评测](../evals/manual-evaluation.md)记录模型/宿主组合的真实结果；未执行就注明未验收。
- [ ] 在实际宿主发现并调用 `$distributed-system-audit`，不要把包格式通过当作调用已通过。

已完成的补强与本地验收见[补强后评审](strengthening-review.md)和[行为证据](../evals/results/2026-10-19/README.md)。该记录不能代替上述实际宿主、远程 CI 和最终发布操作。

## 远程发布

1. 确认账户、公开范围和仓库地址；建议仓库名与 Skill 标识一致。
2. 审阅并精确暂存发布文件，创建 commit；按用户授权创建远程、绑定地址并推送。
3. 等待远程 CI，分别核对 Windows/Linux 结果。
4. 创建首版 tag/Release，上传 ZIP；发布说明分别报告静态检查、包完整性、宿主调用、行为评测的状态。
5. 从公开仓库重新克隆并验收；将实际安装链接补入双语 README，再使用[介绍文案](promotion-copy.md)。

本地准备不代表远程仓库、push、tag 或 Release 已完成。仓库检查通过也不代表生产审计、跨宿主兼容性或模型行为已验收。

## Release 说明模板

```text
v0.1.0 — Distributed Systems Audit
- Evidence-first audit of cross-component correctness and recovery.
- Architecture-neutral invariants, failure timing, root-cause triage, and acceptance.
- English/Chinese READMEs, reusable prompts, and a synthetic example.
- Package checks, install archive integrity tests, and Windows/Linux CI configuration.

Static validation: report actual commands/results.
Archive installation: report actual commands/results.
Host invocation and model behavior: report actual evaluation evidence or not evaluated.
```
