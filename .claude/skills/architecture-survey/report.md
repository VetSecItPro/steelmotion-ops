# /architecture-survey - the HTML report

One self-contained file: `.reports/architecture-survey/SURVEY-<YYYYMMDD-HHMM>.html` in the repo
root (stamp from `TZ=America/Chicago date`). Ensure `.reports/architecture-survey/` is in
`.gitignore` before writing. Open it (`open` on macOS, `xdg-open` on Linux) unless the session is
headless or the operator does not want a browser, and always give the absolute path.

**Inline CSS only, no CSS framework from a CDN.** Optionally Mermaid from
`https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js` for graph-shaped diagrams
(dependencies, call flow); hand-drawn HTML boxes or inline SVG for the rest, and for everything
when the report must work offline. Light and dark via
`prefers-color-scheme`. No em or en dashes anywhere in the text.

## Sections, in order

1. **Verdict.** One line: the top pick, or "no restructuring needed", and the candidate count.
2. **Scope.** Churn window (dates), commit count, top ten files with commit counts, and the
   weak-signal warning if under about 30 commits.
3. **Record check.** Glossary present or not; decision records read; KNOWN candidates with their
   backlog row numbers; candidates dropped because a record already decided them.
4. **Coverage.** Read and skimmed modules by name with line counts and the ranges read; unread
   modules grouped by directory with a count; any unread module in the churn or fan-in top ten
   named.
5. **Candidates**, strongest first, one card each.
6. **Leave alone.** Code that looks suspicious but passes the deletion test or is deliberate, with
   the one-line reason.
7. **Top pick.** Which candidate first and why: cost of change times risk of error, not size.

## Candidate card

| Field | Content |
|---|---|
| Title | in glossary and vocabulary terms ("the guard's freeze handling is shallow across seven closures"), never a class name |
| Rating | `Strong` / `Worth exploring` / `Speculative` badge |
| Status | NEW, KNOWN (backlog row), or REOPENS (decision record, with why) |
| Files | paths with line counts |
| Evidence | churn count, fan-in, and the code fact (quote the line or comment) |
| Friction | why change here is costly or risky today |
| Direction | one or two sentences on which way deepening goes (what would sit behind one seam). **Not** a new interface, class list or file layout |
| Payoff | in locality and leverage terms, and what tests would get easier |
| Before | today's shape: a small diagram when it is a graph (callers, dependencies), one line when it is a count ("restated in 7 files") |

There is no "after" diagram. The after is designed with the operator in the hand-off.

## Writing the report

Keep it short enough to read in five minutes: typically three to six candidates. A survey with
fifteen candidates has not ranked anything. If everything is fine, the report is the scope,
coverage, leave-alone list and a one-line verdict, and that is a good result.
