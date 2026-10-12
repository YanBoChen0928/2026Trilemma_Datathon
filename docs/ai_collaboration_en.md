# AI Collaboration Principles — Driver View

> Scope: how Yan-Bo and the AI assistant work together on the Driver View.
> Team-wide rules live in `CONTRIBUTING.md`; engineering rules live in `mvp_implementation_handoff_en.md`.

## 1. Follow the agreed direction

Once the handoff, blueprints, and `CONTRIBUTING.md` are agreed, work follows them. Confirmed decisions are not reopened unless new evidence shows that one would produce a wrong or unsafe result.

## 2. Triage every issue before raising it

Before presenting an issue to the user, the assistant first asks: does this really need the user's decision?

**The assistant resolves it and reports briefly** when the issue:

- does not change the MVP scope, schedule, team ownership, or a confirmed handoff rule; and
- can be handled with a conservative choice (one that never produces a positive legal verdict the data does not support).

The report says what the issue was and how it was handled, in one or two sentences.

**The assistant brings it to the user** when the issue:

- changes the MVP scope or schedule;
- changes or conflicts with a confirmed handoff rule;
- affects other team members' work or files; or
- has no conservative option, so any choice is a product decision.

When an issue is raised, it comes with a recommendation.

## 3. Where records go

The handoff is the main document. Each kind of record has one home:

| Content | Where it goes |
| --- | --- |
| Decisions themselves (rules, scope, UI) | `mvp_implementation_handoff_en.md`, the single engineering source of truth |
| Official sources and interpretations behind parking rules; rule questions that need a decision | `references.md`, Section 5 (status "Open question" while undecided) |
| Reasons for a scope change | `meter_data_decisions_en.md` (for example, item 4) |
| Small issues the assistant resolved itself | The "Implementation notes" of the related item in `references.md` Section 5, or one sentence in the relevant handoff section |

No new documents are created for these records, so that information stays in one place.

## 4. Progress first

Do not overthink or complicate simple things. Build the MVP first. Extensions and edge cases that the MVP does not need are left for stretch work and are not raised during the build.

## 5. Files and git

- The assistant may read any file. It changes files only with the user's approval; the standing approval for recording questions and notes in `references.md` (Section 3 above) is the exception.
- For git, the assistant provides `add`, `commit`, and `push` commands; the user runs them.
