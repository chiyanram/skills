# 73 · Sources moved out of the reference files (agent-factory#59)

On 2026-11-04 the operator decided that a rule file holds only what an agent needs to act; provenance lives in the
ledger (`19-approved-rules.md`) and the research files. The strip removed citations from every reference. Most of them
were already in each rule's ledger row. The ones below were not, so they are kept here, as they stood in the
references on main at `52ae5e8`, with each file's short source names written out in full. A ledger row whose source cell ends "see research/73" points here.

## Planning and meta (spec-review, diagrams, program-design, writing-docs, acceptance-criteria)

- spec-review: SR1 circleci eng-practices §Avoid Ad-Hoc Comments; SR2 humanlayer create_plan.md:69,79, pstack skills/why/references/sources/notion.md:42, mattpocock to-spec/SKILL.md:55; SR4 create_plan:341, github/spec-kit templates/commands/specify.md:164, firstmate captain-hold-lifecycle/SKILL.md:19, addy spec-driven-development:146; SR6 to-spec:35,:67, jvm-skills .claude/skills/spec/SKILL.md:36, spec-kit:165,:170, spec-driven:144, addy interview-me:111, create_plan:331. Pref line: SR1, SR3.
- diagrams: DG2 humanlayer-skills plugins/show-me/skills/show-me/SKILL.md:47,:59,:85 (Good pair from :85), mattpocock improve-codebase-architecture/HTML-REPORT.md:63; DG1 GitHub Docs "Creating diagrams" §About creating diagrams, mattpocock docs/engineering/pr.md:47, pstack skills/how/references/explainer-prompt.md:40; DG6 show-me:126; DG4 show-me:126 + pstack skills/teach/SKILL.md:17; DG5 HTML-REPORT.md:55 + show-me:126. Pref line: DG1, DG2, DG3, DG6.
- program-design: HumanLayer advanced-context-engineering-for-coding-agents/wsff.md:491-501 (PD1; Good pair :493-501), :507-515 (PD2; Good pair), :517 (PD3), :542-551 (PD4); HumanLayer .claude/commands/create_plan.md:226-234,:325 (PD5; Good pair :226-234); pstack skills/architect/SKILL.md:9,:83 (PD3; Good pair), :57 (PD7); mattpocock to-tickets/SKILL.md:31 (PD4), :40 (PD4 edge), to-spec:55 (PD6); addy planning-and-task-breakdown/SKILL.md:93-95 (PD2), :61-77 (PD4; Bad :61-67, Good :69-75), :86-89 (PD5); addy spec-driven-development:214 (PD7), :96 (PD6 counter-source note). Pref line: PD1, PD2, PD3, PD6.
- writing-docs: WD2 kunchenguid-firstmate AGENTS.md:374, mattpocock skills/productivity/writing-for-agents/SKILL.md:79; WD4 mattpocock .agents/writing-docs.md:56, addy documentation-and-adrs/SKILL.md:134; WD7 writing-for-agents:78,:79 (edge), firstmate AGENTS.md:55, openclaw docs/AGENTS.md:38, jabrena-plinth skills/200-agents-md/references/200-agents-md.md:59; WD5 addy spec-driven-development:212-214. Pref line: WD1, WD4, WD5.
- acceptance-criteria: GA1 addyosmani spec-driven-development:143, github/spec-kit templates/spec-template.md §User Scenarios & Testing, humanlayer create_plan.md:225; GA2/CV1 spec-kit §Functional Requirements, OMG issue SYSML16-204 (SysML 1.6 "The unique Id of the requirement"), cucumber.io/docs/gherkin/reference §Comments; GA3 cucumber-ref §Tags, jabrena plinth skills/058-design-bdd/references/058-design-bdd.md:266 (counter-source; Bad pair :266-270); GA4 cucumber-ref §Background, §Scenario Outline, plinth-bdd:149; GA5 cucumber-ref §Steps, plinth-bdd:32, spec-kit §Edge Cases, plinth 131-java-testing-unit-testing.md:25, plinth-bdd:93-99 (edge); GA6 Dan North "Introducing BDD" §agiledox, cucumber.io/docs/bdd/better-gherkin §Declarative; AC7 addyosmani deprecation-and-migration/SKILL.md:179; AC9 mattpocock to-spec:13, North §BDD for analysis; AC10 addy-sdd:214; GA4 pair adapted from plinth-bdd:169-176 (Bad), :154-164 (Good); GA5 pair from plinth-bdd:104-107 (Bad), :93-99 (Good). Pref line: GA2, GA3, GA6, CV1, AC7, AC8, AC9, AC10.

## Migrations and observability

- MIGRATIONS: MG5 cited r47 :863-868 (PG SET "outside of a transaction block ... no effect"; PG explicit locking) — ledger MG5 row names only r47 :160-163 (PG ALTER TABLE, client config; squawk; strong_migrations; GitLab). Review check cited r47 :863.
- OBS levels.md: no ledger row names its sources (it has no rule ids; ledger rows for levels are FL14/FL25/OQ4, none pointing at r47). Its table cited r47 :456-465, :467 (OpenTelemetry exceptions in logs, logs data model, recording errors, HTTP spans; Log4j Level; OWASP Logging and Logging Vocabulary).
- OBS logging: LG6 cited r47 :869-875 (SLF4J manual fluent API "pass arguments with a Supplier"; SLF4J LoggingEventBuilder) — ledger LG6 names r47 :517-519 only. LG3 edge cited r47 :873-875 (SLF4J LoggingEventBuilder setCause) — ledger LG3 names :494-495 only. LG8 edge cited r47 :527 (SLF4J static/instance "left to the user") — ledger LG8 names :524-525. LG4 cited r47 :504 (OpenTelemetry HTTP url.full scrubbed) — ledger LG4 :502-504 ok.
- OBS metrics: MX1 edge cited r47 :634 (Micrometer Observation "High cardinality key values are not included in meters") — ledger MX1 names :548-550 only (the :634 line sits under TR3).
- OBS tracing: TRN1/TR3 cited r47 :634 (OpenTelemetry Trace API "account_id=42 would make a nice Span attribute"; Micrometer Observation) — ledger TRN1 names :639-641, TR3 :630-632, neither :634. TR5 edge cited r47 :664 (OTel SDK sampling as a cost choice) — ledger TR5 names :661-662. Bridge note cited r47 :666-672 (TR4/TR4a notes; ledger TR4 is a project decision row). TR1 thread hand-off cited :614 (Micrometer Tracing "continue a span in a new thread") — ledger TR1 :611-614 ok.

## Testing

- U1: mattpocock `tdd/mocking.md` :7 (unit-tests.md).
- U2: spock-best-practices `SKILL.md` :52, :55, :56, :79, :80 (unit-tests.md); :52 and :55 source U2's reason.
- U3: addyosmani `test-driven-development/SKILL.md` :240-243 ("ladder") (unit-tests.md).
- S3: agent-factory `research/31:19`, the source of S3's reason (strategy.md).
- M1: agent-factory `research/31:23`, the source of M1's reason (mutation.md).
- S4: agent-factory ADR-0007, cited in the S4 decided edge (mutation.md).
- GT6: agent-factory `research/31:22`, the source of GT6's reason (scenario-to-tests.md).
- TM4: agent-factory `research/31:20`, the source of TM4's reason (integration-tests.md).
- K20: agent-factory `research/31:21`, the source of K20's reason (examples/spock.md).
- B1: plinth `130-java-testing-strategies-correct.md` :42, :67, :119, :149, :176, :211 (boundaries.md, CORRECT table).
- C1: plinth `130-java-testing-strategies-right-bicep.md` :79, :102-103, :134, :167-168, :193 (coverage-design.md,
  RIGHT-BICEP table).
- V2, V3, V5: openclaw test-audit :31-33, :33, :71-73, :105-106, :108-109 (value-bar.md).
- K3: Spock `interaction_based_testing.adoc` :788-797 (spock.md).
- U3: mattpocock `tdd/mocking.md` :10-14 (unit-tests.md).
- SP10, SP11: agent-factory-era neutral pair sources `68b` :602, :636 (integration-tests.md).

## Migrations, line pointers

- MG36: r47 :143 (postgres-design.md).
