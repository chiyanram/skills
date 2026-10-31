# Good/Bad example approvals (operator, via Rule Review page)

| reference | source file | rules | decision | date |
|---|---|---|---|---|
| strategy.md | 31a-v2.md | S1–S5, TM1–TM4, AT1 | approve all | 2026-10-02 |
| coverage-design.md | 31a-v2.md | C1–C4 | approve all | 2026-10-02 |
| boundaries.md | 31a-v2.md | B1–B3 | approve all | 2026-10-02 |
| value-bar.md | 31a-v2.md | V1–V5 | approve all | 2026-10-02 |
| unit-tests.md | 31b-v2.md | U1–U4 | approve all | 2026-10-02 |
| integration-tests.md | 31b-v2.md | IT1–IT5, IT4b, SP1–SP11 | approve all | 2026-10-02 |
| spock.md | 31b-v2.md | K1–K20, K2b | approve all | 2026-10-02 |
| mutation.md | 31c-v2.md | M1–M10 | approve all | 2026-10-02 |
| property-based.md | 31c-v2.md | P1–P4, P6–P8, P10 | approve all | 2026-10-02 |
| acceptance-criteria.md | 31c-v2.md | GA1–GA6 | approve all | 2026-10-02 |
| scenario-to-tests.md | 31c-v2.md | GT1–GT6 | approve all | 2026-10-02 |
| smoke-specs.md | 31d-v2.md | EA1–EA6, EB1–EB4, EC1–EC6, ED1–ED5 | approve all | 2026-10-02 |

## Planning (#35) — operator 2026-10-02
Planning Good/Bad (20 rules, research/42, page https://claude.ai/artifact/JaHyxMYJLdg74ZVj4XAEDY): approve all. DG3 rule amended to exempt `+` lines in a design diff.

## Good rewrites (sources rule) — operator 2026-10-04
All 35 rewritten Goods approved (research/47-good-rewrites.md, page https://claude.ai/artifact/5bJrMoSs7Werx9P2mbP2EJ). They replace the old "real" Goods in 31a–31e-v2 and 42 for the same rule ids. NEEDS COMPILE CHECK items are compiled when the references are written (agent-platform #644 / G9 domains).

## LLM testing (#133, G34) — operator 2026-10-31
Fake model Good/Bad (LT1–LT6, research/71-llm-testing-good-bad.md, page https://claude.ai/artifact/Aa3nMykp8FRfU2VzUiWww1): approve all.
Agent loop Good/Bad (LT7–LT11, research/71, same page): approve all. NEEDS COMPILE CHECK when the reference is written (#134): the pairs use stand-in types (`ChatModelPort`, `ScriptedChatModel`, `OrderAssistant`).
Agent scenarios rules + Good/Bad (LS1–LS10, research/71, same page): approve LS1–LS9; LS10 approved as an ours-rule, with its pair. Same compile check at #134.
Recordings rules + Good/Bad (LT12–LT13, research/71, same page): approve all.
Compile check for `testing/references/llm-tests.md` (#134): all 46 Groovy blocks of LT1–LT13 and LS1–LS10 compile to bytecode under Groovy 4.0.22 and Spock 2.3-groovy-4.0, with empty stand-ins for the domain types and the imports the snippets leave out (Spring test annotations, Spock's `SpecInfo`). No syntax or type error. Copied byte for byte into `examples/llm-tests.md`.
Live tests rules + Good/Bad (LS11, LS13, LS15, LS16, LT14, LT15, LT16, LS19, LS20; research/71, same page): approve all. LS12, LS14, LS17, LS18 merged, with no pair of their own.
Evals rules + Good/Bad (LT17–LT18, research/71, same page): approve all. G34 complete: 34 pairs approved.
Compile check for `testing/references/llm-live-tests.md` (#134): all 22 Groovy blocks of LS11, LS13, LS15, LS16, LS19, LS20 and LT14–LT18 compile to bytecode the same way (Groovy 4.0.22, Spock 2.3-groovy-4.0, empty stand-ins). No syntax or type error. Copied byte for byte into `examples/llm-live-tests.md`. TM3's approved pair (`examples/strategy.md`) is unchanged; with TM3 narrowed, its Bad's exact-wording assertion is also an LT15 case.
