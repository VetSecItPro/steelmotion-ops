#!/usr/bin/env python3
"""
generate-skill-router.py - regenerate the inventory half of SKILL_ROUTER.md from the
actual filesystem, so the router cannot drift from the skills it routes to.

Why this exists: on 2026-08-27 the hand-maintained router named 31 skills against an
estate of 40. Six entries routed to skills that did not exist; fifteen real skills were
invisible to it, including `repo-bootstrap`. A router that is typed by hand rots, and a
rotted router is worse than none, because it fails silently and confidently.

The judgment sections of SKILL_ROUTER.md (disambiguation, confidence calibration,
announcement format) are hand-written and are preserved untouched. Only the inventory
between the generated markers is replaced.

Run after adding, renaming or deleting any skill:  python3 ~/.claude/generate-skill-router.py
"""
import os, re, sys, datetime

# The folder this script lives in, so a run from a worktree regenerates that worktree's router and
# never the live ~/.claude one.
BASE = os.path.dirname(os.path.abspath(__file__))
ROUTER = os.path.join(BASE, 'standards', 'SKILL_ROUTER.md')
BEGIN = '<!-- BEGIN GENERATED INVENTORY - do not edit by hand, run generate-skill-router.py -->'
END   = '<!-- END GENERATED INVENTORY -->'


def parse_frontmatter(text):
    m = re.match(r'^---\n(.*?)\n---', text, re.S)
    if not m:
        return {}
    out, key, buf = {}, None, []
    for line in m.group(1).split('\n'):
        km = re.match(r'^([a-z_]+):\s*(.*)$', line)
        if km:
            if key:
                out[key] = ' '.join(buf).strip()
            key, buf = km.group(1), [km.group(2)]
        elif key:
            buf.append(line.strip())
    if key:
        out[key] = ' '.join(buf).strip()
    return {k: v.strip().strip('"').strip("'") for k, v in out.items()}


def collect():
    rows = []
    sd = os.path.join(BASE, 'skills')
    for e in sorted(os.listdir(sd)):
        p = os.path.join(sd, e, 'SKILL.md')
        if os.path.isfile(p):
            fm = parse_frontmatter(open(p).read())
            rows.append((fm.get('name', e), 'skills/', fm.get('description', ''), fm.get('when_to_use', '')))
    cd = os.path.join(BASE, 'commands')
    for e in sorted(os.listdir(cd)):
        if not e.endswith('.md'):
            continue
        fm = parse_frontmatter(open(os.path.join(cd, e)).read())
        rows.append((fm.get('name', e[:-3]), 'commands/', fm.get('description', ''), fm.get('when_to_use', '')))
    return rows


def triggers(when):
    """Pull the quoted trigger phrases out of when_to_use; fall back to the raw text."""
    q = re.findall(r'"([^"]+)"', when)
    return ', '.join(f'`{p}`' for p in q[:7]) if q else (when[:110] or '-')


def first_sentence(desc, limit=150):
    s = re.split(r'(?<=[.;])\s', desc)[0] if desc else '-'
    return (s[:limit] + '...') if len(s) > limit else s


def main():
    rows = collect()
    stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    out = [BEGIN, '', f'## Intent to Skill Map', '',
           f'**{len(rows)} skills, generated from the filesystem {stamp}.** '
           f'{sum(1 for r in rows if r[1] == "skills/")} in `~/.claude/skills/`, '
           f'{sum(1 for r in rows if r[1] == "commands/")} in `~/.claude/commands/`. '
           'The two directories are disjoint; both are live. Regenerate with '
           '`python3 ~/.claude/generate-skill-router.py` after any skill is added, renamed or removed.', '',
           '| Skill | Where | What it does | Route to it when the user says |',
           '|---|---|---|---|']
    for name, loc, desc, when in rows:
        d = first_sentence(desc).replace('|', '\\|')
        t = triggers(when).replace('|', '\\|')
        out.append(f'| `/{name}` | {loc} | {d} | {t} |')
    missing = [n for n, _, d, w in rows if not d or not w]
    if missing:
        out += ['', f'**Skills with incomplete frontmatter** (cannot be routed reliably): '
                    + ', '.join(f'`/{m}`' for m in missing)]
    out += ['', END]

    if not os.path.isfile(ROUTER):
        sys.exit(f'ERROR: {ROUTER} not found')
    text = open(ROUTER).read()
    block = '\n'.join(out)

    if BEGIN in text and END in text:
        text = text[:text.index(BEGIN)] + block + text[text.index(END) + len(END):]
    else:
        # First run: replace the hand-written map, keep everything else.
        start = text.index('## Intent')
        nxt = text.index('## Pipeline Triggers')
        text = text[:start] + block + '\n\n---\n\n' + text[nxt:]
    open(ROUTER, 'w').write(text)
    print(f'SKILL_ROUTER.md inventory regenerated: {len(rows)} skills '
          f'({sum(1 for r in rows if r[1] == "skills/")} skills/, '
          f'{sum(1 for r in rows if r[1] == "commands/")} commands/)')
    if missing:
        print('  incomplete frontmatter: ' + ', '.join(missing))


def check():
    """--check: fail if any HAND-WRITTEN section names a skill that does not exist.

    Suggested 2026-08-27, after a near-miss where the hand-written
    flag reference was nearly lost to a pointer claiming it lived in the generated
    inventory. A comment saying a section is "preserved across regeneration" is a claim,
    not a check. This is the check.

    Its own lane found the same shape from the other side the same day: a guard whose
    docstring correctly described what it prevents, sitting downstream of a filter that
    discarded exactly the cases it was written to catch. An accurate description and an
    empty path look identical from the outside.
    """
    have = {n for n, _, _, _ in collect()}
    text = open(ROUTER).read()
    hand = text[:text.index(BEGIN)] + (text[text.index(END) + len(END):] if END in text else '')
    named = set(re.findall(r'`/([a-z][a-z0-9-]{2,})`', hand))
    ghost = sorted(n for n in named if n not in have)
    if ghost:
        print(f'FAIL: hand-written sections of SKILL_ROUTER.md name {len(ghost)} skill(s) '
              f'that do not exist: ' + ', '.join(f'/{g}' for g in ghost), file=sys.stderr)
        print('      Either the skill was renamed or deleted, or the reference is a typo. '
              'Fix the prose; regenerating will not.', file=sys.stderr)
        return 1
    print(f'OK: {len(named)} skill references in hand-written sections, all exist '
          f'({len(have)} skills on disk)')
    return 0


if __name__ == '__main__':
    if '--check' in sys.argv:
        sys.exit(check())
    main()
