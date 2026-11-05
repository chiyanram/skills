# R37 · Checkstyle ruleset that gates our approved rules + smell catalogues beyond rameezk (#84 → #33 G9b, SP22)

Question (#84): (1) which Checkstyle modules, with which limits, make the mechanical part of our approved rules fail
the build (OQ3)? (2) which smell / review catalogues should sit next to rameezk's 12-smell baseline?

Nothing here enters `checkstyle.xml` or a reference without the operator's yes. Candidates are in §5 and `review/r37.json`.

**Legend.** `SF` = spring-projects/spring-framework `src/checkstyle/checkstyle.xml` (★60k, Apache-2.0; last change
b6fc3a1b6, 2026-04-02) · `SF-C` = SF `CONTRIBUTING.md` @c377da58d · `SB` = spring-projects/spring-boot
`config/checkstyle/checkstyle.xml` (★81k; 22eef9729, 2026-06-30) · `SJF` = spring-io/spring-javaformat
`…/spring-checkstyle.xml` (the `SpringChecks` set Boot loads, ★956; 4d3417e42, 2026-08-10) · `GG` = checkstyle/checkstyle
`src/main/resources/google_checks.xml` (ebb799824, 2026-09-23) · `SUN` = same repo `sun_checks.xml` (84c81eab0,
2026-09-22) · `CSS` = same repo `config/checkstyle-checks.xml`, Checkstyle's self-check (★9.6k, LGPL-2.1; 6e39d3ef4,
2026-09-24) · `KF` = apache/kafka `checkstyle/checkstyle.xml` (★34k, Apache-2.0; 11ad60b45, 2026-03-02) · `CS/<m>` =
https://checkstyle.org/checks/…/<m>.html §Description/§Properties (fetched 2026-10-04) · `AP` = agent-platform
`origin/master`@772736bf (evidence only, SRC1) · `…/` in AP paths = `src/main/java/ai/aruvii/` · ledger =
`research/19-approved-rules.md`.

**How hits were counted.** `git archive origin/master` into a scratch dir; Checkstyle **14.0.0** CLI
(`checkstyle-14.0.0-all.jar`, sha256 f3845df2…, the version AP pins in `gradle/libs.versions.toml:34`) run with the
config in §3 over all 1020 `src/main/java` files and 299 test files. Counts are **measured**, not estimated.
Metric distributions came from a second probe run with every limit at 0/1. AP itself was not touched.

---

## 1. The sources — why each is strong, how it is built

### 1a. Checkstyle configs

| Source | Why it carries weight | How it is built | What it teaches us |
|---|---|---|---|
| SF (287 lines) | What Spring's committers are *gated* on; SF-C:229 "Many of these rules are enforced at build time by Checkstyle" | Flat list of FQ module names; library concerns (Javadoc, `@since`, header) next to code-shape gates; regex bans | Nesting gates, not complexity: `NestedForDepth` 3, `NestedIfDepth` 5, `NestedTryDepth` 3 (SF:70-78). `NeedBraces` (SF:40). Console/printStackTrace bans (SF:226-239). **No `LineLength` module**, yet SF-C:363 "No lines should exceed 120 characters" |
| SB (106 lines) + SJF (167 lines) | Boot = an application-shaped codebase; it loads SJF's `SpringChecks` (SB:9-13) then adds bans | SJF holds the shared Spring set; SB adds `IllegalImport` lists, `ImportControl`, test-style regexes | `mainCodeIllegalImportCheck` bans `jakarta.annotation.PostConstruct` (SB:27-35) → X6/SP23. SJF tightens `NestedIfDepth` to **3** (SJF:60-62) |
| GG (500 lines) | The reference implementation of Google Java Style, maintained by Checkstyle's own team (GG:6-16) | Style-first: whitespace, wrapping, naming, Javadoc; very few size/complexity gates | `NeedBraces` on do/else/for/if/while (GG:113-116) = GJS 4.1.1 → JV9. `LineLength` 100 (GG:58-60). `EmptyCatchBlock` allowing a comment (GG:467-469). `MissingSwitchDefault` (GG:192) |
| SUN (220 lines) | Checkstyle's "all the classics" config (SUN:6-19) | Every family once, mostly defaults | Defaults for size gates: `FileLength` 2000, `MethodLength` 150, `ParameterNumber` 7 (SUN:73,141-142; defaults per CS/filelength, CS/methodlength, CS/parameternumber). Also `FinalParameters`, `MagicNumber`, `HiddenField`, `DesignForExtension` (SUN:184-206) — the noisy set nobody else keeps |
| CSS (1099 lines) | Checkstyle checking itself — nearly every module on, with tuned limits | Everything on, then `SuppressionXpathSingleFilter` carve-outs | Strictest published numbers: `NestedIfDepth` 3, `NestedForDepth` 2 (CSS:577-582), `FinalLocalVariable` (CSS:446), `ReturnCount` 1 (CSS:604-607), `CyclomaticComplexity` default 10 with `switchBlockAsSingleDecisionPoint` (CSS:849-851) |
| KF (164 lines) | Large Apache application-ish codebase that *does* gate metrics | Hygiene + metrics block with loose, measured limits and suppressions file (KF:158-160) | Only high-star config found with the metric block: `CyclomaticComplexity` 16, `NPathComplexity` 500, `JavaNCSS` 100, `MethodLength` 170, `ParameterNumber` 13, `BooleanExpressionComplexity` 5 (KF:117-149); `FinalLocalVariable` on locals **and** parameters (KF:75-78). Limits were set high to fit existing code, then suppressed |

What the module docs say the metrics are for (opened each):

- `CyclomaticComplexity` (CS/cyclomaticcomplexity): "the minimum number of possible paths … the number of required
  tests, it is not about quality of code"; "1-4 easy to test, 5-7 OK, 8-10 consider re-factoring"; default 10;
  `switchBlockAsSingleDecisionPoint` exists to stop each `case` counting.
- `NestedIfDepth` (CS/nestedifdepth): default `max` 1; depth counts from 0, so `if{if{if{}}}` is depth 2.
- `FinalLocalVariable` (CS/finallocalvariable): locals by default; parameters only via `tokens`; for-each var via
  `validateEnhancedForLoopVariable`.
- `MissingSwitchDefault` (CS/missingswitchdefault): skips switch *expressions* and pattern switches, still flags an
  enum switch *statement* without `default` — S-4 wants no `default`.
- `IllegalImport` (CS/illegalimport) checks imports only — a fully-qualified `@org.springframework…Autowired` passes it.
- Martin Fowler on method size (`MF/CodeSmell`, 2006): "my nose twitches if I see more than a dozen lines of java" —
  a smell, "some long methods are just fine".

### 1b. Smell / review catalogues

| Source | Why strong | How built | Licence |
|---|---|---|---|
| **Fowler & Beck, _Refactoring_ 2e ch. 3** — publisher excerpt, InformIT "When to Start Refactoring Code—and When to Stop", 2018-11-19, https://www.informit.com/articles/article.aspx?p=2952392 (24 pages, `&seqNum=N`) | The origin of the smell vocabulary; the excerpt is Pearson's own | 24 smells, one page each: what it is → which refactorings (by page) cure it | © Pearson — cite names + link, never copy text |
| refactoring.com/catalog (Fowler) | Canonical names of the 2e *refactorings* (the cures) | Cards with aliases and tags (encapsulation, moving-features, …) | © Fowler; link only. **No smell list on the site** — the smells live only in the book |
| martinfowler.com/bliki (`CodeSmell`, `FunctionLength`, `DataClass` …) | Fowler's own short essays; R36 used them | Free essays | © Fowler; link |
| **Kerievsky, _Refactoring to Patterns_** — Industrial Logic "Smells to Refactorings Cheatsheet", J. Kerievsky, 2005-05-03, https://www.industriallogic.com/blog/smells-to-refactorings-cheatsheet/ (PDF `/img/blog/2005/09/smellstorefactorings.pdf`; the copy read is the 3-page adaptation that cites it, identical table) | Adds 5 smells Fowler lacks, each mapped to a pattern refactoring with page refs | Table: smell · one-line description [F/K page] · refactorings | © Industrial Logic; teaching aid, link |
| refactoring.guru/refactoring/smells | Most-read free smell site; grouped for teaching | 23 smells in 5 groups (Bloaters, OO Abusers, Change Preventers, Dispensables, Couplers) using **1st-edition** names (Switch Statements, Lazy Class, Inappropriate Intimacy) + Dead Code, Parallel Inheritance Hierarchies, Incomplete Library Class | Proprietary (site terms: no open licence) — link only |
| SonarSource Java rules (sonar-java @de5daac62, `sonar-java-plugin/…/rules/java/S*.json`) | Largest Java rule set with a "code smell" type and default thresholds | 770 rules: **507 CODE_SMELL**, 200 BUG, 63 VULNERABILITY | SONAR Source-Available Licence v1.0 (LICENSE.txt:1) — read, don't vendor |
| PMD Java rules (https://docs.pmd-code.org/latest/pmd_rules_java.html; ★5.5k) | Metric-based design-flaw rules (GodClass, DataClass, LawOfDemeter, CognitiveComplexity) Checkstyle lacks | 325 rules: Best Practices 71, Code Style 64, **Design 45**, Documentation 6, Error Prone 100, Multithreading 12, Performance 25, Security 2 | BSD-style (docs §License) |
| Error Prone (https://errorprone.info/bugpatterns; ★7.2k) | Compiler-plugin bug patterns; type-aware where Checkstyle is syntax-only | 651 patterns: on-by-default ERROR 187 / WARNING 312; experimental 152 | Apache-2.0 |
| mattpocock/skills `code-review/SKILL.md` (★275k, MIT; read at plugin 1.2.3) | The upstream of the rameezk list | `:38-56` the same 12 smells **in the same order** as rameezk; `:41` "skip anything tooling already enforces" | MIT |
| rameezk/skills `skills/code-review/martin-fowler-code-smells.md` (★0, MIT; file last changed f5586d7eb, 2026-09-17) | Our current baseline (SEAM1, ADR-0017) | 12 smells, one line each (`:10-21`); `:6` "skip anything tooling already enforces" | MIT |
| sanyuan0704/sanyuan-skills `code-review-expert/references/solid-checklist.md` (★3.9k, MIT, last commit 08b6572ef 2026-05-11) | Highest-star code-review skill found by `gh search repos "code review skill"` | `:41-53` 9 smells; "Long method: Function > 30 lines" — no source cited | MIT |
| awesome-skills/code-review-skill (★2.0k, MIT, 4850184df 2026-09-08) | 2nd-highest | `reference/java.md` (409 lines, Chinese): Java 17/21 features, Spring, JPA — **no smell catalogue** | MIT |

---

## 2. Proposed `checkstyle.xml` — module · limit · rule · hits on master

**Scope finding first.** Checkstyle only runs where `aruvii.spring-conventions` is applied
(`build-logic/…/aruvii.spring-conventions.gradle.kts:4` → `aruvii.checkstyle-conventions`).
`aruvii.java-conventions` does not apply it, so **`aruvii-shared` (162 main files) and `aruvii-test-support`
(22 files) are not checked at all today** (their build files: `id("aruvii.test-conventions")`,
`id("aruvii.integration-test-conventions")`). That is why one `UnusedImports` hit survives on master
(`aruvii-test-support/…/testsupport/arch/AruviiTestCodeRulesBase.java:3`) although the module is "on".

Columns: **gated** = main code in modules Checkstyle runs on today · **+ungated** = `aruvii-shared` +
`aruvii-test-support` main code (D3) · **test** = all test source sets (for modules proposed for the test config too).

| Module · limit | Enforces | gated | +ungated | test | Recommendation |
|---|---|---:|---:|---:|---|
| `CyclomaticComplexity` max **5**, `switchBlockAsSingleDecisionPoint` true | **SP22** / ADR-0017 S-6 | **204** (114 files) | 11 | 9 | error + baseline (D1, D2) |
| `NestedIfDepth` max **1** (3 levels fail) | **SP22** / DS9 | 2 | 0 | 0 | error now — fix `ApiKeyAuthFilter.java:37`, `OpenApiSpecImporter.java:301` |
| `NestedForDepth` max 1 · `NestedTryDepth` max 1 | DS9 | 0 · 0 | 0 | 0 | error now |
| `NeedBraces` (default tokens) | **JV9** | **666** (178 files) | 39 | 88 | error + baseline (D4) |
| `FinalLocalVariable`, `validateEnhancedForLoopVariable` true | **OQ2** / TY4 | **2612** (254 files) | 33 | 3397 (ST1) | error + baseline — TY4 forbids editing old lines only to add `final`, so a sweep is not allowed |
| `IllegalImport` `jakarta/javax.annotation.PostConstruct` + regex for FQ use | **X6 / SP23** | 5 | 0 | — | error + baseline the 5 until agent-platform #663 (the @PostConstruct/@Autowired rewrite) lands |
| `IllegalImport` `…annotation.Autowired` + `RegexpSinglelineJava` `@org.springframework…Autowired` | **SC1** | 8 import + **2 FQ** | 1 (test-support, allowed by SC1) | 81 (allowed) | error + baseline until #663; main config only. The 2 FQ uses (`ToolService.java:153`, `ChatOrchestrator.java:128`) pass `IllegalImport` — the regex is required |
| `UnusedImports` | existing | 0 | 1 | — | keep (catches the ungated hit once D3 lands) |
| `LineLength` max **120** | **new CK1** (SF-C:363) | **186** (71 files) | 83 | 258 | error + file baseline (D5). Master's own header says "LineLength — enforced by IDE config" (`checkstyle.xml:20`); 269 lines say it is not |
| `FileLength` max 1000 | **DS2** | 1 (`ChatOrchestrator.java`, 1405) | 0 | 3 | error + one suppression with DS2's stated reason, or the split |
| `ParameterNumber` max 7, `CTOR_DEF` | **FW1** (pending) | 41 | 11 | — | error + baseline *if* FW1 is approved (R36 D1 = 7) |
| `ParameterNumber` max 7, `METHOD_DEF`, `ignoreOverriddenMethods` | **new CK4** (Fowler Long Parameter List; Sonar S107 default 7) | 12 | 2 | 7 | error + baseline |
| `EmptyCatchBlock` `commentFormat="(?!)"` (no comment excuses it) | **ER3 / ER8** | 27 | 2 | 18 | error + baseline (D8). With the default (a comment excuses it): 8 |
| `IllegalCatch` `Throwable, Error` | **ER4** ("never `Throwable`") | 0 | 0 | 4 | error now (main). `catch (Exception)` stays review — ER4 allows it at a commented boundary; would be 300 hits |
| `IllegalType` `Optional` on `PARAMETER_DEF, RECORD_COMPONENT_DEF`, and fields (`VARIABLE_DEF` + `memberModifiers`) | **JV6** | 2 + 0 fields | 1 | 2 | error now — fix 3 |
| `RegexpSinglelineJava` `.parallelStream()` / `.parallel()` | **JV2** | 0 | 0 | — | error now |
| `RegexpSinglelineJava` `System.(out\|err).print`, `.printStackTrace()` | **SP19** (R36) | 6 + 0 | 0 | 3 | error now: suppress `LicenseGenerator.java` (CLI `main`), fix `HashEmbeddingAdapter.java:35` |
| `HideUtilityClassConstructor` `ignoreAnnotatedBy=SpringBootApplication` · `FinalClass` | **SP18** (R36) | 1 · 1 | 0 | 3 | error now (fix `LicenseGenerator`, `JwtAuthentication.java:18`) |
| `RegexpSinglelineJava` `log.x("…" +` | **LG6** (single-line form only) | 1 (`ToolsAutoConfiguration.java:239`) | 0 | — | error now; multi-line concatenation stays review |
| `UnusedLocalVariable` | **new CK5** | 60 | 4 | 3 | error + baseline; most are `ignored` names that Java 22+ writes as `_` |
| `BooleanExpressionComplexity` max 3 (default) | **new CK3** | 10 | 0 | — | error + baseline |
| `EqualsHashCode`, `CovariantEquals`, `StringLiteralEquality`, `SimplifyBooleanExpression`, `SimplifyBooleanReturn`, `EmptyStatement`, `InnerAssignment`, `AvoidNestedBlocks`, `MutableException` | **new CK2** (SF:41,50,64-69; SJF:39,45,50-56) | 0 | 0 | — | error now — free |
| `OneStatementPerLine` · `MultipleVariableDeclarations` | **new CK2** (SF:79,92; GG:184,187) | 43 · 1 | 3 | 7 · 1 | error + baseline |

Metric distributions behind the limits (all 1020 main files, probe run):

| Module | >5 | >7 | >10 | >15 | >20 | worst |
|---|---:|---:|---:|---:|---:|---|
| `CyclomaticComplexity` (switch = 1) | 215 | 99 | 44 | 13 | 7 | `HttpToolHandler.java:231` = 53 |
| `CyclomaticComplexity` (each case counts) | 261 | 124 | 53 | 15 | 7 | same = 62 |
| `ParameterNumber` ctor | 74 | 52 | 35 | 16 | — | `ChatOrchestrator.java:133` = 32 |
| `NestedIfDepth` (depth ≥1 / ≥2 / ≥3) | 92 / **2** / 0 | | | | | |
| `MethodLength` non-blank (>30/>50/>80/>150) | 107 / 25 / 8 / 3 | | | | | `ChatOrchestrator.java:316` = 340 |
| `NPathComplexity` (>20/>50/>200/>500) | 165 / 88 / 45 / 29 | | | | | |
| `BooleanExpressionComplexity` (>3/>4/>5) | 10 / 4 / 3 | | | | | `BertTokenizer.java:127` = 14 |
| `LineLength` (>100/>120/>140) | 2278 / 269 / 107 | | | | | `ErrorCode.java:53` = 280 |

**The 3 noisiest gates:** `FinalLocalVariable` 2612 (+33) · `NeedBraces` 666 (+39) · `LineLength` 186 (+83);
then `CyclomaticComplexity` 204 (+11).

**Not proposed, on purpose:**

| Module | In | Why not |
|---|---|---|
| `MissingSwitchDefault` | GG:192, SUN:188 | Flags an exhaustive enum switch statement without `default` (CS/missingswitchdefault) — S-4 forbids that `default`. 6 hits on master. Prefer switch expressions / Error Prone `MissingCasesInEnumSwitch` |
| `ReturnCount` | CSS:604 (max 1) | Fights DS9 guard clauses / early returns |
| `FinalParameters` | SUN:206 | OQ2: "FinalParameters stays off" |
| `IllegalCatch` on `Exception` | CS default | ER4 allows `catch (Exception)` at a must-not-fail boundary with a comment |
| `MagicNumber`, Javadoc set, `HiddenField`, `DesignForExtension` | SUN | Master's header already rejects MagicNumber/Javadoc with reasons (`checkstyle.xml:15-18`) |
| `MethodLength`, `JavaNCSS`, `NPathComplexity`, `ClassFanOutComplexity` | KF, CSS | Later: FW5 says extract by intent, not length; Fowler `MF/CodeSmell` "some long methods are just fine". Revisit after SP22's baseline shrinks |
| `SpringMethodVisibilityCheck` (SP14) | SJF:163 | Needs the spring-javaformat-checkstyle jar on the checkstyle classpath; 0 hits per R36 — later |
| `IllegalImport` `org.slf4j.LoggerFactory` | SF:110-114, SB:25 | Spring uses commons-logging; LG8 *requires* SLF4J `LoggerFactory` |

**Grandfathering (D1).** Checkstyle has no "new code only" mode. Its CLI `-g` writes one `<suppress-xpath>` per
current violation (`checkstyle --help`: "-g … Generates an output xpath suppression XML … to suppress all violations");
tested: 3803 entries suppress every AST-check hit, leaving 196 (LineLength, FileLength, regex checks), which need the
file-level `SuppressionFilter` (`-G`). Gradle exposes `config/checkstyle/` as `${config_loc}` (Gradle user guide,
Checkstyle plugin, Table 2), so both files sit beside `checkstyle-tests.xml`. A `severity=warning` + `maxWarnings`
ratchet (Gradle `CheckstyleExtension.maxWarnings`, default `Integer.MAX_VALUE`) is the alternative: one number per
task, so a new violation can hide behind a fixed old one.

---

## 3. Proposed config XML (validated: parses and runs on Checkstyle 14.0.0 over AP master)

Main source sets (`checkstyle.xml`). The test config (`config/checkstyle/checkstyle-tests.xml`) adds only
`NeedBraces` (JV9), `FinalLocalVariable` (ST1), `UnusedLocalVariable`, `EmptyCatchBlock` and `LineLength`, keeps its
two naming exceptions, and leaves out SC1/SP23/SP19/complexity.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE module PUBLIC
    "-//Checkstyle//DTD Checkstyle Configuration 1.3//EN"
    "https://checkstyle.org/dtds/configuration_1_3.dtd">
<!--
  Aruvii Checkstyle — main source sets. Proposed by research/59 (R37, skills#84).
  Every module names the approved rule it gates (research/19) or its CK candidate id.
  Grandfathered violations live in checkstyle-baseline.xml (generated with `checkstyle -g`) and
  checkstyle-suppressions.xml; a new violation fails the build.
-->
<module name="Checker">
  <property name="severity" value="error"/>
  <property name="fileExtensions" value="java"/>

  <module name="BeforeExecutionExclusionFileFilter">
    <property name="fileNamePattern" value="module-info\.java$"/>
  </module>
  <!-- Reasoned, permanent exceptions (DS2 stated reason, SP19 CLI main) and the file-level
       baseline for LineLength/FileLength, which are not TreeWalker checks. -->
  <module name="SuppressionFilter">
    <property name="file" value="${config_loc}/checkstyle-suppressions.xml"/>
    <property name="optional" value="true"/>
  </module>

  <!-- DS2: a file over 1000 lines -->
  <module name="FileLength">
    <property name="id" value="DS2-FileLength"/>
    <property name="max" value="1000"/>
  </module>
  <!-- CK1: line length 120 (package/import lines ignored by default) -->
  <module name="LineLength">
    <property name="id" value="CK1-LineLength"/>
    <property name="max" value="120"/>
  </module>

  <module name="TreeWalker">

    <!-- Baseline (D1): one suppress-xpath per grandfathered violation, generated by `checkstyle -g`.
         Delete an entry when that code is fixed; a new violation fails the build. -->
    <module name="SuppressionXpathFilter">
      <property name="file" value="${config_loc}/checkstyle-baseline.xml"/>
      <property name="optional" value="true"/>
    </module>

    <!-- ── Imports (existing) ───────────────────────────────────────── -->
    <module name="AvoidStarImport">
      <property name="excludes" value="jakarta.persistence,org.springframework.web.bind.annotation"/>
      <property name="allowStaticMemberImports" value="true"/>
    </module>
    <module name="RedundantImport"/>
    <module name="UnusedImports"/>

    <!-- SC1: no @Autowired in production code (import and fully-qualified use) -->
    <module name="IllegalImport">
      <property name="id" value="SC1-AutowiredImport"/>
      <property name="illegalClasses" value="org.springframework.beans.factory.annotation.Autowired"/>
    </module>
    <module name="RegexpSinglelineJava">
      <property name="id" value="SC1-AutowiredQualified"/>
      <property name="format" value="@org\.springframework\.beans\.factory\.annotation\.Autowired\b"/>
      <property name="ignoreComments" value="true"/>
      <property name="message" value="SC1: no @Autowired in production code; take dependencies through the one constructor (LY6)."/>
    </module>
    <!-- X6/SP23: no @PostConstruct in main code (Spring Boot checkstyle.xml:27-35) -->
    <module name="IllegalImport">
      <property name="id" value="SP23-PostConstruct"/>
      <property name="illegalClasses" value="jakarta.annotation.PostConstruct, javax.annotation.PostConstruct"/>
    </module>
    <module name="RegexpSinglelineJava">
      <property name="id" value="SP23-PostConstructQualified"/>
      <property name="format" value="@(jakarta|javax)\.annotation\.PostConstruct\b"/>
      <property name="ignoreComments" value="true"/>
      <property name="message" value="SP23: no @PostConstruct; checks go in the constructor, start-up work in ApplicationRunner/SmartLifecycle (SC19, SC20)."/>
    </module>

    <!-- ── Naming (existing) ────────────────────────────────────────── -->
    <module name="TypeName"/>
    <module name="MethodName"/>
    <module name="MemberName"/>
    <module name="LocalVariableName"/>
    <module name="ParameterName"/>
    <module name="StaticVariableName"/>
    <module name="ConstantName">
      <property name="format" value="^log(ger)?$|^[A-Z][A-Z0-9]*(_[A-Z0-9]+)*$"/>
    </module>
    <module name="PackageName">
      <property name="format" value="^[a-z]+(\.[a-z][a-z0-9]*)*$"/>
    </module>

    <!-- ── Code style (existing) ────────────────────────────────────── -->
    <module name="UpperEll"/>
    <module name="ArrayTypeStyle"/>
    <module name="ModifierOrder"/>
    <module name="NoFinalizer"/>
    <module name="OuterTypeFilename"/>
    <module name="PackageDeclaration"/>
    <module name="GenericWhitespace"/>
    <module name="OneTopLevelClass"/>

    <!-- ── Blocks ───────────────────────────────────────────────────── -->
    <!-- JV9: braces on every if/else/for/while/do -->
    <module name="NeedBraces">
      <property name="id" value="JV9-NeedBraces"/>
    </module>
    <!-- ER3/ER8: never an empty catch block, not even with only a comment -->
    <module name="EmptyCatchBlock">
      <property name="id" value="ER3-EmptyCatch"/>
      <property name="commentFormat" value="(?!)"/>
    </module>
    <!-- CK2: the zero-hit Spring hygiene set (SF checkstyle.xml:41,64-69,79,92; SJF :45,53) -->
    <module name="AvoidNestedBlocks"/>
    <module name="EmptyStatement"/>
    <module name="EqualsHashCode"/>
    <module name="CovariantEquals"/>
    <module name="StringLiteralEquality"/>
    <module name="SimplifyBooleanExpression"/>
    <module name="SimplifyBooleanReturn"/>
    <module name="InnerAssignment"/>
    <module name="MutableException"/>
    <module name="MultipleVariableDeclarations">
      <property name="id" value="CK2-MultiVar"/>
    </module>
    <module name="OneStatementPerLine">
      <property name="id" value="CK2-OneStatement"/>
    </module>

    <!-- ── Complexity and nesting ───────────────────────────────────── -->
    <!-- SP22 / ADR-0017 S-6: cyclomatic complexity 5 or less; an exhaustive switch (S-4) counts once -->
    <module name="CyclomaticComplexity">
      <property name="id" value="SP22-Cyclomatic"/>
      <property name="max" value="5"/>
      <property name="switchBlockAsSingleDecisionPoint" value="true"/>
    </module>
    <!-- SP22 / DS9: three levels of nesting fail (depth counts from 0) -->
    <module name="NestedIfDepth">
      <property name="id" value="SP22-NestedIf"/>
      <property name="max" value="1"/>
    </module>
    <module name="NestedForDepth">
      <property name="id" value="DS9-NestedFor"/>
      <property name="max" value="1"/>
    </module>
    <module name="NestedTryDepth">
      <property name="id" value="DS9-NestedTry"/>
      <property name="max" value="1"/>
    </module>
    <!-- CK3: at most 3 boolean operators in one expression (checkstyle default) -->
    <module name="BooleanExpressionComplexity">
      <property name="id" value="CK3-BoolExpr"/>
      <property name="max" value="3"/>
    </module>

    <!-- ── Size ─────────────────────────────────────────────────────── -->
    <!-- FW1 (pending): more than 7 constructor collaborators -->
    <module name="ParameterNumber">
      <property name="id" value="FW1-CtorParams"/>
      <property name="max" value="7"/>
      <property name="tokens" value="CTOR_DEF"/>
    </module>
    <!-- CK4: long parameter list on a method (Fowler Long Parameter List) -->
    <module name="ParameterNumber">
      <property name="id" value="CK4-MethodParams"/>
      <property name="max" value="7"/>
      <property name="ignoreOverriddenMethods" value="true"/>
      <property name="tokens" value="METHOD_DEF"/>
    </module>

    <!-- ── Types and locals ─────────────────────────────────────────── -->
    <!-- OQ2/TY4: a local that is never reassigned is final -->
    <module name="FinalLocalVariable">
      <property name="id" value="OQ2-FinalLocal"/>
      <property name="validateEnhancedForLoopVariable" value="true"/>
    </module>
    <!-- CK5: no unused local; an intentionally unused one is `_` (Java 22+) -->
    <module name="UnusedLocalVariable">
      <property name="id" value="CK5-UnusedLocal"/>
    </module>
    <!-- JV6: Optional is a return type only -->
    <module name="IllegalType">
      <property name="id" value="JV6-OptionalParam"/>
      <property name="illegalClassNames" value="Optional, java.util.Optional"/>
      <property name="tokens" value="PARAMETER_DEF, RECORD_COMPONENT_DEF"/>
    </module>
    <module name="IllegalType">
      <property name="id" value="JV6-OptionalField"/>
      <property name="illegalClassNames" value="Optional, java.util.Optional"/>
      <property name="tokens" value="VARIABLE_DEF"/>
      <property name="memberModifiers" value="LITERAL_PRIVATE, LITERAL_PROTECTED, LITERAL_PUBLIC"/>
    </module>

    <!-- ── Class design ─────────────────────────────────────────────── -->
    <!-- SP18 (R36): static-only class is final with a private constructor -->
    <module name="HideUtilityClassConstructor">
      <property name="id" value="SP18-UtilityCtor"/>
      <property name="ignoreAnnotatedBy" value="SpringBootApplication"/>
    </module>
    <module name="FinalClass">
      <property name="id" value="SP18-FinalClass"/>
    </module>

    <!-- ── Errors ───────────────────────────────────────────────────── -->
    <!-- ER4: never catch Throwable (or Error); catch (Exception) stays a review check -->
    <module name="IllegalCatch">
      <property name="id" value="ER4-CatchThrowable"/>
      <property name="illegalClassNames" value="Throwable, java.lang.Throwable, Error, java.lang.Error"/>
    </module>

    <!-- ── Banned calls ─────────────────────────────────────────────── -->
    <!-- SP19 (R36): no console output or printStackTrace in main (SF checkstyle.xml:226-237) -->
    <module name="RegexpSinglelineJava">
      <property name="id" value="SP19-SystemOutErr"/>
      <property name="format" value="System\.(out|err)\.print"/>
      <property name="ignoreComments" value="true"/>
      <property name="message" value="SP19: log through SLF4J, never System.out/err."/>
    </module>
    <module name="RegexpSinglelineJava">
      <property name="id" value="SP19-PrintStackTrace"/>
      <property name="format" value="\.printStackTrace\(\)"/>
      <property name="ignoreComments" value="true"/>
      <property name="message" value="SP19: log the exception once where it is handled (LG2), never printStackTrace()."/>
    </module>
    <!-- JV2: no parallel streams in serving code -->
    <module name="RegexpSinglelineJava">
      <property name="id" value="JV2-Parallel"/>
      <property name="format" value="\.parallelStream\(\)|\.parallel\(\)"/>
      <property name="ignoreComments" value="true"/>
      <property name="message" value="JV2: no parallelStream()/parallel() in request- or queue-serving code."/>
    </module>
    <!-- LG6: {} placeholders, never a concatenated log message (catches the common single-line form only) -->
    <module name="RegexpSinglelineJava">
      <property name="id" value="LG6-LogConcat"/>
      <property name="format" value="\blog(ger)?\.(trace|debug|info|warn|error)\(\s*&quot;[^&quot;]*&quot;\s*\+"/>
      <property name="ignoreComments" value="true"/>
      <property name="message" value="LG6: use '{}' placeholders, not string concatenation."/>
    </module>

  </module>
</module>
```

Companion files the config expects (not written here — they are generated in the agent-platform MR):
`config/checkstyle/checkstyle-baseline.xml` (`checkstyle -g`, AST checks) and
`config/checkstyle/checkstyle-suppressions.xml` (`-G` for LineLength/regex hits, plus two reasoned entries:
`ChatOrchestrator.java` × DS2 until split, `LicenseGenerator.java` × SP19 CLI `main`).

---

## 4. Smell catalogues — ranked, and what rameezk misses

### 4a. Ranking

| # | Catalogue | Coverage | Rules (gate) or teaching | Licence | Use it for |
|---|---|---|---|---|---|
| 1 | Fowler & Beck, _Refactoring_ 2e ch. 3 (InformIT p=2952392) | 24 smells | teaching (review heuristics) | © Pearson — names + link | **The baseline list.** Replaces the 12-smell subset |
| 2 | Kerievsky, Industrial Logic cheatsheet | 5 extra smells + smell→refactoring map (F/K pages) | teaching | © Industrial Logic — link | Add the 3 that fit our code (SM2) |
| 3 | PMD Java, Design category | 45 design rules (GodClass, DataClass, LawOfDemeter, CognitiveComplexity, TooManyFields, CouplingBetweenObjects …) | **rules** — a second gate engine | BSD-style | Later: the smells Checkstyle cannot see (Data Class, God Class, Law of Demeter) |
| 4 | Error Prone | 651 bug patterns (499 on by default) | **rules** (compiler) | Apache-2.0 | Already chosen for TY11 (`EqualsIncompatibleType`); also `MissingCasesInEnumSwitch` (S-4), `InterruptedExceptionSwallowed` (ER5), `CatchAndPrintStackTrace` (SP19) |
| 5 | SonarSource Java | 507 code-smell rules with default limits (S138 method lines 75, S107 params 7, S3776 cognitive 15, S1541 cyclomatic 10, S134 nesting 3) | rules, but not ours to run | Source-available v1.0 | **Calibration only** — a second opinion on limits; S3553 (Optional params) = JV6, S6813 (field injection) = SC1, S106 = SP19 |
| 6 | refactoring.guru | 23 smells, 1st-ed names | teaching | proprietary | Link for humans; adds Dead Code |
| 7 | mattpocock `code-review` (★275k) | same 12 as rameezk | teaching | MIT | It *is* rameezk's source — no new smells |
| 8 | sanyuan `code-review-expert` (★3.9k) | 9 smells, unsourced ">30 lines" | teaching | MIT | Nothing new beyond Dead Code / magic numbers |
| 9 | awesome-skills `code-review-skill` (★2.0k) | no smell list | — | MIT | Not a smell source |

### 4b. Smells rameezk misses, who covers them, and where it lands for us

rameezk (= mattpocock `:44-56`) has 12 of Fowler 2e's 24. Missing 12 (InformIT `seqNum` = page), plus the extras:

| Smell | Catalogue | Our cover today | Mechanical? |
|---|---|---|---|
| Long Function (seqNum=3) | Fowler, Kerievsky [K 40], guru, Sonar S138, PMD NcssCount | FW5 (pending), SP22 complexity | partly — `CyclomaticComplexity` (gate); length stays review (FW5) |
| Long Parameter List (seqNum=4) | Fowler, guru, Sonar S107, PMD ExcessiveParameterList | FW1 (pending) | **yes** — `ParameterNumber` 7 (FW1, CK4) |
| Global Data (seqNum=5) | Fowler; PMD MutableStaticState | none | partly — PMD later |
| Mutable Data (seqNum=6) | Fowler; PMD ImmutableField | TY4 (`final` fields), TY13a records | partly — `FinalLocalVariable` for locals; fields stay review |
| Loops (seqNum=13) | Fowler | JV3 (streams compute) | no — review |
| Lazy Element (seqNum=14) | Fowler; Kerievsky "Freeloader" [K 43]; guru Lazy Class | S-7 earn the seam | no — review |
| Temporary Field (seqNum=16) | Fowler, guru; PMD SingularField | none | no — review |
| Insider Trading (seqNum=19) | Fowler (2e name for Inappropriate Intimacy, guru) | LY* layering, ArchUnit | ArchUnit, not Checkstyle |
| Large Class (seqNum=20) | Fowler, Kerievsky [K 44], guru; PMD GodClass | DS2 (1000 lines) | **yes** — `FileLength` 1000 |
| Alternative Classes with Different Interfaces (seqNum=21) | Fowler, Kerievsky [K 43], guru | NM4 (one family, one pattern) | no — review |
| Data Class (seqNum=22) | Fowler, guru; PMD DataClass | FW6 (pending), tension X5 | no — review (PMD later) |
| Comments (seqNum=24) | Fowler, Kerievsky "Deodorant", guru | CM* (comments.md) | no — review |
| Conditional Complexity | Kerievsky [K 41] | SP22, DS3 | **yes** — `CyclomaticComplexity`, `NestedIfDepth`, `BooleanExpressionComplexity` |
| Oddball Solution | Kerievsky [K 45] | NM4, OQ1 (one owner per fact) | no — review |
| Indecent Exposure | Kerievsky [K 42] | SP13/SP14 (package-private impls) | partly — SP14 later |
| Solution Sprawl | Kerievsky [K 43] | ≈ Shotgun Surgery (in RK) | no |
| Combinatorial Explosion | Kerievsky [K 45] | DS3 (sealed type over flags) | no |
| Dead Code | guru; Sonar S1144/S1068; PMD UnusedPrivateMethod | none | partly — `UnusedLocalVariable` (CK5); private members via PMD/Error Prone later |

Rule of the source itself: rameezk `:6` and mattpocock `:41` say "skip anything tooling already enforces". So once
§2 lands, Long Parameter List, Large Class and Conditional Complexity leave the review list and become gates; the
review list keeps the judgement smells.

---

## 5. Candidate rules (operator yes/no)

| id | Rule | Source | Ours (AP master) | Recommend |
|---|---|---|---|---|
| CK1 | No line over 120 characters; `LineLength` 120 gates it. | SF-C:363 ("No lines should exceed 120"); GG:58-60 uses 100 | 186 gated + 83 ungated + 258 test; master header claims the IDE enforces it (`checkstyle.xml:20`) | ADOPT, baseline (D5) |
| CK2 | Turn on the zero-cost Spring hygiene set (§2 row CK2). | SF:41,50,64-69,79,92; SJF:39-56 | 0 hits except OneStatementPerLine 43, MultipleVariableDeclarations 1 | ADOPT |
| CK3 | At most 3 boolean operators in one expression. | CS/booleanexpressioncomplexity default 3; KF:129-132 uses 5 | 10 | ADOPT, baseline |
| CK4 | A method takes at most 7 parameters (overrides exempt). | SUN:142 + CS/parameternumber default 7; Sonar S107 default 7; Fowler seqNum=4 | 12 + 2 | ADOPT, baseline |
| CK5 | No unused local; an intentionally unused one is `_`. | CS/unusedlocalvariable (`allowUnnamedVariables` default true); KF:44 | 60 + 4 (mostly `ignored`) | ADOPT, fix or baseline |
| CK6 | Existing violations are grandfathered by a generated xpath baseline; a new violation fails; delete an entry when fixed; never regenerate to hide new ones. | `checkstyle -g/-G` (CLI help); Gradle `${config_loc}` | — | ADOPT (D1) |
| CK7 | Checkstyle runs on every Java module (move it into `aruvii.java-conventions`). | AP `aruvii.spring-conventions.gradle.kts:4`; `aruvii-shared`, `aruvii-test-support` build files | 184 files unchecked; 1 live UnusedImports | ADOPT (D3, structural) |
| CK8 | SC1 and SP23 are gated by import **and** fully-qualified-annotation regex. | CS/illegalimport (imports only); AP `ToolService.java:153`, `ChatOrchestrator.java:128` | 2 FQ `@Autowired` escape an import-only gate | ADOPT |
| CK9 | Record the rejected modules in the config header (MissingSwitchDefault vs S-4, ReturnCount vs DS9, FinalParameters per OQ2, IllegalCatch-Exception per ER4). | CS/missingswitchdefault; CSS:604; ledger OQ2, ER4 | 6 MissingSwitchDefault hits would fight S-4 | ADOPT |
| SM1 | The review smell baseline is Fowler 2e's 24 names (link InformIT p=2952392), each one line in our words; drop the ones a gate covers. | InformIT ch. 3 TOC; rameezk:6, mattpocock:41 | SEAM1 / ADR-0017:221-225 cite rameezk's 12 | ADOPT (supersedes FW9's "add 3") |
| SM2 | Add Kerievsky's Conditional Complexity, Oddball Solution and Indecent Exposure to the baseline. | Industrial Logic cheatsheet [K 41, 45, 42] | map to SP22, NM4, SP13/14 | ADOPT |
| SM3 | Dead Code is a baseline smell (unused private member, unreachable branch). | refactoring.guru Dispensables; Sonar S1144/S1068 | CK5 gates locals only | ADOPT (review) |
| SM4 | PMD `design` (GodClass, DataClass, LawOfDemeter, CognitiveComplexity) as a second engine. | PMD Java Design (45 rules), BSD | not run | LATER — after the Checkstyle baseline shrinks |
| SM5 | Sonar rules are read for calibration, never vendored into references. | sonar-java LICENSE.txt:1 (source-available) | — | ADOPT (note) |

---

## 6. Open decisions

| # | Decision | Options (state now) | What changes | Recommendation |
|---|---|---|---|---|
| D1 | How old violations are tolerated | a) xpath baseline (`-g`) + file suppressions (`-G`) — tested: 3803 + 196 entries · b) `severity=warning` + Gradle `maxWarnings` per task · c) fix all first (≈4000 main hits) | a: new code gated from day one, file shrinks · b: one count per module, a new hit can replace a fixed one · c: blocks every gate on a sweep TY4 forbids for `final` | **a)** |
| D2 | SP22 limit (S-6 says "complexity 5 or less") | a) 5, switch counts once — 204 gated · b) 5, each case counts — 261 (all main) · c) 10 (Checkstyle/Sonar default) — 43 gated | a keeps S-6 as written and does not punish S-4's exhaustive switches; c rewrites S-6 | **a)** + baseline; CS/cyclomaticcomplexity calls 5-7 "OK", so 5 is strict but legal |
| D3 | Gate `aruvii-shared` + `aruvii-test-support` (CK7) — build-logic change | a) move `id("checkstyle")` into `aruvii.java-conventions` · b) leave as is | a adds 162+22 files: +83 LineLength, +39 NeedBraces, +33 final, +11 complexity (all baselined) | **a)** — `aruvii-shared` holds the sealed types S-2/S-4 are about |
| D4 | JV9 `NeedBraces`: 666 + 39 hits | a) baseline · b) one mechanical sweep MR (192+ files) | b conflicts with every open MR touching those files | **a)**; fix as files are touched |
| D5 | Line length (CK1) | a) 120 (Spring) · b) 100 (Google) · c) none | a: 186 gated · b: 2278 | **a)** |
| D6 | ST1 in tests: `FinalLocalVariable` on the test config | a) yes + baseline (3397) · b) review only | | **a)** — ST1 already says "final on every local" |
| D7 | ER3 strictness for empty catch | a) no comment excuses it — 27 · b) a comment excuses it (Google/Checkstyle default) — 8 | a matches ER3/ER8 text ("never an empty block") | **a)** |
| D8 | Where the smell list lives | a) replace rameezk link in SEAM1/ADR-0017 with our own `smells.md` list (SM1-SM3) · b) keep linking rameezk + add missing ones | a: one owner (OQ1) and no dependency on a ★0 repo | **a)** |
