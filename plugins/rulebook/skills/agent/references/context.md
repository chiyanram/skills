# Agent context

How each model request is assembled from the run record: one builder, history windowing and compaction, prompt
caching order and breakpoints, and the size of tool results. Read it when you write or review the code that builds a
model request, a memory window, compaction or summarisation of history, a prompt cache breakpoint, or how a tool
result enters context.

Contents: Rules · When X, use Y · Good / Bad (AE21, AE22, AE23, AE26) · Decided edges · Review checks

## Rules

- **AE21** — Build every model request (chat, resume, summariser, judge) in one pure function from the run record,
  because a second assembly path drifts and drops history, guards or cache order.
- **AE22** — Never split a tool call from its result when windowing or compacting, and run one deterministic repair
  step before each request, because providers reject unpaired calls and results.
- **AE23** — Render each request in stability order (sorted tools, frozen system prompt, append-only history,
  per-turn content last) with no timestamps or ids early, because an early change invalidates the prompt cache.
- **AE24** — Place the provider's cache breakpoints at the end of the stable prefix, in the adapter, because a
  breakpoint anywhere else caches nothing or misses on every turn.
- **AE25** — Trigger windowing and compaction on token counts from the provider or the last usage, appending one
  summary per threshold crossing and never rewriting stored turns, because rewrites re-summarise every turn.
- **AE26** — Bound each tool result in context; a cut result says so and how to fetch more, and the full result stays
  in the run record, because oversized results crowd out the task.

## When X, use Y

| situation | use | why |
|---|---|---|
| code builds a request for the chat, a resume, a summariser or a judge | the one request builder, called with the run record | a second assembly path drifts and drops history, guards or cache order (AE21) |
| history is cut to a window or compacted | whole call-and-result pairs, then the repair step before the request | providers reject unpaired calls and results (AE22) · its test: the `testing` skill's model-calls notes |
| the provider caches prompts | stability order: sorted tools, frozen system prompt, append-only history, per-turn content last | an early change invalidates the cache (AE23) · its test: `testing`'s model-calls.md |
| the request carries cache breakpoints | breakpoints set in the adapter, at the end of the stable prefix | a breakpoint elsewhere caches nothing or misses every turn (AE24) · its tests: `testing`'s model-calls.md |
| history grows toward the context limit | a token count from the provider or the last usage, and one appended summary per crossing | rewriting stored turns re-summarises every turn (AE25) · its test: `testing`'s model-calls.md |
| a tool returns more than its context share | a cut result that says it was cut and how to fetch more; the full result in the run record | oversized results crowd out the task (AE26) |

## Good / Bad

### AE21 — One builder for every request

**Bad**
```java
final var summaryRequest = new ModelRequest(
        SUMMARY_PROMPT,
        run.messages());
```
The summariser builds its own request. It skips the repair step and the guards the chat request gets, and it sends
history the window had already cut.

**Good**
```java
final var summaryRequest = requests.build(
        run,
        Purpose.SUMMARISE);
```
Chat, resume, summariser and judge all go through one pure `build`. A change to history or ordering reaches them all.

### AE22 — The window keeps call and result together

**Bad**
```java
final var window = history.subList(
        Math.max(0, history.size() - MAX_MESSAGES),
        history.size());
```
The cut can fall between a tool call and its result. The provider rejects the next request.

**Good**
```java
final var window = repair.apply(Windows.lastTurnsWithin(
        history,
        tokenBudget));
```
`lastTurnsWithin` keeps the newest whole turns that fit the token budget (AE25), so a call and its result stay
together. `repair` drops any orphan left, the same way before every request.

### AE23 — Stable content first, per-turn content last

**Bad**
```java
final var system = "Today is " + clock.instant() + ". " + SUPPORT_PROMPT;
return new ModelRequest(
        system,
        tools.all(),
        history);
```
The timestamp changes the first bytes of every request, so the prompt cache never hits. `tools.all()` has no fixed
order, so a reload busts it too.

**Good**
```java
return new ModelRequest(
        SUPPORT_PROMPT,
        tools.sortedByName(),
        history.append(Message.user("Today is " + clock.instant() + ". " + question)));
```
The system prompt and the sorted tools never change. The date goes in the newest turn, after the cached prefix.

### AE26 — A cut tool result says so

**Bad**
```java
final var text = orderHistory.toJson();
return ToolResult.ok(call.id(), text.substring(0, Math.min(text.length(), MAX_CHARS)));
```
The model gets the first part of the history and treats it as all of it. Nothing tells it that orders are missing.

**Good**
```java
final var page = orderHistory.page(0, PAGE_SIZE);
runs.saveFullResult(new CallKey(runId, step, call.id()), orderHistory);
final var note = page.hasMore() ? " Cut to the first page; call again with page=1 for more." : "";
return ToolResult.ok(call.id(), page.toJson() + note);
```
The model knows the result is cut and how to get the rest. The run record keeps the full result.

## Decided edges

- **Skip when** the provider has no prompt cache, or the request is a one-off with no shared prefix: AE23 and AE24
  do not apply. — **Do not skip when** the same agent sends more than one request with the same system prompt and
  tools. — **Confidence** medium
- **Skip when** a tool result is always small by its type, such as a status or a single record: it needs no bound
  (AE26). — **Do not skip when** the result is a list, a document, a page or a search result. — **Confidence**
  high
- **Skip when** the run has no history limit because each request holds one turn: AE22 and AE25 do not apply. —
  **Do not skip when** history is carried between requests. — **Confidence** high

## Review checks

Walk every changed request builder, history window, compactor, cache breakpoint and tool-result mapping.

- [ ] AE21 — List every place that creates a model request. More than one builder, or a builder that reads state
  other than the run record, is a finding.
  Applies when: code creates a model request
  Evidence: each creation site at `file:line`
  Not a finding: none
  Severity: blocker
  Verify: re-open each site and the builder it calls
- [ ] AE22 — Open the window and the compactor. A cut by message count that can fall between a call and its result,
  or no repair step before the request, is a finding.
  Applies when: code windows or compacts history
  Evidence: the cut and the repair call at `file:line`
  Not a finding: a run with one turn per request (decided edge)
  Severity: blocker
  Verify: re-open the cut and the code that sends the request
- [ ] AE23 — Read the request from its first byte. A timestamp, id or unsorted collection before the per-turn
  content, or a rewritten earlier message, is a finding.
  Applies when: the provider caches prompts
  Evidence: the request builder at `file:line`
  Not a finding: no prompt cache or no shared prefix (decided edge)
  Severity: blocker
  Verify: re-open the builder and the order of its parts
- [ ] AE24 — Find where cache breakpoints are set. A breakpoint outside the adapter, or one not at the end of the
  stable prefix, is a finding.
  Applies when: a request carries cache breakpoints
  Evidence: the breakpoint at `file:line`
  Not a finding: no prompt cache (decided edge)
  Severity: blocker
  Verify: re-open the adapter's request mapping
- [ ] AE25 — Open the compaction trigger. A trigger on message count or characters, or a compaction that rewrites
  stored turns, is a finding.
  Applies when: code compacts or summarises history
  Evidence: the trigger and the write at `file:line`
  Not a finding: a run with one turn per request (decided edge)
  Severity: blocker
  Verify: re-open the trigger and what it stores
- [ ] AE26 — For each tool that can return a list, a document or a page, find its bound. No bound, or a cut result
  that does not say it was cut, is a finding.
  Applies when: a tool result enters context
  Evidence: the result mapping at `file:line`
  Not a finding: a result small by its type (decided edge)
  Severity: warning
  Verify: re-open the mapping and the run-record write
