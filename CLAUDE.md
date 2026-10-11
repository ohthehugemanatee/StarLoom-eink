# CLAUDE.md — repo-wide rules for agents

e-ink renderer sidecar for data in a self-hosted [StarLoom](https://github.com/jamesread/StarLoom) instance.

## Workflow

IMPORTANT: every change follows this workflow; do not skip steps.

- **Decompose first.** Break a large request into the smallest set of atomic GitHub Issues, as a numbered list with a sequencing graph (`#3 blocks #4,#5`; `#6,#7 parallel after #4`). Atomic means one testable acceptance criterion, and its PR(s) can merge without simultaneously requiring another Issue's PR.
- **Spec-first, per Issue.** Before any diff: intent, target area of code, expected bebehavior.
- **Test-first, and review the tests against the spec.** Add the failing check before the implementation. Review tests for coverage and effectiveness (would they catch a regression?) before writing code, before commit, and again at PR review.
- **Extend the test frameworks when they don't cover the change.** and changes to testing belong in the spec. "We don't have a test for this kind of thing" is not an excuse to skip test-first.
- **PR size.** Warn at 200 LOC changed (added + removed, non-generated); at 400 LOC the PR must be split before merge. Propose the split in the same sequencing-graph format.
- **Constrain scope; ask before straying.** Smallest diff that satisfies the spec, no adjacent refactors. Do not modify files outside the Issue's declared scope without asking. If the operator expands scope mid-flight, name the expansion, propose it as a new Issue with its place in the graph, and finish the original.
- **Prefer upstream components over scripted glue.** 
- **Run tests before commit; fix failures rather than commit around them.** Never commit with known-failing tests, never silence a test or add to an exception file to make CI green, never `--no-verify`.
- **No scheduled checkins.** The integration will alert you on changes in PRs. Trust it. The operator will ping you if it doesn't. 

## Coding behavior

- **Think before coding.** State assumptions; present multiple interpretations rather than picking one silently; stop and ask when something is unclear.
- **Simplicity first.** Minimum code and config that solves the Issue: no speculative abstractions, no unrequested configurability, no error handling for impossible scenarios.
- **Comment budget: approximately 5 words per comment, maximum.** A comment states a non-obvious invariant, an external workaround, or a constraint — nothing else, and one line where one line will do. Never narrate the incident, Issue or PR behind the change; that belongs in the commit message and PR description. If deleting a comment would not leave a future reader confused, delete it rather than trim it. Docstrings and file headers get the same bar.
- **Surgical changes.** Don't improve adjacent code, comments or formatting; match existing style; remove only the imports, vars and functions your change orphaned, and mention other dead code rather than deleting it. "Match existing style" covers formatting and idiom, not comment volume: the budget above wins over the neighbouring file.
- **Goal-driven execution.** For a multi-step task, state a short plan with a verify step per line.
- **NEVER** commit plaintext secrets.

## Commit + PR etiquette

- Imperative mood, lowercase start, short subject; `feat:` / `fix:` prefix optional.
- Bot commits carry `[Claude]`; 
- Open PRs as draft until self-review and local tests pass.

## Documentation style

- **Documentation style is terse, operator-first.** No marketing prose, no emojis, no "in conclusion" sections.
- **Run every piece of prose through the `avoid-ai-writing` skill** (voice `technical`, context `docs`) before it merges. The skill lives in the operator's Claude profile; an agent without it reads <https://raw.githubusercontent.com/conorbronsdon/avoid-ai-writing/refs/heads/main/SKILL.md>.
- **A change carries its doc fix.** Always check the `*.md` in the affected directory and the repo root; a doc that needs updating is a bug, and the fix ships in the same PR. "Needs updating" means the existing text is now factually wrong, or contradicts the new behavior. It does not mean the topic could carry more explanation, more operational detail, or a note on how the bug was found; those go in the PR description if anywhere.
- **Outside `adr/`, docs describe the current implementation only.** Explain reasoning only where an aspect would otherwise be misread. Do not narrate how the current state was reached.
- **ADRs only record decisions that changed code.** A changed configuration does not merit an ADR. 
- **Drafts stay out of the codebase, so they stay out of the documentation.** With squash-merge a branch's intermediate states are not history. If a PR took three attempts to pass, only the third merged and gets documented in the codebase. The other two may be documented in the Issue or PR thread, but nowhere in the repo.
