# 分布式系统深度审计 SOP — 参考矩阵与模板

这些是按需选用的检查模板，不是目标项目必须采用的架构或状态命名。沿实际调用图选择相关部分；不存在的组件标为不适用，缺失的证据标为未验证。生产注入、数据修改和本地探针遵循入口文件的执行边界。

目录：1–3 现象、链路与状态；4–10 故障、所有权、消息、快照、恢复、兼容与任务；11–17 恢复、发现、根因与验收。

## 1. 现象卡
```text
现象：
发生时间：
影响用户/对象：
出现频率：
是否可复现：
关联请求/事件/对象标识：
错误码：
DB 状态：
缓存/投影状态（如适用）：
MQ / Outbox 状态：
生产日志/指标证据：
```
## 2. 全链路模板

下面是可选组件示意，实际链路可能分支、并行或省略其中环节；按项目实际依赖和事务边界重画。
```text
Client
↓
Gateway / Controller
↓
Business Service
↓
DB Transaction
↓
Fence / Lock / Lease
↓
Outbox
↓
Processor
↓
Projector
↓
Cache / Projection
↓
Reader
↓
MQ
↓
Consumer
↓
Delivery
↓
ACK
↓
Reconcile / Repair
↓
Terminal State
```
每一层回答：
- 谁写？
- 谁读？
- 状态在哪里？
- 唯一键是什么？
- 版本/generation 是什么？
- 谁重试？
- 谁补偿？
- 谁判断完成？
- 谁告警？
## 3. 状态机检查模板
```text
NEW
↓ claim
PROCESSING
├─→ COMPLETED
├─→ RETRY
│    ↓
│  PROCESSING
└─→ FAILED
     ↓
   REPLAY / MANUAL
```
检查：
- claim 条件
- lease owner / token / generation
- lease expiry / steal
- stale worker 写入
- retry limit
- cursor 单调性
- 部分成功表达
- FAILED 是否可重放
- terminal 是否可提前出现
- 根据目标状态契约判断缺失租约、所有权或版本是否非法；无租约执行器、由其他机制保证所有权的任务，不能仅因 PROCESSING + null lease 报缺陷
- crash 后如何恢复
## 4. 事务故障矩阵
按实际依赖选择：
- DB 成功 + Outbox 成功
- DB 成功 + Outbox 失败
- DB 成功 + 缓存/投影失败
- DB 成功 + MQ 失败
- DB 成功 + HTTP 失败
- 外部副作用/所有权变更成功 + DB rollback
- Outbox 已落 + 进程 crash
- commit 前 crash
- commit 后、下游前 crash
目标：不存在不可恢复半提交。
## 5. Lease / stale worker 矩阵
```text
A claim
A 卡住
lease 过期
B steal
B complete
A 恢复后 complete
```
正确结果：A 的过期写入被拒绝，B 的结果不被覆盖。数据库条件更新可以用影响 0 行证明拒绝；其他存储或协议用等效可观察证据。记录拒绝或冲突的可观测性，不能把某个指标名当作所有项目的固定接口。
## 6. MQ / Delivery 矩阵
测试：
- publish fail
- broker confirm timeout
- duplicate consume
- out-of-order
- consumer ACK 后 crash
- callback 前 crash
- 100 receivers: 99 success + 1 fail
- failed receiver subset retry
- duplicate receiver event
- 批次完成记录与单项处理记录不一致
不变量：
- 有 durable delivery intent；
- 部分失败可按失败粒度恢复；
- 去重粒度不得吞掉其他合法对象的处理。
## 7. Snapshot / Cache 脏数据矩阵
构造：
- null / empty
- malformed JSON
- wrong type
- old schema
- 不支持的校验算法（如存在）
- wrong checksum
- 相同汇总计数但内容不同
- same weak checksum / different content
- 索引/key 指向对象 A，但内容属于对象 B
- 版本元数据与实际内容不一致
- 所有权代次缺失或不匹配（如存在）
- 删除标记与读取结果不一致（如存在）
- 已删除对象被重试或旧写入复活
- fence exists / missing / stale
- 元数据存在但对应内容缺失
- 内容存在但必要元数据缺失
期望：
- 精确 invalid reason；
- 按业务一致性契约拒绝、降级或回源，涉及权限/隔离的数据不得因降级放开访问；
- 有真正可达的恢复路径；
- 健康对象不被同批坏对象拖死。
## 8. Reader / Reconcile 一致性检查
建立同一份业务正确性契约的断言矩阵；不要求所有项目实现特定名称或结构的验证器。
对每组脏数据同时运行：
- production Reader
- Reconcile health checker
- Repair decision
必须满足：
- Reader invalid ⇒ Reconcile 不得 healthy；
- Reconcile broken ⇒ 有持久化恢复任务，或明确负责人和人工恢复入口；
- Repair 成功后 Reader 满足业务读取契约。
## 9. Compatibility 矩阵
测试：
- old writer + old reader
- old writer + new reader
- new writer + old reader
- new writer + new reader
- rolling deploy midway
- rollback midway
- 兼容开关的受支持组合（如存在）
- 实际受支持的业务模式（如存在）
- schema/checksum algorithm old/new coexistence
发布顺序若是正确性前提，核查是否有实际门禁或可验证的操作流程；不要假定仅有文档就一定会执行，也不预设必须引入新自动化系统。
## 10. Job / Reconcile 假绿矩阵
覆盖：
- lock conflict → skipped
- empty tasks
- unknown task
- LIMIT 0 / batch-size 0
- partial scan failure
- 缓存/投影读取失败
- one shard failed, others passed
- no work performed
根据目标项目的状态契约区分完成、跳过、无任务、降级和失败。表示业务完成的终态不能仅因“方法正常返回”就成立。
## 11. Recovery 四问
每个故障必须回答：
```text
Failure：怎么坏？
Detection：谁发现？
Repair Owner：谁修？
RTO：多久必须收敛？
```
并补：
- retry policy
- manual repair entry
- alert threshold
- residual cleanup
- replay idempotency
## 12. Finding 模板
```text
编号：
名称：
状态：
Impact：
Likelihood：
建议级别：
Invariant：
Reachable Path：
Root Cause：
Business Consequence：
Source Evidence：
Test/Probe Evidence：
Production Evidence：
是否真实缺陷：
是否需要改代码：
是否与其他问题同根因：
治理包：
永久回归要求：
验收标准：
```
## 13. 二次评审表
| 编号 | 真实性 | Impact | Likelihood | 建议级别 | 处理方式 | 合并治理包 |
|---|---|---|---|---|---|---|
| | 已确认/风险/测试缺口/误报 | | | | 必须改/治理/测试/文档/运维/范围外 | |
## 14. 治理包模板
```text
治理包编号：
名称：
关联问题：
根因：
核心不变量：
当前风险：
修复目标：
禁止方案：
涉及模块：
兼容性要求：
客户端影响：
测试矩阵：
回归范围：
上线 Gate：
回滚方案：
完成条件：
```
## 15. 验收关闭标准
不能因为“代码改了”或“原有测试全绿”关闭。
关闭前按适用项确认：
- 代码修复
- 永久回归
- 关键调用方回归
- 反例/边界
- 并发/竞态
- 故障注入
- 恢复收敛
- 可观测性
- 兼容性
- 回滚
- 文档/契约
## 16. 扫描停止判据
停止继续扩散并转修复：
- 按约定覆盖范围复核后，没有新的高优先级发现；
- 新增项主要为测试/文档/可观测性；
- 治理包已经稳定；
- 继续扫描收益低于修复收益。

优先级沿用目标项目规则。收敛只针对已审范围，未验证环境和证据缺口仍需保留。
## 17. 最终交付格式
```text
【范围】
【真实现象】
【核心不变量】
【已确认问题】
【排除/误报】
【治理包】
【修复顺序】
【测试证据】
【恢复闭环】
【上线 Gate】
【回滚】
【剩余风险】
【结论】
```
