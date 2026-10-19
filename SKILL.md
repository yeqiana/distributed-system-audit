---
name: distributed-system-audit
description: Audit cross-component correctness and recovery in distributed systems. Use for transactions, asynchronous workflows, caches, messaging, ownership races, or incidents where isolated tests cannot establish end-to-end correctness. Trace reachable paths, define invariants, verify failure timing, and group evidence-backed findings into repair and acceptance plans. Not needed for ordinary single-function reviews.
---

# Distributed Systems Audit

## Purpose and scope

Start from an observed symptom or an explicitly scoped correctness question. Determine what must remain true across component boundaries, what can violate it, and how the system detects and recovers from that violation.

Audit first; implement repairs only when requested. Adapt the workflow to the actual architecture and available evidence. Do not impose a particular language, framework, database, queue, cache, state name, or deployment model.

Use [references/audit-sop.md](references/audit-sop.md) for detailed matrices and reusable report templates; read the sections relevant to the target chain.

## Execution boundaries

- A read-only audit must not edit files, mutate data/configuration, restart services, or inject faults. Propose probes with expected evidence instead.
- If local probes are permitted, isolate them from shared/live systems and preserve existing dirty work. Live mutations and fault injection require authorization for the concrete action. Existing authorization remains valid within its scope.
- Clean up only artifacts created by this audit. Preserve pre-existing probes and tests; keep temporary audit probes out of commits unless deliberately converted into permanent regressions.
- Expand scope only when the same invariant or root cause crosses the stated boundary. If delegation is available and permitted, use independent read-only domains and consolidate conclusions before accepting findings; serialize conflicting edits.

## Audit workflow

1. **Establish evidence.** Capture symptoms, affected objects, timing, and available logs/metrics/traces. For preventive audits, state the correctness question. Separate observed facts, source inference, and unknowns.
2. **Map the actual chain.** Follow entry points, durable writes, asynchronous handoffs, external effects, readers, acknowledgments, and recovery paths that exist. Record ownership, identifiers, versions, retry responsibility, and completion criteria at each boundary.
3. **Define invariants and state transitions.** Explain what must remain true across commit, retry, partial success, ownership transfer, process failure, and recovery. Include illegal transitions and terminal-state meaning.
4. **Build cross cases.** Combine relevant state, concurrency, failure, and timing dimensions. Prioritize reachable business consequences over exhaustive permutations.
5. **Verify suspected defects.** Seek evidence of the current behavior and a reachable contract violation. Use the smallest deterministic probe when permitted and useful; otherwise give its design and mark the result unverified.
6. **Check recovery.** For each failure, identify detection, durable recovery intent, repair owner, retry/compensation behavior, convergence conditions, and the applicable recovery-time target. Mark unknown targets explicitly.
7. **Review and converge.** Check counter-evidence, remove false positives, distinguish defects from test/docs/observability gaps, and group symptoms by root cause. Produce repair, regression, and acceptance plans within the requested scope.

## Evidence and finding acceptance

A code smell is not a defect. Before accepting a finding, answer:

- Which invariant is violated, and where is it defined or inferred?
- Is the path reachable under stated preconditions?
- What business consequence follows?
- Which production observation, deterministic reproduction, regression result, or source path supports current behavior? Record environment, revision, and limitations; do not treat stale observations as current proof.
- What counter-evidence or existing safeguard might invalidate the claim?
- Is this a separate root cause, and does it require code, tests, documentation, configuration, or operational recovery?

Rate impact and likelihood separately, then use the target project's severity scale. When no scale exists, report impact, likelihood, and provisional repair priority; do not invent universal P0/P1 mappings.

Validate states against the target contract before calling them illegal. For example, a processing task with no lease is not a defect when the system deliberately uses a different ownership or idempotency mechanism.

For a temporary probe, record the invariant, setup, correct expectation, actual result, command, and conclusion. A planned or unexecuted probe is not reproduction evidence. Capture evidence before cleanup and retain the permanent regression requirement.

## Invariants to consider

Apply only those relevant to the actual system:

| Boundary | Correctness question |
| --- | --- |
| Transaction / handoff | Does a committed fact have durable, recoverable intent for every required downstream effect? |
| Ownership / lease / fence | Can a superseded worker still produce an unauthorized effect or overwrite the current result? |
| Cache / projection / snapshot | Do identity, contents, and version metadata describe a consistent logical revision? |
| Messaging / acknowledgment | Are duplicate, missing, reordered, or partially completed deliveries handled under the stated delivery contract? |
| Terminal state | Does completion represent the required business outcome, rather than a returned method or finished loop? |
| Detection / repair | Does health reflect reader correctness, and does each detected failure have a reachable recovery owner? |
| Compatibility | Can supported versions coexist, recover, and roll back under explicit deployment assumptions? |

Check the concrete guarantees of batching, pipelines, locks, and transactions. A batch is not automatically atomic; a caught exception does not necessarily roll back. Distinguish malformed business data from infrastructure failure, and verify how both affect retries and terminal states.

## Test selection

Choose applicable dimensions: boundaries/pagination/deadlines; state transitions; duplicate requests/idempotency; ownership races; partial dependency failure/process crash; ordering; malformed or legacy data; consistency across stores/readers; recovery/replay; version coexistence/rollback; and false-green observability.

Combine them where failure depends on interaction, for example `state × concurrency`, `failure × timing`, `idempotency × reordering`, and `compatibility × recovery`. Record meaningful omissions and unavailable environments. Do not execute every matrix or mutate live systems merely because a dimension is listed.

## Convergence and handoff

Stop expanding when agreed coverage is reached, findings stabilize into actionable root-cause groups, or additional scanning yields mainly low-value documentation issues. Repeated passes without new high-priority findings support convergence only within the inspected scope; they do not prove zero risk.

Prefer one concise report containing scope, evidence, invariants, confirmed findings, unresolved risks, counter-evidence/false positives, root-cause groups, repair order, test requirements, and recovery/rollout/rollback acceptance where applicable. Use the project's issue and report conventions; do not require a new process or fixed set of documents.

End with an Executive Summary covering the goal, changed files (or none), verification evidence, material risks, required acceptance, and conclusion.

A code change alone does not close a finding. Closure requires applicable permanent regressions, affected-caller checks, fault/recovery evidence, compatibility/rollback verification, and contract or observability updates. Mark unexecuted acceptance explicitly.
