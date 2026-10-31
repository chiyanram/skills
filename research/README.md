# research: the evidence behind each rule

Every rule in the plugin can be traced back to a file here. Nothing in this folder ships. It is the record of what
was looked at, what was decided and why.

## Start here

| file | read it for |
|---|---|
| [19-approved-rules.md](19-approved-rules.md) | **the ledger**: every approved rule, with its target reference, reason, source and evidence |
| [00-decision-register.md](00-decision-register.md) | every decision that is not a rule, and the repo and file it lands in |
| [00-reference-format.md](00-reference-format.md) | the template every reference follows |
| [00-operator-inputs.md](00-operator-inputs.md) | every link and idea the operator shared, and where it landed |
| [69-llm-testing-in-agent-sdks.md](69-llm-testing-in-agent-sdks.md) | how 10 agent SDKs and Spring repos test LLM features: fakes, recordings, real-model tests, evals; candidates LT1–LT18 (R40, #131) |
| [70-agent-scenario-tests.md](70-agent-scenario-tests.md) | how to test each agent scenario at each tier (unit, IT, smoke, live), what the references live-test and why, Aruvii's proposed tests; candidates LS1–LS20 (R41, #153) |
| [71-llm-testing-good-bad.md](71-llm-testing-good-bad.md) | neutral Good/Bad pairs for the LLM-testing rules (LT1–LT11, LS1–LS10), each beside the reference project's own test code (G34, #133) |
| [64-core-design.md](64-core-design.md) | the core design from first principles, with the *why* of each reference repo in `64a`–`64e` |
| [repos/INDEX.md](repos/INDEX.md) | one deep report per reference repo: mattpocock, pstack, superpowers, addyosmani, openclaw and others |

## How files are named

- **`NN-topic.md`**: one research topic. The number gives the order the files were written in. It is not the ticket
  ID: `08-standards-inventory.md` is ticket R7. The ticket ID is in each file's title.
- **`00-*.md`**: registers that span every topic.
- **`NNa`, `NNb`, …**: parts of one topic, split by area (for example `68a`–`68f`, neutral pairs per domain).
- **`*-BRIEF.md`**: the brief handed to a research subagent. Its results come right after it: `31` → `31a`–`31e`,
  `55` → `56a`–`56c`, `60` → `60a`–`60c`.
- **`*-v2.md`**: a second round of the same file (`31a-v2.md` replaces `31a`). The highest version wins.
- **`repos/`**: per-repo reports, with `_BRIEF.md` as their shared brief.

## Citations

Research cites reference repos as `path:line @commit`. The pinned commits, and how drifted citations are marked, are
in [../refs/README.md](../refs/README.md). Evidence from a real project is cited as `path:lines @sha` from that
project.
