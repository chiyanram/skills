---
name: code
description: Use when you write or review production code: Java, Spring beans and configuration, types, errors, interfaces, services, comments, concurrency, messaging, security, code smells, and Angular UI. Lists each code reference and when to read it.
---

# Code

Read only the references the task needs. Each one holds Rules, When X use Y, Good / Bad, Decided edges and Review
checks, so a writer reads it top to bottom and a reviewer starts at Review checks. Where a reference cannot hold every
approved Good/Bad pair, `references/examples/<name>.md` holds them all.

| reference | rule IDs | read it when |
|---|---|---|
| [angular-ui](references/angular-ui.md) | NGA–NGD | you write or review an Angular component, template, or its TypeScript or `tsconfig` |
| [comments](references/comments.md) | CM | you write or review a comment, a Javadoc block or a lint suppression |
| [concurrency](references/concurrency.md) | CC | you start threads, submit async work, call a remote service, retry, lock, or build a pool or a cache |
| [design](references/design.md) | SEAM | you write or review an interface a caller depends on, or a method that implements one |
| [errors](references/errors.md) | ER | you write or review a `throw`, a `catch`, an exception handler or request validation |
| [java](references/java.md) | U4, JV | you write or review Java production code |
| [messaging](references/messaging.md) | MS | you write or review a message consumer, a scheduled job, or an operation that can run twice |
| [security](references/security.md) | SE, SS | code takes outside input, stores or checks a secret, or touches the security filter chain, a guard, a token or a security test |
| [services](references/services.md) | LY1–LY3 | you write or review a controller, a service, an interface or a use case that makes two calls |
| [smells](references/smells.md) | DS, FW, NM, SM | you write or review production code: the smell baseline, and the shape and naming rules behind it |
| [spring](references/spring.md) | LY6, LY7, SC, X6, SX | you write or review a bean, a configuration class, a settings record, a startup hook or a proxied method |
| [types](references/types.md) | TY | you write or review a field, parameter, return type, record, enum, sealed type or generic type |
