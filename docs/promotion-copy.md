# 介绍文案

## 一句话

Distributed Systems Audit：沿真实调用链查证据，把跨组件故障整理成可验证的根因、修复与恢复验收方案。

## 中文介绍

Distributed Systems Audit 是一个用于跨组件正确性与故障恢复的 Agent Skill，调用名为 `distributed-system-audit`。

它从真实现象或明确的审计问题出发，还原调用链、定义不变量，再组合状态、并发、故障和时序进行验证。二次评审会区分已确认问题、源码风险和测试缺口，排除误报、合并同根因，形成修复与验收计划。

不绑定具体项目或技术栈。默认先审计；只读任务不修改文件和系统。没有证据就保留未验证，不把“方法返回成功”当作“业务已经完成”。

模型行为和宿主兼容性以实际评测记录为准，不承诺自动找全所有问题。发布时补入已确认的公开仓库链接。

## English

Distributed Systems Audit is an architecture-neutral agent skill for cross-component correctness and recovery. Trace the real execution path, define invariants, verify failure timing, challenge false positives, and group evidence-backed findings into repair and acceptance plans. Read-only boundaries, static package validation, host invocation, and model behavior evaluation remain explicit and separate.
