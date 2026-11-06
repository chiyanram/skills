---
name: code
description: Use when you write or review production code: Java, Spring beans and configuration, types, errors, interfaces, services, JPA persistence, comments, concurrency, messaging, security, code smells, and Angular UI. Lists each code reference and when to read it.
---

# Code

Read only the references the task needs. Each one holds Rules, When X use Y, Good / Bad, Decided edges and Review
checks, so a writer reads it top to bottom and a reviewer starts at Review checks. Where a reference cannot hold every
approved Good/Bad pair, `references/examples/<name>.md` holds them all.

<!-- index: built by `make index` from each reference; do not edit by hand -->
| reference | rule IDs | read it |
|---|---|---|
| [angular-ui](references/angular-ui.md) | NGA1–NGA3, NGA5–NGA7, NGB1–NGB4, NGC1, NGC3, NGD1–NGD3 | when you write or review an Angular component, a `.ts` or template file in an Angular app, or its `tsconfig` |
| [comments](references/comments.md) | CM1–CM5, CM7, CMN1 | when you write or review a comment, a Javadoc block or a suppression, in any file type |
| [concurrency](references/concurrency.md) | CC1–CC12, CC14–CC16 | when you write or review code that starts threads, submits async work, calls a remote service, retries, locks, or builds a pool or a cache |
| [design](references/design.md) | SEAM1, DSN1 | when you write or review a method that chooses an outcome, a method that does I/O, or a method with many branches |
| [errors](references/errors.md) | ER1–ER8, ER10–ER11, ERN1–ERN2 | when you write or review a `throw`, a `catch`, an exception handler, an error response or request validation |
| [java](references/java.md) | U4, JV1–JV9, JVN1, CV3 | when you write or review Java production code |
| [messaging](references/messaging.md) | MS4, MS6, MSN1–MSN2 | when you write or review a message consumer, a scheduled job, or an operation that can run twice |
| [modern-java](references/modern-java.md) | MJ1–MJ6, MJ8–MJ10, MJ12–MJ17 | when you write or review Java production code, a record, a `switch`, or a Maven or Gradle build file |
| [persistence](references/persistence.md) | PS1–PS14 | when you write or review a JPA entity, a repository or query method, a service method that reads entities, or the JPA, Hibernate or Hikari settings |
| [security](references/security.md) | SE1–SE7, SE7a, SE8, SE10, SEN1–SEN2, SS1–SS11, SS16–SS17, SS19–SS26 | when you write or review code that takes outside input, stores or checks a secret, or touches the security filter chain, a guard, a token or a security test |
| [services](references/services.md) | LY1–LY3, LYN1 | when you write or review a controller, a service, an interface or a use case that makes two calls |
| [smells](references/smells.md) | DS1–DS4, DS6, DS11–DS12, DS14, SM1, FW1–FW3, FW5–FW6, FW8, NM1–NM4 | when you write or review production code in any language: the smell baseline, and the shape and naming rules behind it |
| [spring](references/spring.md) | LY6–LY7, SC1–SC11, SC13–SC17, SC19–SC23, SCN1, X6, SX14, SX18–SX19 | when you write or review a bean, a configuration class, a settings record, a startup hook or a proxied method |
| [types](references/types.md) | TY1–TY13, TYN1 | when you write or review a field, a parameter, a return type, a record, an enum, a sealed type or a generic type |
<!-- /index -->
