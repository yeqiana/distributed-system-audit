# 分布式系统审计

[简体中文](README.zh-CN.md) | [English](README.md)

一个用于审计**跨组件正确性与故障恢复**的 Agent Skill：沿真实调用链检查不变量，用证据验证可达问题，再形成修复、回归与验收方案。

仓库名和 Skill 标识统一为 `distributed-system-audit`，英文展示名为 **Distributed Systems Audit**。

## 适用场景

当结果依赖多个组件，或受重试、所有权和故障时序影响时使用，例如：

- 事务已经提交，必要的下游处理却没有发生。
- 租约已被接管，旧 worker 仍然能覆盖结果。
- 缓存、投影与事实源不一致。
- 消息重复、乱序、部分失败，或确认时机不正确。
- 恢复任务显示健康，但业务读取仍然错误。
- 新旧版本混跑、发布或回滚会破坏恢复能力。

不绑定具体项目、语言、框架或中间件。目标链路可能有队列、缓存、Outbox、租约，也可能没有；按实际架构检查。普通单函数 Review 通常不需要整套深度审计。

## 工作方式

| 阶段 | 产出 |
| --- | --- |
| 建立证据 | 真实现象或预防性审计问题，区分事实与假设 |
| 还原链路 | 入口、持久化、异步交接、副作用、读取与恢复负责人 |
| 定义不变量 | 必须成立的业务约束与合法/非法状态转换 |
| 组合验证 | 相关的状态×并发×故障×时序场景 |
| 确认问题 | 可达路径、业务后果、证据与反证 |
| 检查恢复 | 发现方式、修复负责人、重放/补偿与收敛条件 |
| 二次评审 | 排除误报、合并同根因、安排修复与验收 |

代码味道不等于真实缺陷。先评估影响与触发可能性，再沿用目标项目的严重级别；缺少环境、未执行探针、没有生产证据，都必须明确标注。

## 直接使用

```text
使用 $distributed-system-audit。
审计指定业务链路的正确性与故障恢复能力。
范围：当前仓库，严格只读；不改文件、数据、配置，不重启、不注入故障。
先读当前源码和我提供的证据，列出不变量、可达路径、业务后果和恢复负责人。
区分已确认缺陷、源码风险与测试缺口，不能把未执行探针写成已复现。
二次评审排除误报、合并同根因，给修复顺序、永久回归和验收条件。
```

更多提示词：[审计](prompts/audit.md)、[二次评审](prompts/triage.md)、[修复交接](prompts/repair-handoff.md)。[旧 worker 示例](examples/stale-worker.md)是合成案例，不代表真实事故或已执行的测试。

## 安装

将完整 Skill 目录放到所用 Agent 的 skills 目录。至少保留 `SKILL.md`、`agents/` 和 `references/`；只复制入口文件会丢失引用资料。

Codex 默认本地目录结构：

```text
~/.codex/skills/distributed-system-audit/
  SKILL.md
  agents/openai.yaml
  references/audit-sop.md
```

Windows 下可在本仓库根目录安装已生成的发布包：

```powershell
$skillsRoot = Join-Path $env:USERPROFILE '.codex/skills'
$skillDestination = Join-Path $skillsRoot 'distributed-system-audit'
if (Test-Path -LiteralPath $skillDestination) { throw '请先比对已有安装，避免覆盖本地修改。' }
New-Item -ItemType Directory -Path $skillsRoot -Force | Out-Null
Expand-Archive -LiteralPath './dist/distributed-system-audit-v0.1.0-rc1.zip' -DestinationPath $skillsRoot
```

ZIP 内有 `distributed-system-audit/` 顶层目录。也可将仓库完整复制到同一目标目录，或在公开仓库地址确定后直接克隆到该位置。若使用自定义 skills 位置，以实际配置为准；其他 Agent 按各自的发现方式安装，并单独验证调用。

## 交付内容与边界

一份报告即可包含范围、不变量、证据、问题、排除项、根因分组、修复顺序、永久回归、恢复验收和剩余风险。[完整 SOP](references/audit-sop.md)提供按需选用的矩阵与模板，不要求每个系统照搬全部内容。

默认先审计。只读任务只分析和设计探针；获准的本地探针应隔离执行，并只清理本轮产物。修复代码、共享环境或生产修改、故障注入和部署，均受用户实际授权范围约束。

这个 Skill 提供方法和指令，不提供扫描器或基础设施，也不保证找全所有问题。“代码改了”或“单测全绿”不足以证明故障已经恢复。

## 校验与打包

仅维护仓库需要 Python 3.10+ 和开发依赖；使用 Skill 指令本身不需要 Python 运行环境。

```text
python -m pip install -r requirements-dev.txt
python scripts/test_skill.py
python -m unittest discover -s tests -v
python scripts/test_skill.py --package dist/distributed-system-audit-v0.1.0-rc1.zip
```

PowerShell 校验入口：

```powershell
pwsh -NoProfile -File scripts/test-skill.ps1
```

打包不会覆盖已有 ZIP，再次构建时请换一个输出文件名。仓库内只允许输出到 `dist/`，也可以输出到仓库外；`docs/` 等源目录会在写入前被拒绝。静态检查覆盖 YAML、元数据、引用资源和本地链接；回归测试验证坏包拒绝、安装完整性及合成记录的可复现性。CI 配置覆盖 Windows/Linux，本地通过不代表远程 CI 已通过。

**静态通过不等于模型行为通过。** 按[行为契约](evals/behavior-contracts.md)和[评测流程](evals/manual-evaluation.md)记录具体模型/宿主组合的真实结果。正式发布前查看[发布清单](docs/release-checklist.md)。

生成 11 组固定的盲评输入和隔离工作区：

```text
python scripts/prepare_behavior_eval.py
```

输出位于仓库外的临时目录，每例包含 Skill、请求、合成原始材料和隔离工作区；受测代理不接收评分标准。合成模型执行与代理行为分开验收，两者都不代表生产证据。

[本轮本地评测记录](evals/results/2026-10-19/README.md)为 11/11 例通过，保存完整答复、命令、输入哈希、评分依据和限制。具体继承模型版本未暴露，此结论仅对应所记录的运行，不外推至其他模型和宿主。[补强后评审](docs/strengthening-review.md)记录修复与剩余发布验收项。

## 仓库导航

| 路径 | 内容 |
| --- | --- |
| [SKILL.md](SKILL.md) | Agent 入口、证据规则和工作流程 |
| [agents/openai.yaml](agents/openai.yaml) | 展示元数据与调用策略 |
| [references/audit-sop.md](references/audit-sop.md) | 按需选择的矩阵与报告模板 |
| [prompts](prompts/audit.md) | 可复制的任务提示词 |
| [examples](examples/stale-worker.md) | 合成审计示例 |
| [evals](evals/manual-evaluation.md) | 行为验收标准与结果记录 |
| [docs/release-checklist.md](docs/release-checklist.md) | 发布检查 |
| [docs/promotion-copy.md](docs/promotion-copy.md) | 介绍文案 |
| [docs/skillpay-one-time-purchase.md](docs/skillpay-one-time-purchase.md) | Skill Pay 一次性商品上架准备与交付边界 |

## 许可证

[MIT](LICENSE)。
