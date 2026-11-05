# R10 · Can Claude cloud sessions be a worker backend (and host a coordinator)?

Type: wayfinder:research (AFK) · Status: closed · Assignee: claude · Blocked by: —
Part of: ../map.md · Informs: G4 (backends), D1

## Question

From Anthropic's own docs (code.claude.com, claude.ai/code, Agent SDK, Claude Code on the web / cloud sessions,
remote triggers / scheduled agents): can a coordinator (a local Claude Code session, a coordinator agent on a VM, or
a web app via the Agent SDK) programmatically START a cloud session with a given repo, branch, agent definition and
first message (the brief), WATCH its progress/status, SEND it a follow-up, and END/clean it up? Which plugins,
settings, CLAUDE.md/AGENTS.md and skills does a cloud session load (project vs user vs managed scope)? Credentials
for GitLab (cloud sessions are GitHub-first?) and the 5h/weekly limits. Can a cloud session host the coordinator
itself? Verdict per capability: supported / partial / not supported, each with a doc URL.

## Resolution (2026-10-01)

`../research/12-claude-cloud-backend.md` + lead corrections. Spawn (`claude --cloud`) and steer (`claude -p … --cloud <id>`)
are documented; GitLab push-back is NOT supported on Anthropic-hosted environments (bundle in, nothing out). Cloud is
a backend adapter for later — usable via a self-hosted environment or a GitHub mirror; Agent SDK remains the path for
the AG-UI web app coordinator.
