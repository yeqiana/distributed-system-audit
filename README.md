# Distributed Systems Audit

[简体中文](README.zh-CN.md) | [English](README.md)

An agent skill for auditing **correctness across component boundaries and recovery after failure**. Trace the real execution path, define invariants, verify reachable failure cases, and turn evidence-backed findings into repair and acceptance plans.

Skill ID and repository name: `distributed-system-audit`.

## When to use it

Use it when a result depends on several components or on retry, ownership, and failure timing:

- A transaction commits but a required downstream effect is missing.
- A superseded worker can still change the result.
- A cache or projection disagrees with the source of truth.
- Messages are duplicated, reordered, partially delivered, or acknowledged too early.
- A recovery job looks healthy while the business reader still returns incorrect data.
- Mixed versions can break recovery during deployment or rollback.

The skill is independent of any particular project, programming language, framework, or infrastructure product. A chain may use queues, caches, Outbox, leases, or none of these; inspect what actually exists. Ordinary single-function reviews usually need a lighter process.

## How it works

| Stage | Result |
| --- | --- |
| Establish evidence | Symptoms or a preventive audit question; facts separated from assumptions |
| Map the actual chain | Entry, writes, handoffs, effects, readers, and recovery ownership |
| Define invariants | Required behavior and legal/illegal state transitions |
| Test interactions | Relevant combinations of state, concurrency, failure, and timing |
| Verify findings | Reachable violation, business consequence, evidence, and counter-evidence |
| Check recovery | Detection, repair owner, replay/compensation, and convergence |
| Review and converge | False positives removed; symptoms grouped by root cause; repair order and acceptance |

A suspected code smell is not a confirmed defect. Severity follows the target project's scale after impact and likelihood are assessed. Unavailable environments, unexecuted probes, and missing production evidence remain explicit gaps.

## Quick start

```text
Use $distributed-system-audit.
Audit the specified business chain for correctness and recovery.
Scope: this repository, read-only. Do not modify files, data, configuration,
services, or infrastructure, and do not inject faults.
Start with current code and the evidence I provide.
Report invariants, reachable paths, consequences, evidence, and recovery owners.
Separate confirmed defects, source-level risks, and test gaps.
Group findings by root cause and propose repair, regression, and acceptance steps.
```

Additional prompts: [audit](prompts/audit.md), [second-pass triage](prompts/triage.md), and [repair handoff](prompts/repair-handoff.md). The [stale-worker example](examples/stale-worker.md) is synthetic, not a production incident or an executed test.

## Install

Copy the complete skill folder into your agent's skills directory. At minimum, keep `SKILL.md`, `agents/`, and `references/` together; the entry point refers to supporting material.

For Codex's default local skill location, the installed layout is:

```text
~/.codex/skills/distributed-system-audit/
  SKILL.md
  agents/openai.yaml
  references/audit-sop.md
```

To install the generated release archive on Windows, run from this repository root:

```powershell
$skillsRoot = Join-Path $env:USERPROFILE '.codex/skills'
$skillDestination = Join-Path $skillsRoot 'distributed-system-audit'
if (Test-Path -LiteralPath $skillDestination) { throw 'Review the existing installation before replacing it.' }
New-Item -ItemType Directory -Path $skillsRoot -Force | Out-Null
Expand-Archive -LiteralPath './dist/distributed-system-audit-v0.1.0-rc1.zip' -DestinationPath $skillsRoot
```

The ZIP has one top-level `distributed-system-audit/` folder. Alternatively, copy this repository folder to the same destination or clone the published repository there once its URL is available. Respect a custom skills location if your installation uses one. For other agents, follow their own discovery convention and verify invocation separately.

## Outputs and boundaries

A single report can contain scope, invariants, evidence, findings, rejected hypotheses, root-cause groups, repair order, regression requirements, recovery acceptance, and unresolved risks. Detailed matrices and templates are in [the SOP](references/audit-sop.md); select relevant sections instead of imposing every matrix on every system.

The default is audit first. Read-only requests permit analysis and probe design, not edits or fault injection. Authorized local probes must be isolated and cleaned up without touching pre-existing work. Repairs, shared/live mutations, and deployment stay within the user's actual authorization.

The skill supplies instructions, not a scanner or infrastructure. It neither guarantees that all defects will be found nor treats a code change or green unit tests as proof of recovery.

## Validate and package

Only repository maintenance needs Python 3.10+ and the development dependency. Using the skill instructions does not require a Python runtime.

```text
python -m pip install -r requirements-dev.txt
python scripts/test_skill.py
python -m unittest discover -s tests -v
python scripts/test_skill.py --package dist/distributed-system-audit-v0.1.0-rc1.zip
```

PowerShell entry point:

```powershell
pwsh -NoProfile -File scripts/test-skill.ps1
```

Packaging refuses to overwrite an existing archive; choose another output filename for a later build. Outputs inside the repository must be under `dist/`; an external output location is also supported. Source directories such as `docs/` are rejected before writing. Static checks validate YAML, metadata, supporting resources, and local links. Regression tests exercise rejected packages, install integrity, and reproducible synthetic observations. The CI configuration targets Windows and Linux; successful local checks do not establish remote CI results.

**Static package validation does not prove agent behavior.** Use [the behavior contracts](evals/behavior-contracts.md) and [evaluation procedure](evals/manual-evaluation.md), and record actual results for each model/host combination. See [the release checklist](docs/release-checklist.md) before publishing.

Prepare 11 fixed blind evaluation inputs in an external temporary directory:

```text
python scripts/prepare_behavior_eval.py
```

Each case contains the skill, a request, raw synthetic artifacts, and an isolated workspace. The evaluator does not receive the scoring rubric. Synthetic execution is checked separately from agent behavior; neither is production evidence.

The [recorded local evaluation](evals/results/2026-10-19/README.md) passed 11/11 cases. It includes full responses, commands, input hashes, grading, and limits. The exact inherited model version was unavailable; this is a result for that recorded run, not a claim about every model or host. The [strengthening review](docs/strengthening-review.md) describes the fixes and remaining release checks.

## Repository guide

| Path | Contents |
| --- | --- |
| [SKILL.md](SKILL.md) | Agent entry point, evidence rules, and workflow |
| [agents/openai.yaml](agents/openai.yaml) | UI metadata and invocation policy |
| [references/audit-sop.md](references/audit-sop.md) | Optional matrices and report templates |
| [prompts](prompts/audit.md) | Copy-ready task prompts |
| [examples](examples/stale-worker.md) | Synthetic audit example |
| [evals](evals/manual-evaluation.md) | Behavioral acceptance criteria and result recording |
| [docs/release-checklist.md](docs/release-checklist.md) | Publication checks |
| [docs/promotion-copy.md](docs/promotion-copy.md) | Introduction copy |

## License

[MIT](LICENSE).
