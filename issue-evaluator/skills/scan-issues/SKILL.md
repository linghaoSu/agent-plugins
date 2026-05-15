---
name: scan-issues
description: Scan the current project for high-value unattended issues (unassigned or assigned without PR) using an expanding time window, read-only — never modify issues
argument-hint: "[initial-window, e.g. 2w, 1m]"
allowed-tools: [Read, Glob, Grep, Bash, Agent]
---

# Scan High-Value Issues

Scan the current repository for high-value **unattended** issues — those that are unassigned, or assigned but have no associated pull request. If none are found within the initial time window, the window doubles repeatedly until results are found or the window reaches one year.

## CRITICAL CONSTRAINT

**This skill is strictly read-only.** It does not modify GitHub, git state, or
repo files, and it writes no local report artifact by default; all results are
returned in the conversation. During the entire execution, you MUST NOT:
- Comment on any issue
- Close, reopen, or edit any issue
- Add or remove labels on any issue
- Assign or unassign any issue
- Create any issue
- Perform any write operation via `gh issue edit`, `gh issue comment`, `gh issue close`, `gh issue reopen`, `gh issue create`, or equivalent `gh api` calls with POST/PATCH/PUT/DELETE methods on issue endpoints

The ONLY permitted `gh` operations are read-only queries: `gh issue list`, `gh issue view`, and GET requests via `gh api`.

Before reading large issue/comment sets, apply `../../WORKFLOW-CONTRACTS.md`
**Output, Token, And Error Contract**. Default budget: 100 issues per search
window, 50 comments per issue, and 15 issues in the final table. If more data
is available, prioritize higher reaction count, maintainer-endorsed labels,
recent activity, and missing active PR ownership. Set `truncated: true`, state
what was omitted, and provide the continuation query in `next_action`.

## Arguments

The user provided: `$ARGUMENTS`

This is an **optional** initial time window (e.g. `2w`, `1m`, `3d`). If not provided, default to **2 weeks**.

Supported formats:
- `Nd` — N days
- `Nw` — N weeks
- `Nm` — N months

## Workflow

### Step 1: Determine Repository Info

```bash
gh repo view --json owner,name,url --jq '"\(.owner.login)/\(.name)"'
```

If this fails, abort with an error — this skill requires a GitHub remote.

### Step 2: Parse Initial Time Window

Parse `$ARGUMENTS` into a number of days. Defaults:
- Not provided → 14 days
- `2w` → 14 days
- `1m` → 30 days
- `3d` → 3 days

Set `current_window_days` to this value.
Set `max_window_days` to 365 (one year).

### Step 3: Expanding Window Search Loop

Repeat the following until high-value issues are found OR `current_window_days > max_window_days`:

1. **Calculate the date threshold:**
   ```bash
   date -v-${current_window_days}d +%Y-%m-%d   # macOS
   # or: date -d "${current_window_days} days ago" +%Y-%m-%d   # Linux
   ```

2. **Fetch open issues created since that date:**
   ```bash
   gh issue list --state open --limit 100 --json number,title,labels,createdAt,updatedAt,comments,reactionGroups,author,milestone,assignees --search "created:>=${date_threshold}"
   ```
   If `--search` with date filter isn't supported, use:
   ```bash
   gh api "repos/{owner}/{repo}/issues?state=open&since=${date_threshold}T00:00:00Z&per_page=100&sort=created&direction=desc" \
     --jq '.[] | select(.pull_request == null) | {number, title, labels: [.labels[].name], created_at, updated_at, comments, reactions, assignees: [.assignees[].login]}'
   ```

3. **Filter and classify PR association status:**

   The goal is to surface issues that **no one is effectively working on**. For each issue from step (2), check PR association and record its status for scoring.

   **3a. Timeline cross-reference check:**
   ```bash
   gh api "repos/{owner}/{repo}/issues/<number>/timeline" --jq '[.[] | select(.event == "cross-referenced" and .source.issue.pull_request != null) | .source.issue | {number, state: .state, pull_request}]'
   ```

   **3b. Keyword PR search fallback** — for issues with no timeline cross-references:
   ```bash
   gh pr list --state all --search "in:title in:body <issue-number>" --limit 5 --json number,state,mergedAt
   ```

   **3c. Classify each issue into one of these PR association categories:**

   | Assigned? | PR Status | Category | Action |
   |---|---|---|---|
   | Yes | Open PR exists | **Actively worked on** | **Skip** — someone is assigned and has an open PR |
   | Yes | All PRs closed (not merged) | **Abandoned attempt** | Keep |
   | Yes | No PR at all | **Forgotten assignment** | Keep |
   | No | Open PR exists | **Unowned with PR** | Keep — PR exists but no assignee; the PR may be stale, from an external contributor, or lacking review |
   | No | All PRs closed (not merged) | **Failed attempt, no owner** | Keep |
   | No | No PR at all | **Completely unattended** | Keep |

   The **only** combination that is skipped is: assigned + active open PR. All other combinations are kept and their category is recorded for use in scoring (step 5).

4. **Deep evaluation: Content quality + Maintainer signal analysis**

   For every issue that passed step (3) — whether assigned or unassigned — perform a deeper evaluation. This step can be parallelized across issues using agents.

   **4a. Identify maintainers and their permission levels:**

   First, determine who the repo maintainers are. Fetch collaborators with their roles:
   ```bash
   gh api "repos/{owner}/{repo}/collaborators?per_page=100" --jq '.[] | {login: .login, role: .role_name}'
   ```
   If this requires admin access and fails, fall back to the `author_association` field on each comment (available without special permissions). The hierarchy from highest to lowest:
   1. **OWNER** — repository owner
   2. **MEMBER** — organization member
   3. **COLLABORATOR** — invited collaborator
   4. **CONTRIBUTOR** — has merged PRs
   5. **NONE** — external / first-time commenter

   **4b. Fetch issue body and comments:**
   ```bash
   gh issue view <number> --repo <owner/repo> --json body,comments
   ```

   **4c. Evaluate issue content quality:**

   Assess the issue body for the following signals:

   | Content Signal | Assessment |
   |---|---|
   | Clear problem statement with expected vs actual behavior | High quality |
   | Includes reproduction steps or a minimal example | High quality |
   | References specific code paths, files, or line numbers | High quality |
   | Contains logs, stack traces, or screenshots | Medium quality |
   | Vague description ("X doesn't work", "please add Y") with no detail | Low quality |
   | Only a title with empty or near-empty body | Very low quality |

   Assign a **content quality score**:
   - High quality (clear, reproducible, specific): **+3**
   - Medium quality (some detail but incomplete): **+1**
   - Low quality (vague, no actionable info): **0**
   - Very low quality (empty or near-empty): **-2**

   **4d. Analyze maintainer comments:**

   Scan the issue comments to find those from maintainers (OWNER, MEMBER, COLLABORATOR). Among all maintainer comments, use the **highest-level** maintainer's stance as the primary signal. If multiple comments exist from the same top-level maintainer, use their **most recent** comment.

   Classify the maintainer's sentiment toward the issue:

   | Maintainer Sentiment | Weight Multiplier | Examples |
   |---|---|---|
   | **Endorsed / confirmed** — maintainer acknowledges the issue, says it should be fixed, labels it, or asks for a PR | **×1.5** | "This is a valid bug", "PRs welcome", "Good catch", "We should fix this" |
   | **Neutral / informational** — maintainer comments but doesn't take a clear stance | **×1.0** | "Can you provide more info?", "Interesting", triaging questions |
   | **No maintainer comment** — no maintainer has weighed in | **×0.8** | (silence) |
   | **Deprioritized / wontfix leaning** — maintainer signals low priority or pushback | **×0.5** | "Not a priority right now", "By design", "Unlikely to change", "Duplicate of..." |

   If there are comments from multiple maintainers with **conflicting** stances, use the highest-level maintainer's stance. If they are the same level, use the most recent comment.

   **4e. Detect claim/self-assignment in comments:**

   Scan **all** comments (not just maintainer comments) for signs that someone has recently claimed the issue but hasn't been formally assigned yet. Look for patterns such as:
   - "I'll take this", "I'd like to work on this", "I'm working on this"
   - "Can I be assigned?", "Can this be assigned to me?", "Assign me please"
   - "I'll submit a PR", "Working on a fix", "I'll send a PR"
   - "Let me handle this", "I'd like to pick this up", "Claiming this"
   - Maintainer replies like "Go ahead", "It's yours", "@user sure"

   **Freshness matters.** Classify the claim:

   | Claim Status | Score Modifier | Rationale |
   |---|---|---|
   | **Recent claim (within 14 days)** — someone commented claiming the issue and no sign of abandonment | **×0.2** | Respect open-source etiquette — someone just claimed it, give them time to deliver |
   | **Stale claim (15–60 days ago)** — claimed but no follow-up PR or progress update since | **×0.7** | Claimed but possibly abandoned; still worth surfacing cautiously |
   | **Very stale claim (60+ days ago)** — claimed long ago with zero follow-up | **×1.0** (no penalty) | Effectively abandoned — fair game |
   | **No claim detected** | **×1.0** (no penalty) | No one has expressed intent |

   This modifier is applied **after** the maintainer sentiment multiplier in the final score calculation (step 5). It stacks multiplicatively:
   ```
   final_score = round((base_score + content_quality_score) × maintainer_weight × claim_modifier)
   ```

   > **Open-source etiquette principle**: If someone has publicly expressed intent to work on an issue, we should respect that by deprioritizing the issue in our results — even if they haven't been formally assigned. This avoids duplicating effort and respects community norms.

5. **Score each remaining issue for "high value":**

   Compute a **base score** from quantitative signals:

   | Signal | Points |
   |---|---|
   | Total reactions (thumbs-up, heart, hooray, etc.) >= 5 | +3 |
   | Total reactions >= 2 | +1 |
   | Comments >= 10 | +3 |
   | Comments >= 5 | +2 |
   | Comments >= 3 | +1 |
   | Has label matching `bug`, `critical`, `high-priority`, `priority/high`, `P0`, `P1`, `severity/high`, `important` (case-insensitive) | +3 |
   | Has label matching `enhancement`, `feature`, `feature-request` (case-insensitive) | +1 |
   | Has a milestone assigned | +1 |
   | **PR association signals (from step 3c):** | |
   | Completely unattended (unassigned, no PR) | +1 |
   | Forgotten assignment (assigned, no PR) | +2 |
   | Forgotten assignment 30+ days (assigned 30+ days, no PR) | +3 |
   | Unowned with open PR (unassigned but has open PR) | +2 |
   | Unowned with stale open PR (open PR with no activity for 30+ days) | +3 |
   | Failed attempt, no owner (unassigned, all PRs closed not merged) | +2 |
   | Abandoned attempt (assigned, all PRs closed not merged) | +2 |

   Then add the **content quality score** from step 4c.

   Then apply the **maintainer sentiment multiplier** (step 4d) and **claim modifier** (step 4e):

   ```
   final_score = round((base_score + content_quality_score) × maintainer_weight × claim_modifier)
   ```

   An issue is considered **high-value** if its `final_score` is **>= 4**.

   **Adaptive threshold:** If the repo has very few issues (< 10 total open), lower the threshold to >= 2 to surface the most relevant ones even in low-activity repos.

6. **Evaluate results:**
   - If high-value unattended issues are found → proceed to Step 4
   - If NO high-value unattended issues are found:
     - Report: "No high-value unattended issues found in the last `current_window_days` days. Expanding search window..."
     - Set `current_window_days = current_window_days * 2`
     - If `current_window_days > max_window_days`, set `current_window_days = max_window_days` and run **one final search** at the max window before giving up
     - Repeat from (1)

### Step 4: Rank and Present Results

Sort high-value issues by `final_score` (descending), then by maintainer weight (descending), then by reactions (descending).

Present the top results (up to 15) in this format:

```markdown
## High-Value Unattended Issues — <owner>/<repo>

**Search window**: last <N> days (since YYYY-MM-DD)
**Issues scanned**: <count>
**High-value unattended issues found**: <count>
**Contract**:
status: success | needs_user | terminal | degraded
mode: scan
inputs_resolved: <repo + search window>
outputs_written: []
skipped: <issues skipped and why>
errors: <retryable | terminal | needs_user | degraded entries>
next_action: <one command or query>
truncated: true | false

### Top Issues

| # | Score | Title | Labels | Status | Claim | Content | Maintainer Signal | Reactions | Comments | Created |
|---|-------|-------|--------|--------|-------|---------|-------------------|-----------|----------|---------|
| [#123](url) | 9 | Issue title... | `bug`, `P0` | Unassigned, no PR | — | High | Endorsed by @admin (OWNER) ×1.5 | 12 | 25 | 2026-03-15 |
| [#456](url) | 7 | Another issue... | `enhancement` | Unassigned, open PR #789 (stale 60d) | — | Medium | No maintainer comment ×0.8 | 3 | 8 | 2026-02-10 |
| [#780](url) | 6 | Third issue... | `bug` | Assigned 45d, no PR | — | High | Neutral ×1.0 | 5 | 4 | 2026-01-20 |
| [#900](url) | 2 | Fourth issue... | `bug` | Unassigned, no PR | @dev claimed 3d ago ×0.2 | High | Endorsed ×1.5 | 8 | 6 | 2026-03-01 |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

### Quick Summary

For each top issue (up to 5), provide a 1-2 sentence summary explaining the issue, its content quality, and the maintainer stance:

1. **#123 — Title**: <brief summary of the issue>. _High-quality report with repro steps. OWNER @admin endorsed: "PRs welcome". Unassigned with no PR, 12 reactions, open 3 months._
2. **#456 — Title**: <brief summary>. _Medium-quality description. No maintainer response. Unassigned but has open PR #789 (stale 60 days, no review activity)._
3. **#780 — Title**: <brief summary>. _High-quality report. Neutral maintainer response. Assigned to @user 45 days ago but no PR opened._
4. **#900 — Title**: <brief summary>. _High-quality report. OWNER endorsed. However, @dev claimed 3 days ago (×0.2) — score heavily reduced out of open-source etiquette._
5. ...
```

### Step 5: If No Issues Found After Full Expansion

If the search reached the one-year maximum and still found no high-value issues:

```markdown
## Scan Complete — <owner>/<repo>

No high-value unattended issues found within the past year.

- **Total open issues scanned**: <count>
- **Time window expanded to**: 365 days

This may indicate:
- All significant issues have assignees actively working on them
- The project has low issue activity
- Issues are resolved quickly
- The project uses a different issue tracker
```

## Notes

- **Read-only**: This skill MUST NOT perform any write operations on issues. This is a hard constraint — violation would be a critical error.
- Use `gh` CLI for all GitHub interactions
- The `--search` parameter in `gh issue list` supports GitHub search syntax — prefer it for date filtering when available
- Be mindful of API rate limits — batch requests where possible and avoid fetching reactions for every single issue unless needed for scoring
- For repos with 100+ open issues, prioritize the `gh api` approach with pagination if the first page doesn't cover the window
- The scoring heuristic is intentionally simple — it's a triage tool, not a definitive ranking
