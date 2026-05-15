# Roadmap Item Schema

Use stable item IDs so reruns can update instead of rewriting:
`ITS-ROADMAP-001` for portfolio items, or `ITS-<slug>-001` for slug items.

Each candidate item records:

```markdown
| ID | Title | Status | Work Type | Evidence Class | Confidence | Source Anchors | Suggested Action |
|---|---|---|---|---|---|---|---|
```

Controlled values:
- `Status`: `Committed`, `Planned`, `Candidate`, `Blocked`, `Done`,
  `Deferred`, `Needs Revalidation`
- `Work Type`: `Feature`, `Maintenance`, `Spike`, `Bug`, `Docs`, `Release`
- `Evidence Class`: `Explicit`, `Commercial`, `Artifact`, `Repo`, `Git`,
  `TODO`, `GitHubMilestone`, `GitHubPR`, `GitHubIssue`, `Inferred`

For every item promoted to `Now`, `Next`, `Later`, a milestone, or a release
gate, use this lane item template verbatim:

```markdown
### <ID> - <Title>
**Status:** <Committed|Planned|Candidate|Blocked|Done|Deferred|Needs Revalidation>
**Work Type:** <Feature|Maintenance|Spike|Bug|Docs|Release>
**Evidence Class:** <Explicit|Commercial|Artifact|Repo|Git|TODO|GitHubMilestone|GitHubPR|GitHubIssue|Inferred>
**Confidence:** <High|Medium|Low|Unknown>
**Source Anchors:** <path:line | artifact heading | commit SHA | issue/PR URL | user statement>
**Why Now / Why Next / Why Later:** <prioritization rationale>
**Owner:** <owner or Unassigned>
**Decision Owner:** <owner or None>
**Release Gate:** <entry criteria; exit criteria; evidence required; no-go conditions>
**Evidence Required:** <test, review, artifact, command, user decision>
**Dependencies:** <hard dependencies with evidence; otherwise None>
**Risk:** <low|medium|high - concrete failure mode>
```

The lane item template is the source of truth. Do not substitute looser fields
such as `Gate` or `Evidence`.

Each lane item must include:
- `Why Now` / `Why Next`
- `Owner` or `Unassigned`
- `Decision Owner` if a human decision is required
- `Release Gate`
- `Evidence Required`
- `Dependencies`
- `Risk`
