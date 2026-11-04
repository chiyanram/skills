# Demo

Read it when you write a demo.

## Rules

- **D1** — Enable Checkstyle `MissingSwitchDefault`, because a switch without a default hides a new case (TY2,
  `types.md`).

## When X, use Y

| situation | use | why |
|---|---|---|
| a closed set | a sealed type (D1) | a new case fails to compile |

## Good / Bad

### D1 — a switch

**Bad**
```java
// a citation-looking string inside code is fine: see pstack :15
```
**Good**
```java
switch (x) { case A -> a(); case B -> b(); }
```

## Decided edges

None.

## Review checks

- [ ] D1 — `grep -n "default ->"`. A default arm is a finding.
