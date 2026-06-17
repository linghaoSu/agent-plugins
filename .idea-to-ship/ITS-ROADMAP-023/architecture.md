# Architecture - Roadmap External PM Export

**Slug:** ITS-ROADMAP-023
**Date:** 2026-06-17
**Status:** draft
**References:** requirements.md

## Summary

Build a deterministic export helper under `idea-to-ship/scripts/` and expose it
through the existing `$idea-to-ship:roadmap` workflow as an export-only mode.
The helper parses structured roadmap items, validates eligibility, renders one
overview issue/item plus linked child items for Linear or GitLab, and writes
Markdown, JSONL, and a manifest atomically. It never calls live provider APIs;
deduplication and retry are driven by stable roadmap IDs, content hashes, and
manifest entries.

## Goals / Non-Goals

Goals:

- Satisfy FR-1 through FR-19 with an export-only MVP.
- Keep roadmap markdown as the source of truth.
- Preserve all required roadmap evidence in provider-ready records.
- Generate exactly one overview issue/item per export scope and link child
  records to it.
- Make reruns deterministic and idempotent through stable IDs and a manifest.
- Hard fail before final output when required fields, mappings, or existing
  resource state are ambiguous.
- Keep tests local, deterministic, and provider-free.

Non-goals:

- No live Linear, GitLab, GitHub, Jira, or other provider writes.
- No provider tokens or auth config.
- No sync or write-back.
- No title-only deduplication.
- No export of weak, unknown, inferred, or unanchored items by default.
- No broad new orchestrator skill.

## Codebase Context

Sub-agent exploration fallback: runtime-native explorer delegation was not used
because the current request did not explicitly authorize sub-agents for this
architecture pass. The main context performed the codebase exploration and
records the relevant findings below.

Relevant files and conventions:

- `idea-to-ship/skills/roadmap/SKILL.md` owns portfolio and slug roadmap
  generation, source authority, generated marker preservation, Candidate Brief
  gates, final lane validation, and refresh behavior. The export mode should
  extend this workflow rather than invent a separate planning source.
- `idea-to-ship/templates/roadmap-item-schema.md` defines stable IDs,
  candidate table fields, lane item fields, and the required lane item field
  names. This is the parser contract for child records.
- `idea-to-ship/templates/roadmap-final.md` defines generated marker behavior,
  lane sections, milestones, dependency sections, status by feature, candidate
  backlog, and open decisions.
- `idea-to-ship/templates/roadmap-candidate-brief.md` defines Candidate Brief
  structure and keeps Unverified Signals separate from candidate work.
- `tests/idea-to-ship-eval-fixtures.py` already contains roadmap artifact
  helpers for generated markers, draft fallback, structured lane fields, and
  current roadmap artifact checks. Export behavior should extend this fixture
  family or be invoked from its shell wrapper.
- `tests/idea-to-ship-eval-fixtures.sh` is the release-gate entry point for
  critical idea-to-ship contract and artifact fixtures.
- `scripts/release-gate.sh` runs `idea-to-ship-fixtures` in `all` mode and in
  staged/working mode when the diff touches `idea-to-ship/` or its fixture
  files. A helper under `idea-to-ship/scripts/` will naturally trigger those
  fixtures when changed.
- Plugin-specific scripts already live under plugin directories, such as
  `secret-scanner/scripts/scan.py` and `skill-stats/scripts/skill_cleaner_wrapper.py`.
  A roadmap exporter belongs under `idea-to-ship/scripts/`, not top-level
  `scripts/`.
- `skill-stats/scripts/skill_cleaner_wrapper.py` and
  `tests/skill-stats-cleaner-fixtures.py` provide a useful local precedent for
  deterministic CLI behavior, JSON output validation, fixture temp roots, and
  plan/apply safety checks, though this feature must remain export-only.

Layering conventions:

- Skills define workflow contracts in markdown.
- Deterministic behavior belongs in local scripts and fixtures where possible.
- Templates live under `idea-to-ship/templates/`.
- Verification is offline and provider-free.
- Release gate integration is advisory unless `--strict` is used.

Tech stack constraints:

- Python 3 is available and already required by the release gate.
- Avoid new runtime dependencies for markdown parsing or provider SDKs.
- Use standard-library parsing and JSON only.
- Use atomic file writes for generated artifacts.

## Cross-Skill Routing

| Signal | Routed skill | Result | Design impact |
|---|---|---|---|
| External PM state, duplicate issue risk, retry behavior, and data-safety constraints | `antifragile:antifragile-system` recommended, not run in this architecture pass | MVP avoids live provider calls; resilience constraints are folded into the design locally | Export-only mode, provider-free fixtures, hard validation before final writes, manifest-based idempotency, and no live provider release-gate checks are mandatory. |
| Retry/state-machine signal from manifest classifications | `harness-engineering:sprint-contract` considered, not run | The state machine is small and deterministic enough for local script fixtures | Use explicit status values (`new`, `unchanged`, `changed`, `skipped-existing`, `conflict`, `needs-user`) and fixture them instead of adding a harness. |
| Provider auth, tokens, or credentials | `secret-scanner:scan-secrets` not run | No provider auth or secret material is in scope for MVP | Architecture prohibits token config, live API clients, `.env` examples, and provider SDK setup in the first pass. |

## Alternatives Considered

### Option A - Roadmap Skill Plus Deterministic Export Helper

Extend `$idea-to-ship:roadmap` with an export-only path that calls or instructs
the operator to run `idea-to-ship/scripts/roadmap_export.py`. The script owns
parsing, validation, rendering, hashing, manifest updates, and atomic writes.
The roadmap skill remains the user-facing workflow owner and documents the
mutation boundary.

**Module changes:** `idea-to-ship/skills/roadmap/SKILL.md`,
`idea-to-ship/scripts/roadmap_export.py`, roadmap export templates under
`idea-to-ship/templates/`, `tests/idea-to-ship-eval-fixtures.py` or a called
export fixture, `tests/idea-to-ship-eval-fixtures.sh`, and docs/catalog entries
if a public flag is documented.

**Data flow:** User invokes roadmap export mode -> roadmap skill resolves source
scope and provider -> script reads source roadmap and optional mapping/manifest
-> script validates items -> script writes generated export artifacts
atomically -> user manually imports or reviews.

**Interfaces:** A Python CLI plus generated artifact schema. The skill can
reference the CLI rather than embedding parsing logic in prompts.

**Pros:**

- Matches repo pattern: skill markdown for workflow, Python for deterministic
  checks and transforms.
- Small blast radius: no new public plugin or provider API layer.
- Strong testability: parser, validation, idempotency, and rendering can be
  fixture-tested locally.
- Easy to reverse: remove the helper and skill export section without changing
  core roadmap generation.
- Keeps provider writes out of `/roadmap`.

**Cons:**

- Adds the first `idea-to-ship/scripts/` helper, so maintainers must accept a
  new plugin-local script directory.
- Requires careful markdown parsing of existing roadmap shape without a third
  party markdown parser.
- Export UX is less discoverable than a dedicated public skill unless docs are
  updated clearly.

**Risk:** Medium. The main risk is parser drift if roadmap item structure
changes. Mitigation is to parse only the stable item schema and fixture the
current roadmap shapes.

### Option B - Model-Only Roadmap Export In The Skill Prompt

Add instructions to `$idea-to-ship:roadmap` telling the model to manually
produce Linear/GitLab issue lists from the current roadmap artifact.

**Module changes:** `idea-to-ship/skills/roadmap/SKILL.md`,
`idea-to-ship/templates/roadmap-export-markdown.md`, and contract fixtures for
the prompt.

**Data flow:** User invokes roadmap export mode -> model reads roadmap -> model
writes Markdown/JSONL-ish output directly into artifacts.

**Interfaces:** Mostly artifact templates and prompt contracts.

**Pros:**

- Very small implementation footprint.
- No parser code.
- Fast to add as documentation.

**Cons:**

- Poor fit for hard fail, retry, manifest hashing, and duplicate prevention.
- JSONL and manifest output can be malformed or inconsistent.
- Hard to prove provider-free idempotency with fixtures.
- Repeats the exact risk the repo avoids elsewhere: model judgment doing a
  deterministic transform.

**Risk:** High. This option would make export correctness depend on model
discipline instead of deterministic checks.

### Option C - New Public `idea-to-ship:roadmap-export` Skill

Create a separate public skill dedicated to roadmap exports. The skill would
wrap the same deterministic helper as Option A but expose a distinct entry
point instead of extending `$idea-to-ship:roadmap`.

**Module changes:** New `idea-to-ship/skills/roadmap-export/SKILL.md`, optional
`agents/openai.yaml`, `idea-to-ship/scripts/roadmap_export.py`, templates,
README/SKILLS/catalog metadata, and fixtures.

**Data flow:** User invokes `$idea-to-ship:roadmap-export` -> skill checks source
roadmap and provider -> helper writes artifacts.

**Interfaces:** New public skill plus helper CLI.

**Pros:**

- Clear user-facing boundary for export behavior.
- Keeps `$idea-to-ship:roadmap` smaller.
- Easy to route future sync/write-back work away from roadmap generation.

**Cons:**

- Adds a new public skill for a feature that is still tightly coupled to
  roadmap semantics.
- More docs/catalog/metadata maintenance.
- Higher risk of users skipping roadmap source gates and treating export as a
  backlog generator.

**Risk:** Medium. The helper would still be deterministic, but the public skill
surface increases maintenance and routing complexity.

## Recommendation

**We pick Option A.** A deterministic helper owned by the existing roadmap
workflow is the smallest design that satisfies export-only, hard-fail,
manifest, retry, and provider-free fixture requirements. The accepted tradeoff
is adding a new `idea-to-ship/scripts/` helper and modest export documentation
to `$idea-to-ship:roadmap`, rather than creating a separate public skill.

Option A fits the codebase because roadmap semantics already live in
`idea-to-ship/skills/roadmap/SKILL.md`, the stable item schema already lives in
`idea-to-ship/templates/roadmap-item-schema.md`, and deterministic behavior is
already tested through `tests/idea-to-ship-eval-fixtures.py`. It keeps live PM
provider integration out of the blast radius and leaves future sync/write-back
as a separate roadmap item or later stage.

## Chosen Design - Detail

### Module Breakdown

- `idea-to-ship/scripts/roadmap_export.py` - new deterministic CLI. Owns
  roadmap parsing, item eligibility, provider mapping, overview/child record
  construction, validation, content hashing, manifest merge, and atomic output
  writes.
- `idea-to-ship/templates/roadmap-export-markdown.md` - new documentation
  template for the human-readable export artifact shape. The script may render
  directly from code, but the template documents required sections and generated
  markers.
- `idea-to-ship/templates/roadmap-export-schema.md` - new schema reference for
  JSONL records, manifest fields, status values, provider mapping fields, and
  blocked item reasons.
- `idea-to-ship/skills/roadmap/SKILL.md` - add export-only workflow rules,
  arguments, safety gates, provider-free behavior, and hand-off guidance.
- `idea-to-ship/README.md`, `README.md`, and `SKILLS.md` - update only if the
  export mode becomes a documented public invocation.
- `tests/idea-to-ship-roadmap-export-fixtures.py` - new behavior fixture for
  the helper. It should create temporary roadmap files and assert output.
- `tests/idea-to-ship-eval-fixtures.sh` - invoke the new export fixture after
  the existing contract fixture helper so release gate keeps one idea-to-ship
  entry point.
- `tests/idea-to-ship-eval-fixtures.py` - add lightweight contract assertions
  that `$idea-to-ship:roadmap` documents export-only boundaries, provider-free
  behavior, stable IDs, and manifest retry semantics.
- `.idea-to-ship/<source-scope>/exports/<provider>/` or
  `.idea-to-ship/exports/<provider>/` - generated output directory, depending
  on source mode.

### Data Flow

```text
User
  -> $idea-to-ship:roadmap --export --provider <linear|gitlab> [scope flags]
  -> roadmap skill resolves source roadmap and safety gates
  -> roadmap_export.py preflight
       -> read roadmap markdown
       -> read optional mapping config
       -> read existing manifest if present
       -> parse structured item blocks and approved candidate records
       -> filter eligible executable items
       -> build overview record
       -> build child records linked to overview
       -> validate required fields and provider mapping
       -> classify rerun status from manifest
       -> render markdown, JSONL, manifest, and report in memory
       -> atomically write generated artifacts
  -> User reviews/imports outside the skill
```

The script should not write final artifacts until all required validation
passes. It may print hard-fail diagnostics and retry guidance to stdout/stderr,
but final importable issue lists must not be left behind after a failed run.

### Interfaces

Primary CLI:

```bash
python3 idea-to-ship/scripts/roadmap_export.py \
  --source .idea-to-ship/roadmap.md \
  --provider linear \
  --scope portfolio \
  --output-dir .idea-to-ship/exports/linear \
  --include-approved-candidates \
  --mapping-file path/to/mapping.json
```

Arguments:

- `--source <path>`: roadmap source. Required.
- `--provider linear|gitlab`: target provider mapping. Required.
- `--scope portfolio|slug`: source mode. Required or inferred from source path.
- `--output-dir <path>`: output directory. Optional; defaults to
  `.idea-to-ship/exports/<provider>/` for portfolio sources and
  `.idea-to-ship/<slug>/exports/<provider>/` for slug sources.
- `--include-approved-candidates`: include approved candidates with concrete
  anchors and detailed required fields.
- `--mapping-file <path>`: optional provider mapping and known remote IDs.
- `--manifest <path>`: optional explicit manifest path; default is
  `<output-dir>/manifest.json`.
- `--formats markdown,jsonl[,csv]`: optional format set; default
  `markdown,jsonl`.
- `--dry-run`: validate and print a summary without writing final artifacts.

Exit codes:

- `0`: export succeeded.
- `1`: validation hard failure or needs-user conflict.
- `2`: usage error, unreadable input, or unsupported provider/format.

Provider mapping config shape:

```json
{
  "provider": "linear",
  "target": {
    "team": "optional-team-key",
    "project": "optional-project-key",
    "cycle": "optional-cycle-key",
    "milestone": "optional-milestone-key"
  },
  "assignees": {
    "Unassigned": null,
    "linghao": "provider-specific-user-id"
  },
  "labels": {
    "roadmap": "roadmap",
    "risk:high": "risk::high"
  },
  "existing_remote": {
    "ITS-ROADMAP-023": {
      "remote_id": "optional-provider-id",
      "remote_url": "optional-provider-url"
    }
  }
}
```

Internal export record shape:

```json
{
  "schema_version": 1,
  "provider": "linear",
  "role": "overview",
  "roadmap_id": "overview:portfolio",
  "title": "Roadmap export - <goal or source>",
  "body_markdown": "...",
  "labels": ["roadmap", "idea-to-ship"],
  "source": {
    "path": ".idea-to-ship/roadmap.md",
    "content_hash": "sha256:..."
  },
  "relation": null,
  "content_hash": "sha256:...",
  "status": "new"
}
```

Child record shape:

```json
{
  "schema_version": 1,
  "provider": "gitlab",
  "role": "child",
  "roadmap_id": "ITS-ROADMAP-023",
  "title": "[ITS-ROADMAP-023] Export idea-to-ship roadmaps to external PM issue lists",
  "body_markdown": "...",
  "labels": ["roadmap", "type::feature", "risk::high"],
  "source": {
    "path": ".idea-to-ship/roadmap.md",
    "anchors": ["idea-to-ship/templates/roadmap-item-schema.md:3-36"]
  },
  "relation": {
    "overview_id": "overview:portfolio",
    "kind": "child-of-overview"
  },
  "content_hash": "sha256:...",
  "status": "new"
}
```

Manifest shape:

```json
{
  "schema_version": 1,
  "generated_at": "2026-06-17T00:00:00Z",
  "source": {
    "path": ".idea-to-ship/roadmap.md",
    "content_hash": "sha256:..."
  },
  "provider": "linear",
  "overview": {
    "roadmap_id": "overview:portfolio",
    "content_hash": "sha256:...",
    "remote_id": null,
    "remote_url": null,
    "status": "new"
  },
  "items": {
    "ITS-ROADMAP-023": {
      "role": "child",
      "content_hash": "sha256:...",
      "remote_id": null,
      "remote_url": null,
      "status": "new"
    }
  },
  "blocked": {
    "ITS-ROADMAP-999": {
      "reason": "missing source anchors"
    }
  }
}
```

Markdown export artifact:

- Use generated markers:
  `<!-- idea-to-ship:roadmap-export generated:start -->` and
  `<!-- idea-to-ship:roadmap-export generated:end -->`.
- Preserve human notes outside markers if rerun.
- If an existing markdown export has human content and no generated markers,
  write `roadmap-export.draft.md` instead of replacing it.

Output files:

- `roadmap-export.md`: human-readable overview, child issues, blocked items,
  warnings, and retry guidance.
- `issues.jsonl`: one overview record followed by child records.
- `manifest.json`: idempotency and retry state.
- `issues.csv`: optional flat issue list, only if requested.

### Data / Schema Changes

No database or remote schema changes.

Local generated artifact schema additions:

- Export markdown generated markers:
  `idea-to-ship:roadmap-export generated:start/end`.
- JSONL record schema version `1`.
- Manifest schema version `1`.
- Status values: `new`, `unchanged`, `changed`, `skipped-existing`, `conflict`,
  `needs-user`, `blocked`.

### Parser Strategy

Use a narrow, schema-aware parser rather than a broad markdown parser:

- Detect generated roadmap markers when present and parse inside the generated
  section first.
- Parse `### ITS-... - <title>` blocks.
- Extract required `**Field:**` lines from the lane item template.
- Recognize candidate table rows only as an index; require a detailed item
  block or equivalent required fields before exporting an executable child.
- Treat `Unverified Signals`, `Conflicts`, and `Rejected / Not
  Roadmap-Relevant` sections as non-executable sources.
- Reject duplicate stable IDs.
- Reject child records missing required fields from FR-6.

This avoids adding dependencies while still tying parsing to the documented
roadmap item schema.

### Failure Modes & Handling

- Missing source roadmap: exit `2` with usage/setup guidance.
- Unsupported provider or format: exit `2`.
- Missing required item fields: exit `1`, print item ID and missing fields, and
  write no final importable artifacts.
- Duplicate stable IDs: exit `1`, print all conflicting IDs and source
  locations.
- Weak or unverified item: exclude from executable output and list under
  blocked/skipped items.
- Missing optional assignee/project/milestone/cycle: warn if provider output
  remains valid.
- Existing manifest maps a roadmap ID to a different provider/scope: exit `1`
  as `needs-user`.
- Existing manifest has same roadmap ID and same content hash: mark
  `unchanged` or `skipped-existing`; do not generate a duplicate create action.
- Existing manifest has same roadmap ID and different content hash: mark
  `changed` and emit an update/review instruction, not a duplicate create
  action.
- Two existing remote IDs for one roadmap ID: exit `1` as `needs-user`.
- Atomic write failure: exit `1`, leave previous artifacts intact.

### Rollout / Migration

This is additive. Existing roadmap generation does not change unless a user
invokes the export path. Existing `.idea-to-ship/roadmap.md` remains valid and
continues to use its current generated markers. The first implementation should
ship without docs claiming live sync. Future sync/write-back can consume the
manifest schema but must be designed separately with explicit authorization.

### Test Strategy Hooks

Unit-testable seams:

- Roadmap parser from string input to structured item objects.
- Eligibility filter from items to executable/blocked sets.
- Provider mapper from internal issue schema to Linear/GitLab fields.
- Manifest merge/classification logic.
- Content hash computation.
- Atomic output writer with temp directories.

Provider-free behavior fixtures:

- Minimal portfolio roadmap with one eligible item -> overview plus one child.
- Roadmap with weak/unverified items -> blocked section, no executable child.
- Missing required field -> exit `1`, no final output.
- Missing optional assignee/project -> warning, successful output.
- Existing manifest with remote ID -> no duplicate create action.
- Existing manifest with changed content -> changed/update instruction.
- Duplicate remote IDs -> `needs-user` hard fail.
- Repeated run with identical inputs -> stable JSONL ordering and content
  hashes except timestamp metadata.
- Existing markdown export with human content outside markers -> preservation
  or draft fallback.

Release-gate integration:

- `tests/idea-to-ship-roadmap-export-fixtures.py` runs behavior fixtures.
- `tests/idea-to-ship-eval-fixtures.sh` invokes both existing contract fixtures
  and the new export behavior fixture.
- `tests/idea-to-ship-eval-fixtures.py` adds contract invariants for
  roadmap export documentation.
- `scripts/release-gate.sh` does not need a new check if the shell wrapper owns
  the new fixture invocation. It already runs idea-to-ship fixtures when
  `idea-to-ship/` or the fixture files change.

## Staged Implementation Plan

1. **Stage 1 - Provider-neutral exporter core**: Add
   `idea-to-ship/scripts/roadmap_export.py` with source parsing, item
   validation, internal issue schema, overview/child construction, JSONL output,
   manifest output, and focused behavior fixtures. No skill docs yet. Verify
   the script can export a temp roadmap fixture without provider API calls.
2. **Stage 2 - Linear/GitLab mappings and markdown report**: Add first-class
   Linear/GitLab mapping renderers, generated markdown export artifact,
   blocked/skipped sections, warning handling, manifest rerun classification,
   and marker/draft preservation behavior. Verify idempotency and hard-fail
   scenarios.
3. **Stage 3 - Roadmap skill integration and docs**: Update
   `$idea-to-ship:roadmap` instructions, templates, README/SKILLS entries if
   public, and fixture contracts. Wire the export fixture through
   `tests/idea-to-ship-eval-fixtures.sh`; run
   `bash tests/idea-to-ship-eval-fixtures.sh` and
   `scripts/release-gate.sh --mode all --strict`.

Each stage is independently shippable: Stage 1 provides a hidden deterministic
helper, Stage 2 provides complete local export artifacts, and Stage 3 exposes
the workflow safely to users.

## Open Questions

- Should CSV ship in Stage 2 or remain a follow-up until a concrete importer
  needs it?
- Should provider mapping config live only in an explicit JSON file, or should
  the CLI also accept simple flags for common optional fields?
- Should approved candidate export require a command flag only, or should it
  also require a marker in the roadmap item itself?
- Should overview item IDs use `overview:portfolio` / `overview:<slug>` or an
  `ITS-EXPORT-<source>` style ID? The design currently prefers
  `overview:<scope>` because it is clearly not a roadmap work item.
