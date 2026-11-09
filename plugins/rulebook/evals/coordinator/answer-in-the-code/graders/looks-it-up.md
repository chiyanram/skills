---
type: llm
---

The port is a fact in the code: `server.port: 8085` at `application.yml` line 5.

PASS if the output uses port 8085 and cites where it comes from (the file, ideally with its line), and does not ask the human which port the API uses.

FAIL if the output asks the human which port to use, or picks a port without citing the config.
