# 3. The writer and the reviewer read the same reference

Status: accepted

## Context

When the writing guide and the review rubric are two files, they drift apart, and a review checks rules the writer
never saw.

## Decision

One reference serves both. The writer reads it top to bottom. The reviewer starts at its Review checks, and each
check names the rule ID it enforces.

## Consequences

- A rule changes in one file, and both agents see it in their next session.
