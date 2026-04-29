# Shared Vocabulary — idea-to-ship

Terms used across skills in this plugin. When a skill says one of these,
it means exactly this — not the general industry usage.

## Vertical Slice

A unit of work that cuts through all layers (UI → API → DB → test) and
delivers one observable behavior end-to-end. The opposite of a horizontal
slice, which implements one layer across many features.

**Why it matters:** A vertical slice is independently shippable and
testable. A horizontal slice is neither — it requires other slices to land
before anything works.

## Staged Implementation

Breaking architecture into ordered, independently-shippable stages. Each
stage leaves the system working. Stages are vertical slices of the full
design.

**Rule:** At the end of every stage, the build passes, existing tests pass,
and no feature is half-wired. A user who checked out the repo after stage N
would see a working system (possibly with missing features, but nothing
broken).

## Design Drift

When the implementation silently deviates from `architecture.md` without
updating it. Design drift is a first-class defect — it means the
architecture doc is now a lie.

**Three valid responses to drift:**
1. Fix the implementation to match the design.
2. Update the design to match the implementation, with a documented reason.
3. Note it explicitly in `implementation-log.md` as an accepted deviation.

Silent drift (option 0) is forbidden.

## Deep Module

A module that provides a simple interface but hides significant complexity
behind it. From Ousterhout's *A Philosophy of Software Design*.

**Shallow module** (anti-pattern): interface is nearly as complex as the
implementation — the module doesn't earn its existence. Common symptom:
a "wrapper" class that adds no abstraction, just indirection.

**Deletion test:** Imagine deleting the module. If complexity vanishes, it
was pass-through. If complexity reappears across N callers, it was earning
its keep.

## Seam

A point where you can alter behavior without editing the code under test.
Examples: dependency injection, interface boundaries, environment variables,
feature flags, HTTP interceptors.

Seams are where tests can substitute controlled inputs. A design with no
seams is a design that's hard to test.

## Tracer Bullet

The first vertical slice through a new system — end-to-end, minimal,
working. Its purpose is to prove the architecture works before investing
in breadth.

A tracer bullet is not a prototype or spike — it ships. It's thin but
production-quality.

## Blast Radius

The set of code, features, and users affected if a change goes wrong.
Smaller blast radius = safer to ship = easier to roll back.

When choosing between architectures, prefer the one with the smallest
blast radius that still meets the requirements.

## Falsifiable Hypothesis

A diagnosis or assumption stated in a form that can be **disproved** by a
specific, concrete check. Used in debugging and in reviewing architecture
assumptions.

**Template:** "If X is the cause, then doing Y will produce Z."

If you can't state the prediction, it's a vibe, not a hypothesis. Discard
it and think harder.
