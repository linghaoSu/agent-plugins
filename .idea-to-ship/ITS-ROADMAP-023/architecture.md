# Architecture - Roadmap External PM Export

**Slug:** ITS-ROADMAP-023
**Date:** 2026-06-17
**Status:** draft
**References:** requirements.md

## Summary

Build a deterministic export helper under `idea-to-ship/scripts/` and expose it
through the existing `$idea-to-ship:roadmap` workflow as an export-only mode.
The helper parses structured roadmap items, validates section-aware eligibility,
renders one overview issue/item plus linked child items for Linear or GitLab,
and writes Markdown, JSONL, and a manifest atomically. It never calls live
provider APIs; deduplication and retry are driven by stable roadmap IDs,
provider target identity, content hashes, and manifest entries.

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

These routes were rechecked during design review because the requirements carry
data-safety, retry, and external-state signals. No adjacent skill writes a
separate artifact for this MVP design; the useful constraints are folded into
the architecture below.

| Signal | Routed skill | Result | Design impact |
|---|---|---|---|
| External PM state, duplicate issue risk, retry behavior, and data-safety constraints | `antifragile:antifragile-system` guidance applied | No implementation exists yet to audit, so the read-only route contributes architecture constraints instead of repo findings | Export-only mode, provider-free fixtures, hard validation before final writes, manifest-based idempotency, explicit multi-file write transaction, and no live provider release-gate checks are mandatory. |
| Retry/state-machine signal from manifest classifications | `harness-engineering:sprint-contract` / `harness-engineering:harness-design` considered and scoped out | The exporter is a deterministic single-shot CLI, not an autonomous or long-horizon agent; the evaluator contract is the fixture suite wired into the release gate | Use explicit status/action values, a deterministic merge table, fixed timestamp seams, and objective fixtures instead of a separate harness artifact. |
| Provider auth, tokens, or credentials | `secret-scanner:scan-secrets` guidance applied, scan not run | No provider auth, token config, `.env` example, or generated secret material is in scope for MVP | Architecture prohibits token config, live API clients, provider SDK setup, and auth examples in the first pass. |

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
- `scripts/release-gate.sh` - add the new export fixture file to staged/working
  trigger paths so edits to the fixture itself still run idea-to-ship checks.
- `.idea-to-ship/<scope-id>/exports/<provider>/` or
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
       -> compute canonical hashes and target identity
       -> classify rerun status from manifest
       -> render markdown, JSONL, manifest, and report in memory
       -> publish generated artifacts through the multi-file write transaction
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
- `--scope portfolio|slug`: source type. Required or inferred from source
  path.
- `--scope-id <id>`: stable source identity. Optional for portfolio sources
  where it defaults to `portfolio`; required or inferred from
  `.idea-to-ship/<slug>/` for slug sources. This ID is used in overview IDs,
  manifests, hashes, and output paths.
- `--output-dir <path>`: output directory. Optional; defaults to
  `.idea-to-ship/exports/<provider>/` for portfolio sources and
  `.idea-to-ship/<scope-id>/exports/<provider>/` for slug sources.
- `--include-approved-candidates`: include approved candidates with concrete
  anchors and detailed required fields.
- `--mapping-file <path>`: optional provider mapping and known remote IDs.
- `--manifest <path>`: optional explicit manifest path; default is
  `<output-dir>/manifest.json`.
- `--csv`: optional additive CSV output. Markdown and JSONL are always produced
  and cannot be disabled in the MVP.
- `--dry-run`: validate and print a summary without writing final artifacts.
- `--generated-at <iso8601>`: optional deterministic timestamp override for
  fixtures. If omitted, read `SOURCE_DATE_EPOCH` when present; otherwise use
  current UTC time.
- `--max-items <n>`: optional safety limit; default `200` parsed roadmap items
  across executable and blocked records.
- `--max-output-bytes <n>`: optional safety limit; default `5000000` bytes
  across generated Markdown, JSONL, manifest, and optional CSV.

Exit codes:

- `0`: export succeeded.
- `1`: validation hard failure or needs-user conflict.
- `2`: usage error, unreadable input, unsupported provider, or unsupported
  output flag. A legacy or future `--formats` value that omits either Markdown
  or JSONL is rejected instead of producing an incomplete export.

Provider mapping contract:

- Linear required target field: `team`. Missing `team` hard fails because a
  Linear issue cannot be import-ready without a target team.
- GitLab required target field: `project_path`. Missing `project_path` hard
  fails because a GitLab issue cannot be import-ready without a target project.
- Optional target fields: Linear `project`, `cycle`; GitLab `milestone`. Missing
  optional targets warn only when the generated output remains valid without
  them.
- Optional assignee mappings: if a roadmap owner is `Unassigned`, emit no
  provider assignee. If a roadmap owner is named and unmapped, warn and preserve
  the owner text in `roadmap_fields.owner` and `body_markdown`; do not invent a
  provider user ID. A future `require_assignee_mappings` config flag may turn
  this warning into a hard fail.
- Optional label mappings: provider labels are emitted only for explicitly
  mapped labels. Unmapped labels warn and are omitted from `provider_fields`
  while the original evidence remains in `roadmap_fields` and `body_markdown`.
- Known external resources come from `existing_remote` in the mapping config or
  from the manifest. They influence status/action classification only; they do
  not authorize live provider reads or writes.

Provider mapping config shape:

```json
{
  "provider": "linear",
  "scope_type": "portfolio",
  "scope_id": "portfolio",
  "target": {
    "team": "linear-team-key",
    "project": "optional-project-key",
    "cycle": "optional-cycle-key"
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
      "remote_refs": [
        {
          "remote_id": "optional-provider-id",
          "remote_url": "optional-provider-url"
        }
      ]
    }
  }
}
```

Common JSONL record schema. Every JSONL line uses these fields; role-specific
objects are nullable where they do not apply. Markdown is a rendered view, not
the only carrier of required evidence.

Required common fields:

- `schema_version`, `generated_at`, `provider`, `scope_type`, `scope_id`,
  `role`, `roadmap_id`, `title`, `body_markdown`, `overview_fields`,
  `roadmap_fields`, `provider_fields`, `source`, `provider_target`,
  `mapping_hash`, `relation`, `content_hash`, `status`, and `action`.
- `source` always has `path`, `content_hash`, and `anchors`; overview records
  use an empty `anchors` list.
- `overview_fields` is required for overview records and `null` for child
  records.
- `roadmap_fields` is required for child records and uses nullable values only
  for overview records.
- `provider_fields.target` is required on every record.

```json
{
  "schema_version": 1,
  "generated_at": "2026-06-17T00:00:00Z",
  "provider": "linear",
  "scope_type": "portfolio",
  "scope_id": "portfolio",
  "role": "overview",
  "roadmap_id": "overview:portfolio:portfolio",
  "title": "Roadmap export - <goal or source>",
  "body_markdown": "...",
  "overview_fields": {
    "goal": "Roadmap - portfolio",
    "scope_type": "portfolio",
    "scope_id": "portfolio",
    "exported_item_count": 3,
    "blocked_item_count": 1,
    "provider_target": "linear team linear-team-key",
    "generated_at": "2026-06-17T00:00:00Z",
    "source_path": ".idea-to-ship/roadmap.md"
  },
  "roadmap_fields": {
    "status": null,
    "work_type": null,
    "evidence_class": null,
    "confidence": null,
    "source_anchors": [],
    "rationale": "portfolio overview",
    "release_gate": null,
    "evidence_required": null,
    "dependencies": null,
    "risk": null,
    "owner": "Unassigned",
    "decision_owner": "None"
  },
  "provider_fields": {
    "target": {"team": "linear-team-key"},
    "labels": ["roadmap", "idea-to-ship"],
    "assignee": null
  },
  "source": {
    "path": ".idea-to-ship/roadmap.md",
    "content_hash": "sha256:...",
    "anchors": []
  },
  "provider_target": "sha256:...",
  "mapping_hash": "sha256:...",
  "relation": null,
  "content_hash": "sha256:...",
  "status": "new",
  "action": "create"
}
```

Child record shape:

```json
{
  "schema_version": 1,
  "generated_at": "2026-06-17T00:00:00Z",
  "provider": "gitlab",
  "scope_type": "portfolio",
  "scope_id": "portfolio",
  "role": "child",
  "roadmap_id": "ITS-ROADMAP-023",
  "title": "[ITS-ROADMAP-023] Export idea-to-ship roadmaps to external PM issue lists",
  "body_markdown": "...",
  "overview_fields": null,
  "roadmap_fields": {
    "status": "Planned",
    "work_type": "Feature",
    "evidence_class": "Explicit",
    "confidence": "High",
    "source_anchors": ["idea-to-ship/templates/roadmap-item-schema.md:3-36"],
    "rationale": "Why Next: ...",
    "release_gate": "entry criteria; exit criteria; evidence required; no-go conditions",
    "evidence_required": "fixture output and review artifact",
    "dependencies": "None",
    "risk": "medium - parser drift can drop required fields",
    "owner": "Unassigned",
    "decision_owner": "None"
  },
  "provider_fields": {
    "target": {"project_path": "group/project"},
    "labels": ["roadmap", "type::feature", "risk::medium"],
    "assignee": null
  },
  "source": {
    "path": ".idea-to-ship/roadmap.md",
    "content_hash": "sha256:...",
    "anchors": ["idea-to-ship/templates/roadmap-item-schema.md:3-36"]
  },
  "provider_target": "sha256:...",
  "mapping_hash": "sha256:...",
  "relation": {
    "overview_id": "overview:portfolio:portfolio",
    "kind": "child-of-overview"
  },
  "content_hash": "sha256:...",
  "status": "new",
  "action": "create"
}
```

Manifest shape:

```json
{
  "schema_version": 1,
  "generated_at": "2026-06-17T00:00:00Z",
  "scope_type": "portfolio",
  "scope_id": "portfolio",
  "source": {
    "path": ".idea-to-ship/roadmap.md",
    "content_hash": "sha256:..."
  },
  "provider": "linear",
  "provider_target": "sha256:...",
  "mapping_hash": "sha256:...",
  "target": {
    "team": "linear-team-key",
    "project": "optional-project-key",
    "cycle": "optional-cycle-key"
  },
  "overview": {
    "roadmap_id": "overview:portfolio:portfolio",
    "content_hash": "sha256:...",
    "remote_refs": [],
    "status": "new",
    "action": "create"
  },
  "items": {
    "ITS-ROADMAP-023": {
      "role": "child",
      "content_hash": "sha256:...",
      "remote_refs": [
        {
          "remote_id": "LIN-123",
          "remote_url": "https://linear.app/example/issue/LIN-123/example"
        }
      ],
      "status": "skipped-existing",
      "action": "reuse"
    }
  },
  "blocked": {
    "ITS-ROADMAP-999": {
      "reason": "missing source anchors"
    }
  },
  "conflicts": {
    "duplicate_remote_refs": []
  }
}
```

Manifest merge precedence and classification:

| Inputs | Status | Action | Rule |
|---|---|---|---|
| No manifest entry and no `existing_remote` entry | `new` | `create` | Emit a local create instruction. |
| Manifest or mapping has one remote ref for same provider, scope type, scope ID, and target; content hash same | `skipped-existing` | `reuse` | Do not emit a duplicate create instruction. |
| Manifest or mapping has one remote ref for same provider, scope type, scope ID, and target; content hash changed | `changed` | `review-update` | Emit local update/review instructions only, never a duplicate create instruction. |
| Manifest entry has no remote ref; content hash same | `unchanged` | `create` | This is only a repeated local export. Keep the same local create instruction because no external resource is known to exist. |
| Manifest entry has no remote ref; content hash changed | `changed` | `create-or-review` | User has not supplied remote state; output remains local and reviewable. |
| Manifest provider, scope type, scope ID, target, source path, or mapping hash conflicts with current inputs | `needs-user` | `halt` | Hard fail before final artifacts; retry by choosing the intended manifest/mapping or output dir. |
| More than one remote ref for one roadmap ID, or one remote ref reused by multiple roadmap IDs | `needs-user` | `halt` | Hard fail; retry by correcting manifest or mapping data. |

The merge reads manifest data first, then overlays `existing_remote` entries
from the mapping file only when they match the same provider, scope type, scope
ID, target, and source path. Any disagreement between the two sources is a
`needs-user` hard fail; the script never chooses by title.

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
- Required structured `roadmap_fields` on every child record for FR-6 evidence.
- Required structured `provider_fields.target` on every record.
- Provider target identity hash and mapping hash on JSONL records and manifest.
- Stable source identity (`scope_type` and `scope_id`) on JSONL records and
  manifest. Overview IDs use `overview:<scope_type>:<scope_id>`.
- Status values: `new`, `unchanged`, `changed`, `skipped-existing`, `conflict`,
  `needs-user`, `blocked`.
- Action values: `create`, `reuse`, `review-update`, `create-or-review`,
  `halt`.
- Markdown and JSONL are required outputs; CSV is additive only.

### Parser Strategy

Use a narrow, schema-aware parser rather than a broad markdown parser:

- Detect generated roadmap markers when present and parse inside the generated
  section first.
- Track the current top-level roadmap section for every `### ITS-... - <title>`
  block before deciding eligibility.
- Default executable sections are only `## Now`, `## Next`, `## Later`, and
  lane-item blocks nested under `## Milestones`.
- `## Candidate Backlog`, Candidate Brief `Candidate Work`, and other
  candidate sections are non-executable by default.
- Approved candidates are executable only when all of these are true:
  `--include-approved-candidates` is set, the candidate has a full
  lane-template-equivalent detail block, the block contains the exact approval
  marker `**External Export:** Approved`, and required source anchors are
  concrete.
- Extract required `**Field:**` lines from the lane item template.
- Recognize candidate table rows only as an index; require a detailed item
  block or equivalent required fields before exporting an executable child.
- Treat `Unverified Signals`, `Conflicts`, and `Rejected / Not
  Roadmap-Relevant` sections as non-executable sources.
- Block non-executable candidates with explicit reasons such as
  `candidate-not-approved`, `candidate-table-only`, `missing-source-anchors`,
  `weak-confidence`, `unknown-confidence`, `inferred-only`, or
  `rejected-section`.
- Reject duplicate stable IDs.
- Reject child records missing required fields from FR-6.

This avoids adding dependencies while still tying parsing to the documented
roadmap item schema.

### Determinism And Hashing

Deterministic output is a first-class contract:

- Normalize all source and generated text to UTF-8 with LF line endings before
  parsing or hashing.
- Sort JSON object keys and use compact separators when computing hashes.
- Preserve source order for eligible lane items; overview is always the first
  JSONL record; blocked items follow source order in Markdown.
- Compute `source.content_hash` from normalized source roadmap bytes.
- Compute `mapping_hash` from provider, scope type, scope ID, source path,
  target, assignee mappings, label mappings, and relation mode. Exclude
  `existing_remote`, output format toggles such as `--csv`, and generated
  timestamps because they affect artifacts or retry classification, not provider
  mapping identity.
- Compute each record `content_hash` from provider, scope type, scope ID, role,
  roadmap ID, title, canonical body, `overview_fields` without
  `generated_at`, `roadmap_fields`, `provider_fields`, and relation. Exclude
  `generated_at`, `status`, `action`, warnings, remote references, and output
  format toggles.
- Build canonical body by normalizing `body_markdown` and replacing every
  generated timestamp fragment with a fixed placeholder before hashing. The
  rendered Markdown/JSONL body may still contain the real `generated_at` value.
- Compute `provider_target` from provider, scope type, scope ID, and required
  target fields.
- Fixtures pass `--generated-at` or `SOURCE_DATE_EPOCH` so timestamp fields are
  stable. Hashes never include generated timestamps, and a fixture must prove
  that changing only `generated_at` changes rendered timestamps but not
  `content_hash`.

### Failure Modes & Handling

- Missing source roadmap: exit `2` with usage/setup guidance.
- Unsupported provider or output flag: exit `2`.
- Missing required provider target mapping: exit `1`, name the provider, target
  field, and retry path (`team` for Linear, `project_path` for GitLab).
- Ambiguous provider mapping, manifest provider/scope type/scope ID/source
  path/target mismatch, or mapping-hash conflict: exit `1` as `needs-user` and
  write no final artifacts.
- Missing required item fields: exit `1`, print item ID and missing fields, and
  write no final importable artifacts.
- Duplicate stable IDs: exit `1`, print all conflicting IDs and source
  locations.
- Weak or unverified item: exclude from executable output and list under
  blocked/skipped items.
- Missing optional assignee/project/milestone/cycle: warn if provider output
  remains valid.
- Existing manifest maps a roadmap ID to a different provider, scope type,
  scope ID, source path, or target: exit `1` as `needs-user`.
- Existing manifest has same roadmap ID and same content hash: mark
  `unchanged` with `create` when no remote ref exists, or `skipped-existing`
  with `reuse` when a remote ref exists. Only remote-backed entries suppress
  local create instructions.
- Existing manifest has same roadmap ID, a remote ref, and different content
  hash: mark `changed` with `review-update` and emit only local update/review
  instructions, not a duplicate create action.
- Existing manifest has same roadmap ID, no remote ref, and different content
  hash: mark `changed` with `create-or-review` because no external resource is
  known to exist.
- Two existing remote IDs for one roadmap ID: exit `1` as `needs-user`.
- Same remote ID reused by two roadmap IDs: exit `1` as `needs-user`.
- Parsed item count exceeds `--max-items` or rendered output exceeds
  `--max-output-bytes`: exit `1`, print the configured limit and a retry path
  to narrow scope or raise the explicit limit, and write no final artifacts.
- Atomic write failure: exit `1`, leave previous artifacts intact.

Every exit `1` hard failure prints a `Retry:` line naming the exact roadmap
field, mapping key, manifest entry, or output directory to fix before rerun.

### Atomic Write Transaction

All final outputs are generated in memory before any publish step. `--dry-run`
executes parsing, validation, hashing, and manifest classification, prints the
summary, and writes nothing.

Publish algorithm:

1. Create a temporary directory under the same parent as `--output-dir` so
   renames stay on one filesystem.
2. Render every requested output file into the temp directory.
3. Validate the rendered JSONL and manifest by reading the temp files back.
4. Build a publish journal listing every target path, whether it existed before
   publish, and its rollback path if present.
5. Move current output files that will be replaced into a rollback directory;
   record absence markers for targets that did not previously exist.
6. Publish new files with `os.replace`, using a deterministic order:
   `roadmap-export.md`, `issues.jsonl`, optional `issues.csv`, then
   `manifest.json` last as the commit marker.
7. If any publish step fails before `manifest.json` is replaced, replay the
   journal in reverse: restore old files for existed-before targets, unlink
   newly-created outputs for absent-before targets, and remove temp files.
8. If rollback itself fails, exit `1` with the rollback directory path and a
   recovery message; the old manifest remains the authoritative state because
   it was replaced last.
9. On success, remove temp and rollback directories.

Markdown preservation still applies before publish: if `roadmap-export.md`
contains generated markers, replace only the generated region; if it has human
content and no generated markers, publish `roadmap-export.draft.md` instead of
overwriting the human-owned file.

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
- Overview record/body includes roadmap goal, scope type, scope ID, exported
  item count, provider target, generated timestamp, and source roadmap path.
- Roadmap with weak/unverified items -> blocked section, no executable child.
- Candidate Backlog item without `**External Export:** Approved` -> blocked
  `candidate-not-approved`.
- Approved candidate with the marker, full lane-template-equivalent fields, and
  concrete anchors -> executable child only when
  `--include-approved-candidates` is set.
- Missing required field -> exit `1`, no final output.
- Missing Linear `team` or GitLab `project_path` -> exit `1` with retry
  guidance and no final output.
- Legacy or future `--formats csv` / `--formats jsonl` attempts -> exit `2`
  rather than disabling required Markdown or JSONL output.
- Missing optional assignee/project -> warning, successful output.
- JSONL child record contains structured `roadmap_fields` for every FR-6 field
  and structured `provider_fields.target`.
- JSONL overview and child records share the common `source` shape and
  `generated_at` field.
- Existing manifest with remote ID -> no duplicate create action.
- Existing manifest without remote ID and same content hash -> unchanged local
  export still emits the create instruction.
- Existing manifest with changed content -> changed/update instruction.
- Manifest provider/scope type/scope ID/source path/target conflict ->
  `needs-user` hard fail.
- Duplicate remote IDs for one roadmap ID, or one remote ID reused by multiple
  roadmap IDs -> `needs-user` hard fail.
- Repeated run with identical inputs -> stable JSONL ordering and content
  hashes except timestamp metadata.
- Repeated run with fixed `--generated-at` -> byte-stable artifacts except
  paths under temporary directories.
- Repeated run where only `--generated-at` changes -> rendered timestamps change
  but `content_hash` values and rerun classification stay stable.
- Rerun with only `--csv` toggled -> content hashes, `mapping_hash`, and rerun
  classification stay stable while `issues.csv` is added or omitted.
- Existing markdown export with human content outside markers -> preservation
  or draft fallback.
- Over-budget item count or output bytes -> exit `1` with retry guidance and no
  final output.
- Publish failure injected after each publish step before `manifest.json`
  replacement -> rollback keeps previous artifacts authoritative and deletes
  newly-created outputs that had no prior version.

Release-gate integration:

- `tests/idea-to-ship-roadmap-export-fixtures.py` runs behavior fixtures.
- `tests/idea-to-ship-eval-fixtures.sh` invokes both existing contract fixtures
  and the new export behavior fixture.
- `tests/idea-to-ship-eval-fixtures.py` adds contract invariants for
  roadmap export documentation.
- `scripts/release-gate.sh` should add
  `tests/idea-to-ship-roadmap-export-fixtures.py` to the staged/working trigger
  path list. The shell wrapper owns execution, but the release gate must still
  notice edits to the new fixture file itself.

## Staged Implementation Plan

1. **Stage 1 - Provider-neutral exporter core**: Add
   `idea-to-ship/scripts/roadmap_export.py` with section-aware source parsing,
   item validation, structured internal issue schema, overview/child
   construction, canonical hashing, fixed timestamp seam, required Markdown and
   JSONL outputs, manifest output, safety limits, and focused behavior fixtures.
   No skill docs yet. Verify the script can export a temp roadmap fixture
   without provider API calls.
2. **Stage 2 - Linear/GitLab mappings and markdown report**: Add first-class
   Linear/GitLab required-target validation, mapping renderers, generated
   markdown export artifact, blocked/skipped sections, warning handling,
   manifest rerun classification, remote-ref conflict detection, multi-file
   publish transaction, optional CSV output behind `--csv`, and marker/draft
   preservation behavior. Verify idempotency and hard-fail scenarios.
3. **Stage 3 - Roadmap skill integration and docs**: Update
   `$idea-to-ship:roadmap` instructions, templates, README/SKILLS entries if
   public, and fixture contracts. Wire the export fixture through
   `tests/idea-to-ship-eval-fixtures.sh`; update `scripts/release-gate.sh`
   staged trigger paths for the new fixture; run
   `bash tests/idea-to-ship-eval-fixtures.sh` and
   `scripts/release-gate.sh --mode all --strict`.

Each stage is independently shippable: Stage 1 provides a hidden deterministic
helper, Stage 2 provides complete local export artifacts, and Stage 3 exposes
the workflow safely to users.

## Open Questions

- Should provider mapping config live only in an explicit JSON file, or should
  the CLI also accept simple flags for common optional fields?
