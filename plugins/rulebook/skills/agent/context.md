# Agent context

How each model request is assembled from the run record: one builder, history windowing and compaction, prompt
caching order and breakpoints, and the size of tool results. Read it when you write or review the code that builds a
model request, a memory window, compaction or summarisation of history, a prompt cache breakpoint, or how a tool
result enters context.

## Rules

- Build every model request (chat, resume, summariser, judge) in one pure function from the run record, because a
  second assembly path drifts and drops history, guards or cache order.
- Window and compact history by whole call-and-result pairs, and run one deterministic repair step before each
  request, because providers reject unpaired calls and results. A run with one turn per request carries no history.
- Render each request in stability order: sorted tools, a frozen system prompt, append-only history, per-turn content
  last, with timestamps and ids only in that last part, because an early change invalidates the prompt cache. With no
  prompt cache, or a one-off request with no shared prefix, the order is free.
- Place the provider's cache breakpoints in the adapter, at the end of the stable prefix, because a breakpoint
  anywhere else caches nothing or misses on every turn.
- Trigger windowing and compaction on token counts from the provider or the last usage, and append one summary per
  threshold crossing, leaving stored turns as they are, because rewriting them re-summarises every turn.
- Bound each tool result that can be a list, a document, a page or a search result. A cut result says it was cut and
  how to fetch more, and the full result stays in the run record, because oversized results crowd out the task.
  Tests for each rule here are in the `testing` skill's model-calls notes.

## Good / Bad

### One builder for every request

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

### The window keeps call and result together

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
`lastTurnsWithin` keeps the newest whole turns that fit the token budget, so a call and its result stay
together. `repair` drops any orphan left, the same way before every request.

### Stable content first, per-turn content last

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

### A cut tool result says so

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

## Review

Walk every place that builds a model request, windows or compacts history, or maps a tool result into context.

Each line is a finding, a blocker unless marked (warning).

- More than one request builder, or a builder that reads state other than the run record.
- A cut by message count that can fall between a call and its result, or no repair step before the request.
- A timestamp, id or unsorted collection before the per-turn content, or a rewritten earlier message.
- A cache breakpoint outside the adapter, or one not at the end of the stable prefix.
- A compaction trigger on message count or characters, or a compaction that rewrites stored turns.
- (warning) A list, document or page tool result with no bound, or a cut result that does not say it was cut.
