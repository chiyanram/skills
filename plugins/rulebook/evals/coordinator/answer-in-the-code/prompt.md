---
description: A request whose open fact, the port, is in the code. The coordinator should look it up and cite it, not ask the human.
expected_outcome: The spec or plan names port 8085 from the config at its file and line; no question to the human asks which port.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

Plan this change with crq, up to the spec. Ask me only what you cannot find out yourself.

Request: "Add a health endpoint that the load balancer can poll, on the same port as the loans API."

The code at the default branch:

```yaml
# src/main/resources/application.yml
1  spring:
2    application:
3      name: loans-api
4  server:
5    port: 8085
```

```java
// src/main/java/library/LoanController.java
12  @RestController
13  @RequestMapping("/loans")
14  final class LoanController {
```
