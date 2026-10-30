---
description: "/critique-adversarial - Hostile cut-editor for articles. Reads the full piece first, maps the thesis spine, then recommends cuts that TIGHTEN prose without damaging the argument. Classifies every passage: CUT / REWRITE / MOVE / KEEP. Never cuts blind."
when_to_use: 'Trigger phrases: "cut this down", "it is too long", "tighten this article", "hostile edit", "what can I remove", "make it sharper". For prose, not code.'
allowed-tools: Bash(cat *), Bash(wc *), Bash(grep *), Bash(mkdir *), Bash(date *), Read, Write, Edit, Glob, Grep, Agent
---

# /critique-adversarial - Context-Aware Hostile Editor

**Cut only what won't hurt the argument.** This skill adapts the adversarial cut pattern for articles. It reads the entire piece first, identifies the thesis and how each section serves it, and only recommends cuts that tighten prose without weakening the argument. Some things that LOOK like fat are actually load-bearing. The skill knows the difference.

**FIRE AND FORGET** - Point at a draft, receive a cut/rewrite/move/keep classification for every flagged passage with specific reasoning.

> **When to use:**
> - After the author's own cut, to catch what the author left in
> - Before shipping any long-form article
> - When a piece feels bloated but you cannot see what to remove
> - As a second-pass editor when you want hostile-but-informed feedback
>
> **When NOT to use:**
> - Before the article has a clear thesis (settle the angle first)
> - On first drafts before the author has cut (let them cut first; then adversarial catches what remains)

---

## DISCIPLINE

> Reference: [Steel Discipline Protocol](~/.claude/standards/STEEL_DISCIPLINE.md)

Key enforcements for this skill:

- **Steel Principle #1:** No cut recommendation without reading the FULL article first. Never cut blind. Context first, cuts second.
- **Steel Principle #2:** Every cut recommendation must answer: "Does removing this weaken the argument?" If yes or unclear, classify as KEEP with reasoning.
- **Steel Principle #3:** Repetition is not automatically fat. Rhythmic repetition, load-bearing emphasis, and reinforcement of the central claim are OK. Unnecessary repetition is not.
- **Steel Principle #4:** Never recommend a cut without quoting the exact text (10+ words). Vague "consider shortening this section" is rejected.
- **Steel Principle #5:** The author's voice is sacred. Passages that establish or maintain voice are preserved even if technically "cuttable."

### Adversarial-Specific Rationalization Table

| Rationalization | Reality | What to Do |
|----------------|---------|------------|
| "This paragraph repeats the last one, cut it" | Maybe. Or maybe the repetition is emphasis that earns readers' attention | Check if repetition serves rhythm or reinforcement; KEEP if yes |
| "This example is generic, cut it" | Generic examples are rewrite candidates, not cut candidates | Classify as REWRITE with a specific example replacement |
| "This section is tangential" | Tangents that reveal the author's mind are character; tangents that derail the argument are fat | Read the thesis first; cut only if the tangent doesn't serve the thesis or voice |
| "Cut 500 words from here" | Arbitrary cut quotas damage the argument | Cut what actually needs cutting; if that is 200 words, it is 200 words |
| "This quote is too long" | Long quotes establish authority when the source is primary | Trim quotes only if parts of the quote add no argumentative weight |
| "The intro is slow, cut it" | Slow intros that plant the reader in a scene are a feature, not a bug | Only cut intro passages that abstract instead of concrete |
| "This hedge is wishy-washy" | Hedges on genuinely uncertain claims are honest; hedges on clear claims are cowardly | Distinguish genuine uncertainty (KEEP) from covered hedging (CUT) |

---

## STATUS UPDATES

This skill follows the [Status Update Protocol](~/.claude/standards/STATUS_UPDATES.md).

```
📖 Phase 1: Full Read (context before cuts)
🧭 Phase 2: Thesis + Spine Map
🔍 Phase 3: Passage-by-Passage Classification
📊 Phase 4: Report with evidence
🎯 Phase 5: User review + apply
```

---

## OUTPUT STRUCTURE

```
articles/YYYY-MM-DD-[slug]/drafts/
├── critique-adversarial.md          # This skill's full report
├── critique-adversarial-applied.md  # Draft with approved changes applied
```

---

## PHASE 1: FULL READ (MANDATORY FIRST STEP)

Read the entire article end-to-end. No sampling. No skimming. This is the context foundation for every downstream cut recommendation.

```bash
DRAFT=$1  # path to draft file
WORD_COUNT=$(wc -w < "$DRAFT")
echo "📖 Reading full article: $WORD_COUNT words"
cat "$DRAFT"
```

**Do not skip this phase.** Recommendations made without full context are rejected.

---

## PHASE 2: THESIS + SPINE MAP

Before recommending any cut, build a structural map of the article.

### Thesis Extraction

Identify the ONE specific claim this article is making. Usually found in the first 2-4 paragraphs, sometimes repeated/refined at the closer.

Format:
```
Thesis: [one-sentence specific claim]
Supporting pillars (must not be cut):
  Pillar A: [evidence/reasoning that holds up the thesis]
  Pillar B: [evidence/reasoning]
  Pillar C: [evidence/reasoning]
```

### Section-by-Section Role Map

For each section heading, identify its role:

| Section | Role | Load-Bearing? |
|---------|------|---------------|
| Hook | Plant reader in specific context | YES (cutting weakens opening) |
| Setup | Establish the tension | YES if concise; candidate for cut if over-developed |
| Pillar section | Supports a thesis pillar | YES |
| Counterargument | Addresses disagreement | YES if Standard/Deep-tier article |
| Closer | Land the thesis | YES |
| Tangent | Serves voice or color | DEPENDS (see rationalization table) |

**Any section marked YES for load-bearing gets extra scrutiny before any cut is recommended within it.**

---

## PHASE 3: PASSAGE-BY-PASSAGE CLASSIFICATION

Go through the article and flag every passage that could be cut, rewritten, moved, or needs to stay. Target: 10-20 flagged passages per ~3K word article. Fewer flags = stronger piece. More flags = more work.

### Classification Categories

| Tag | Meaning | Action |
|-----|---------|--------|
| **CUT** | Removing it improves prose without weakening argument | Recommend removal |
| **REWRITE** | Content is needed, execution is weak (generic, tell-not-show, unclear) | Recommend specific rewrite |
| **MOVE** | Wrong placement breaking argument flow; belongs elsewhere | Recommend new location |
| **TRIM** | Partial cut within the passage - quote parts to remove | Recommend surgical trim |
| **KEEP** | Looks cuttable but is load-bearing (voice, emphasis, pillar support) | Explain why it stays |

### Required Evidence Per Flag

For every flagged passage, the report must include:

1. **Location:** line number or paragraph marker
2. **Exact quote:** 10+ words, verbatim from the draft
3. **Classification:** CUT / REWRITE / MOVE / TRIM / KEEP
4. **Reasoning:** one sentence connecting the classification to the thesis spine or voice
5. **Recommended action:** specific text to remove, specific rewrite, or specific new placement
6. **Argument impact:** what happens to the argument if this action is taken

### Fat Sub-categories (within CUT and TRIM)

When classifying CUT or TRIM, specify which fat type:

| Sub-tag | Meaning | Example |
|---------|---------|---------|
| FAT | Filler that adds nothing | "It's important to note that..." |
| REDUNDANT | Repeats a point already made, no emphasis value | Same idea said twice in adjacent paragraphs |
| OVER-EXPLAIN | Explains something the reader already understands | Defining a term the audience knows |
| TRANSITION-WASTE | Connective scaffolding that does no work | "As we saw above..." |
| QUOTE-BLOAT | Long quotes with sections that add no argumentative weight | Block quote where only 1 sentence matters |
| STRUCTURAL | Well-written but wrong placement | Example given before the claim it supports |

---

## PHASE 4: REPORT

Save to `articles/YYYY-MM-DD-[slug]/drafts/critique-adversarial.md`:

```markdown
# Adversarial Critique Report - [slug]

**Date:** YYYY-MM-DD
**Draft reviewed:** [path to input draft]
**Starting word count:** [X] words
**Flagged passages:** [N]

## Thesis Spine

**Thesis:** [extracted thesis]

**Supporting pillars:**
- A: [pillar]
- B: [pillar]
- C: [pillar]

## Section Role Map

| Section | Role | Load-Bearing |
|---------|------|--------------|
| ...     | ...  | ...          |

## Passage Classifications

### CUT Recommendations ([N])

#### Cut 1: [location]
**Quote:** "exact 10+ word quote from the draft..."
**Sub-category:** FAT / REDUNDANT / OVER-EXPLAIN / TRANSITION-WASTE / QUOTE-BLOAT / STRUCTURAL
**Reasoning:** [one sentence]
**Argument impact:** [what happens to the argument if cut]
**Recommended removal:** [specific text to delete]

#### Cut 2: [location]
[...]

### REWRITE Recommendations ([M])

#### Rewrite 1: [location]
**Quote:** "exact 10+ word quote..."
**Issue:** GENERIC / TELL-NOT-SHOW / UNCLEAR / JARGON-DENSE
**Reasoning:** [one sentence]
**Suggested rewrite:** [specific replacement text or guidance]

### MOVE Recommendations ([K])

#### Move 1: [from location] → [to location]
**Quote:** "exact 10+ word quote..."
**Reasoning:** [why the current placement breaks the argument flow]

### TRIM Recommendations ([L])

#### Trim 1: [location]
**Full passage:** "..."
**Portion to trim:** "the specific sentences or phrases to remove"
**Reasoning:** [one sentence]

### KEEP (Looks Cuttable But Is Load-Bearing) ([P])

#### Keep 1: [location]
**Quote:** "exact 10+ word quote..."
**Why it looks cuttable:** [what makes it feel like fat]
**Why it stays:** [how it serves the thesis, pillar, voice, or rhythm]

## Summary

| Category | Count | Estimated Word Impact |
|----------|-------|----------------------|
| CUT | N | -[X] words |
| REWRITE | M | net 0 (replace, not remove) |
| MOVE | K | net 0 (relocate) |
| TRIM | L | -[Y] words |
| KEEP | P | 0 (preserved) |

**Total recommended word reduction:** [X + Y] words (from [starting] to ~[after]).
**Cuttable percentage:** [Z]%

**Tightest passage:** [location] - no flags found
**Loosest passage:** [location] - most flags

## Argument Integrity Check

After applying ALL recommended cuts/rewrites/moves:
- Thesis clarity: [stronger / same / weaker]
- Supporting pillars: [all preserved / pillar X weakened]
- Voice preservation: [preserved / reduced in section Y]
- Reader takeaway: [sharper / same / muddied]

**Overall verdict:** [Apply cuts / Apply selectively / Do not apply - article is already tight]
```

---

## PHASE 5: USER REVIEW + APPLY

Present the report. User reviews. Options:

1. **Apply all** - accept every recommendation, save result to `critique-adversarial-applied.md`
2. **Apply selectively** - user marks specific items to accept; skill applies only those
3. **Reject all** - skill's recommendations are not applied; article stays as-is
4. **Re-run with stricter/lenient threshold** - adjust aggressiveness, get new report

Do NOT auto-apply. Author has final authority on every cut.

---

## CLEANUP PROTOCOL

> Reference: [Resource Cleanup Protocol](~/.claude/standards/CLEANUP_PROTOCOL.md)

### Adversarial-Specific Cleanup

1. **Reports preserved.** `critique-adversarial.md` stays in the article's draft folder as audit trail.
2. **Applied version preserved.** `critique-adversarial-applied.md` becomes the next draft input to downstream phases.
3. **No temp files created.** Skill reads and writes only in the article's existing draft folder.

---

## SITREP

> Reference: [SITREP Standard](~/.claude/standards/SITREP_FORMAT.md)

```
═══════════════════════════════════════════════════════════════
SITREP - /critique-adversarial
═══════════════════════════════════════════════════════════════

  Draft reviewed:  articles/YYYY-MM-DD-[slug]/drafts/draft-vN.md
  Word count:      [before] → [after] ([% reduction])
  Flags:           CUT:[N] REWRITE:[M] MOVE:[K] TRIM:[L] KEEP:[P]

  Thesis preserved:     YES / NO
  Pillars preserved:    [N]/[N]
  Voice preserved:      YES / YES-WITH-NOTES / NO
  Argument integrity:   STRONGER / SAME / WEAKER

  Tightest section:     [section name]
  Loosest section:      [section name]

  Verdict:         [APPLY ALL / APPLY SELECTIVELY / DO NOT APPLY]

  Files:
    Report:        articles/YYYY-MM-DD-[slug]/drafts/critique-adversarial.md
    Applied:       articles/YYYY-MM-DD-[slug]/drafts/critique-adversarial-applied.md

═══════════════════════════════════════════════════════════════
                Next: fact pass · or re-run
═══════════════════════════════════════════════════════════════
```

---

## RELATED SKILLS

**Feeds from:**
- The author's own cut - this skill catches what they left in

**Feeds into:**
- A fact pass - the tightened draft goes to fact-checking next
- `/article` (project skill in the Steel Motion repo) - publishes the article once the cut and fact pass are done

**Auto-suggest after completion:**
- If cuts applied: "Cuts applied. Want a fact pass next?"
- If no cuts applied: "Article is tight. Ready for fact pass?"
- If argument weakened: "Flagged argument impact. Want to rework before applying?"

---

## MODES

```bash
/critique-adversarial [draft-path]             # Standard pass
/critique-adversarial [draft-path] --strict    # More aggressive flagging (target: 25+ flags)
/critique-adversarial [draft-path] --lenient   # Only flag obvious fat (target: 5-10 flags)
/critique-adversarial [draft-path] --dry       # Report only, do not write applied version
```

---

## REMEMBER

- **Context first.** Read the full article before flagging anything. No exceptions.
- **Thesis spine is sacred.** Cuts that weaken the thesis or its supporting pillars are rejected.
- **Voice is sacred.** Passages that establish or maintain the author's voice stay, even if "redundant."
- **Repetition ≠ fat.** Rhythmic repetition, load-bearing emphasis, and reinforcement of central claims are preserved.
- **Quote exactly.** Every flag requires a 10+ word verbatim quote. Vague recommendations are rejected.
- **Classify precisely.** CUT / REWRITE / MOVE / TRIM / KEEP - each is a different action. Do not conflate.
- **Argument integrity check is mandatory.** Before finalizing the report, verify the article still holds up with all cuts applied.
- **Author has final authority.** This skill recommends. The author decides.

ARGUMENTS: $ARGUMENTS

<!-- /critique-adversarial - context-aware hostile cut-editor for long-form articles -->
<!-- Adapts prophet-a-novel/.claude/commands/adversarial.md for article form -->
