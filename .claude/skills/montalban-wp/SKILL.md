---
name: montalban-wp
description: Write economics working papers in the style of José Montalbán (SOFI). Use whenever drafting WP prose (intro, data, strategy, results, conclusions) for this project. Contains the consolidated style rules (v2, 24/28-09-2026), evidence levels from his corpus, the writing process, and the pre-send checklist. Faithful transcription of the skill built in the Montalbán sessions; source PDF alongside.
---

# Montalbán working-paper style: everything learned

Compiled 28-09-2026 from `style/our_skill/montalban-wp/SKILL.md` and `style/blindtest/LOG.md` (original session). This copy lives in the TALIS repo so it can never be lost again.

## A. Corpus and evidence

Evidence units, one per paper, each in its latest WP version:

| Unit | Paper | Year | Authors | Madrid data |
|---|---|---|---|---|
| AA2025 | Affirmative Action during Early Childhood | 2025 | Margaryan & Montalbán | LOMCE + questionnaires |
| BB2024 | Home Broadband (CEP DP) | 2024 | Montalbán, Sanchis-Guarner, Weinhardt | no |
| SC2020may | School Choice Priorities (SOFI WP) | 2020 | Gortázar, Mayor, Montalbán | CDI as a control |
| JMP2019nov | Countering Moral Hazard (PSE WP v2) | 2019 | sole | no |

- **GENDER2019 (thesis ch. 2) is EXCLUDED from the evidence** (a PhD thesis is a different genre from a WP). Kept only as background on Madrid testing data. The PhD thesis as a whole is also excluded. Evolution units (BB2021 QMUL, SC2020jan, JMP2019jun, JMP2018) used only to see how the style changed.
- Weighting rules (user): all his WPs count as his voice (he was usually the junior author and did the writing); a paper gets less weight only when co-authors are very senior; underdeveloped early drafts get less weight.
- Evidence levels: **[4/4], [3/4]** = number of evidence units in which the rule holds. **STABLE** = at least 3/4 and present in at least one 2024–25 paper → apply. **ERA-2019/20** = present in SC and JMP but absent from AA2025 and BB2024 → apply sparingly (default Q1, section G). **SINGLE** = one paper only → do not use as a rule.
- Anti-AI layer: Lu Han's anti-AI patterns list applies verbatim. **When it conflicts with Montalbán, Montalbán wins** (user decision). No other style guide applies.

## B. Process (from the user; comes before style)

1. **Ideas before prose.** Before writing a section, draft an argument plan: one line per paragraph saying what it *defends* and how it leads to the next. List the **gaps**: why something matters, what to compare it with, what the author would claim.
2. **Author's questions go to the user before writing.** Benchmarks, the preferred estimate, how strongly to interpret, what goes in text vs footnote/appendix, institutional facts not in our sources. Do not write, find the problem, then patch.
3. **Numbers** are phrased as in section E. Checking them against `facts/` is a silent background step.
4. **Never invent facts or interpretations** that the tables and facts do not give (round 1 temptation: "roughly what we would expect by chance").
5. **Empirical Strategy** is presented intuitively and plainly: the comparison in words, why it identifies the effect, then the equation. It should not read like an econometrician showing off.
6. Getting close is enough; 100% is not expected.

## C. Architecture and lengths

| Measure | AA2025 | BB2024 | SC2020 | JMP2019 | Rule |
|---|---|---|---|---|---|
| Main-text words | 7,488 | 12,406 | 11,029 | 13,020 | 7.5–13k; target ~9–13k for Jornada |
| Paragraph median | 104 | 128 | 150 | 147 | **STABLE** 100–150 |
| Paragraph p10/p90 | 52/177 | 57/231 | 62/281 | 54/310 | **STABLE** short ~55, long 180–310 |
| Sentence median (words) | 20 | 22 | 25 | 26 | **STABLE** 20–26, large SD |
| Footnotes per 1k words | 1.7 | 2.7 | 4.3 | 3.0 | **STABLE** 1–4 |
| Intro words / paragraphs | 1,379/11 | 1,638/10 | 1,847/10 | 2,714/12 | **STABLE [4/4]** 10–12 paragraphs, 1,400–2,700 words |

- Numbering: "1 Introduction", "2.1 …" (arabic). [4/4]
- **Run-in headings** inside sections, in sentence case (SC and JMP use Title Case; AA sentence case; default Q2 = sentence case).
- Paragraph lengths vary. There are no one-sentence punch paragraphs: p10 is never below ~50 words. [4/4]

## D. Section templates

**Introduction** (arc confirmed across units):
- P1: the policy problem and why it matters, with 2–4 citations. May pack motivation, trade-off, and a budget or scale figure into one long paragraph. [4/4]
- "This paper / In this paper / We study …" arrives at **P2** (AA, JMP, SC-jan) or **P4–5** (SC-may, BB). **STABLE: by P2–P5; never after the literature review.**
- The headline results with numbers come **early** (P1–P2 in JMP and AA; P5–P6 elsewhere), with their relative size.
- Contributions and the broad literature come **late**: the paragraph with the most citations is P8–P10. [3/4] Form varies (AA: "Our study contributes to two strands of literature"; JMP: run-in "Related literature."; SC: a literature paragraph). Rule: survey the literature **after** the results, not as an opening "gap".
- Roadmap at the end ("The remainder of the paper is organized as follows"). [4/4]
- **Avoid** symmetric double scaffolds ("There are two main reasons … First … Second …" followed by "This setting offers two advantages. First … Second …"). First/Second is fine inside a paragraph; the whole intro must not be built on parallel pairs.

**Institutional Background**:
- General to specific, with concrete magnitudes and their sources. The law or decree goes in a footnote; comparisons give scale. [4/4]
- Procedures walked in time order (calendar). Bullets acceptable for a dated calendar or rule schedule (JMP, twice); otherwise prose.
- Close by linking the institution to identification (what it lets us compare). [4/4]

**Data**:
- One paragraph per source (who produces it, years, universe, contents, stakes), or a list "(i) … (ii) …" with one sentence per file. [4/4]
- Sample restrictions: each with its **share** and its **reason**. Consequences for identification in a footnote ("available upon request" or an appendix table). [4/4]
- Summary statistics walked in prose, mentioning 3–5 facts, not the whole table. [4/4]
- Survey indices described in words: the items, the scale, the standardization. [AA]

**Empirical Strategy**:
- The comparison in words first, then "Our equation of interest …" / "The reduced-form equation …", then a "where …" clause defining each term. [4/4]
- Estimation choices (kernel, bandwidth, clustering, software) take one short sentence each; each alternative goes in a footnote. [3/4]
- "Let X denote" before an equation: SINGLE (JMP) → optional.
- Order: the design in words, the equation and its "where" gloss, the estimator, then the identifying-variation figure.

**Internal Validity**:
- Identifying assumption → testable implications → one paragraph per test (figure or table, result in words, complementary test in the appendix). [AA, BB, JMP]
- Balance and null tests are **terse in the text**: no covariate-by-covariate detail, no chi2 or p-values in the prose, just a pointer to the table. [4/4]

**Results**:
- Descriptive picture or baseline levels first, then the estimates, then the interpretation. [4/4]
- The literature enters Results to interpret magnitudes ("consistent with", "in line with", "contrasts with"). [4/4]
- Robustness is one sentence in the text plus a footnote or appendix table. A robustness *section* has one titled run-in paragraph per check, in the order announced. [SC, JMP, BB]
- Heterogeneity: list the values for the groups, then compare absolute versus relative size. [SC, JMP, AA]
- Results subsection opens with a short technical pointer (linkage, validity), goes to the first table, and gives the "why this outcome matters" literature afterwards, in its own paragraph.

**Conclusions**:
- 1–6 paragraphs: restate the findings in words, then the implication, then the limits and open questions. [4/4]

## E. How numbers and results are stated

- **STABLE [4/4]**:
  - Effect in natural units, then its size relative to the mean: "…, which corresponds to …", "(X percent with respect to the baseline mean)", "or X percent relative to a control mean of Y".
  - Significance in words ("statistically significant at the 5% level", "close to zero and statistically insignificant"). Standard errors and CIs stay in the tables.
  - "precisely estimated null", "we cannot reject …", "we fail to reject …" for nulls. **Numbers for nulls stay in the tables**; give coefficients in the text only for the headline estimate or significant effects.
  - Point to the exact location: "column 5 of Panel B in Table 3", "Panels (c) and (d) of Figure 5".
  - Scale words: about, approximately, roughly, around.
- "respectively" to pair values: [3/4] (not AA).
- Walking through the columns and naming the preferred specification: [BB, SC, JMP].
- Numbers in prose = the headline coefficient, its significance and one verbal comparison ("about five times smaller", "slightly lower"). Other columns qualitative ("This hardly affects the estimates."). **Never give ranges across columns.**
- Paired values in parentheses ("65 (90) percent for STEM (non-STEM)"): ERA-2019/20 → not default.
- Percent: **"percent" in running text; "%" only inside parentheses and tables** (Q3; the corpus mixes, do not normalize a section that mixes deliberately).

## F. Voice and connectors (rates per 1,000 words)

- **STABLE**: "we", active voice; First/Second/Finally within paragraphs (0.7–2.4/1k); "However" (0.4–1.5); "In addition", "Moreover"; "e.g.", "i.e."; "robust"; "potential(ly)" (0.9–1.8); "may/might" (1.1–4.7); "consistent with"; "Overall," [3/4]; "Interestingly" [3/4], rare; inline "(i), (ii)" (0.2–1.3).
- **ERA-2019/20** (SC, JMP; absent in AA/BB): heavy hedging with "seem(s) to"; recent papers hedge with "likely", "could", "suggest" instead. **Not used by default** (J.5/N.4 decided: voice = AA/BB 2024–25).
- **SINGLE (do not use as rules)**: "In a nutshell", "Let X denote", "Result #1:" headings, "Related literature.", "Taken together", "We find", "Notably", em-dashes, "available upon request", "To the best of our knowledge".
- **Anti-tidiness**: no neat closing one-liners that settle a point; footnotes may argue step by step ("Two problems arise. First … Second …"); some loose ordering is fine.
- Markers checked against the corpus — **use**: "unique" [4/4], "universe" [4/4], "henceforth" [3/4], "Interestingly" [3/4], "respectively" [3/4]; "so-called" [2/4] and "Regarding …," [SC] sparingly. **Do NOT use as signature**: "Generally,", "Accordingly,", "Organization of the Paper.", "Importantly,", "It is important to reiterate", "One can argue", "In a nutshell".
- **Ceiling**: judges also detect his non-native slips. We do not imitate errors; the goal is his structure and habits without his mistakes.
- **Tension to watch**: Montalbán restates key facts (the size of the reform, the main estimate, the two distances) where they matter again — restate only KEY facts, and never announce what comes next without adding content.

## G. Defaults (each reversible by the user)

- **Q1 voice**: base = the 2024–25 voice (AA, BB) plus the STABLE rules; ERA-2019/20 traits sparingly, never as a signature.
- **Q2 run-in headings**: sentence case, as in AA.
- **Q3**: "percent" in running text; "%" only inside parentheses and tables.

## H. Pre-send checklist

- Argument plan and gaps written, and the user's questions answered.
- Length within ±5% of the target (section C). Lengths within section C ranges. Paragraphs vary; none under ~50 words.
- Intro: "this paper" by P2–P5, literature after the results, no double scaffolds.
- Every estimate has its unit, relative size and significance in words. Balance and nulls are terse.
- Every robustness claim names its appendix table.
- Only STABLE rules applied, with the defaults in G.
- `tools/tic_lint.py` passed (no hard-limit violations; recreate if absent — hard limits in J.4/M.5).
- Lu Han list passed, except where Montalbán wins.
- Numbers match `facts/`.

## I–O. Consolidation rules (rounds 3–9; "rule of rules" in L)

**Rule of rules (L)**: judge feedback from one held-out section is a **hypothesis**. It becomes a rule only when the corpus check finds it in at least 3 of the 4 units. Round 5 broke this and round 6 penalised it.

**Self-bias (I, stable 6/6 across rounds)**: I write 7–21% too short. Hit the target length within ±5%. Fill the gap ONLY with the kinds of material he uses, never with filler: a restatement of a key fact where it matters again; the institutional or data detail spelled out; one more sentence of interpretation; a longer footnote. His extra length comes from signposting a paragraph's job ("Note that our period ends in 2008 for two reasons: (i)…"), re-introducing an institution or variable when it reappears, and table walk-throughs — never extra facts. **Expanding to reach length is where invention creeps in — pad only with restatements and details that are in the sources.** If a draft is short, first check whether footnote material is missing (footnote words do not count toward the target); otherwise leave it short rather than pad (M.2, L.5 supersedes). If within ~10 percent below target, stay short.

**What not to do (I, J, N)**:
- Do not reorder into textbook logic ("motivate first, then define, then assume"). A paragraph may do two jobs; a detail may come late (channels after the specification, literature positioning after the identification argument).
- Do not remove all redundancy; repeat nouns rather than using pronouns.
- Do not balance paragraphs: next to short ones, usually one overloaded paragraph (setting + data + reform in intros).
- **No synthesis sentences he did not write**: no "These results have several policy implications"; no closing "Overall, …" in every section (corpus ≤0.35/1k); end paragraphs on a fact or a plain claim. A loose trailing fact at the end of a paragraph is fine ("The data also show that the region of Madrid has a rich school supply.").
- **Banned polish** (0–1 corpus hits): literary inversions ("Only in … does …"); "that is," glosses; one-line interpretive closers at the end of a paragraph.
- Stacked closing restatements ("In sum, … These patterns suggest … Taken together, …"): NOT a rule (1/4 papers) — revoked.
- Chopped action/reason sentences ("We do so because…"): revoked; his real habit is long sentences chained with ", and" / ";" and the reason inside the same sentence ("We impose this restriction because …"; caveats get their own short sentence: "Non-citizen children constitute 10.4% of the sample.").

**Sentences and endings (L)**: keep the reason inside the sentence, joined with ", and", ";" or "since". End a subsection on the last result or a forward pointer ("We turn to this question in the next section."); no recap paragraph.

**Citations (L)**: in a parenthesis at the end of the claim, or "X (year) show that…". Never a stand-alone "See, e.g., X; Y; Z." sentence (0 corpus occurrences; bare "See X (year)." pointers go in footnotes). Literature cited author by author, sentence by sentence ("X (year) finds … Y (year) shows …"); do not compress several studies into one tidy parenthetical list.

**Equations (I)**: gloss in one long sentence: "where X is …; Y is …; …; and ε is the error term" (SC, BB); then one sentence on the parameter of interest. No (a)/(b) lists for the terms.

**Footnotes (M, N, O)**: they are MY decision; target rate 1.7–4.3 per 1k words as a **check, not a quota** — every footnote must carry substance: a caveat, a benchmark, a list of exclusions, a mechanism, a legal reference (legal hierarchy and law numbers), a robustness result, a speculative explanation of a pattern ("One possible reason is…"), bare "See X (year)." pointers, grab-bag notes mixing a figure pointer with a rule. Never pointer-only or source-only notes ("See Table X for the full estimates.", "The data come from X."). Footnotes are uneven: some one line, one or two loaded with several loosely related papers and asides. Placement decided by content, never by length. Never add explanatory clauses just to "improve" them.

**Tables (O)**: two kinds. Descriptive/summary tables: walk them panel by panel with 3–5 concrete values. Regression tables: the headline estimate, its significance and one comparison.

**Data sections (M)**: one run-in label per source or block ("School database.", "Household parental education.").

**Precision (M.4)**: state what the text needs in the fact sheet's own terms. Do not add extra shares, significance levels on balance rows, or unit corrections just because they are available. If the source text and table disagree, treat it as the author's slip — do not silently correct in ways that change facts; keep correcting genuine errors (we do not imitate his mistakes).

**Rhythm (M.5, J.4 hard limits, checked by `tools/tic_lint.py`)**: median sentence 22–29 words; 6–13% short sentences; semicolons 1.9–4.0/1k; footnotes 1.7–4.3/1k. My tics: "therefore" ≤0.6/1k; "Hence" ≤0.7/1k; "On the one hand … On the other hand" ≈0; "Recall that" 0; "Overall," ≤0.35/1k; "In conclusion" not a habit (0–0.05/1k); "We now" ≤0.17; "Note that", "Moreover", "Hence", "As a result": 0.1–0.5/1k each (at most one per section). Must appear: "However" (0.4–1.6/1k), "e.g./i.e." (0.5–2.2/1k), "potential(ly)" (≥0.8/1k).

**Cross-references (M.7)**: a roadmap does not need "(Section 5.1)" after each part.

## Blind-test protocol (for future rounds; user: "sin trampas", 25-09-2026)

- Held-out sections come from papers not yet read by the writer. JMP (all versions) is contaminated; candidates: GENDER2019 and SC2020jan-only passages (then exclude that unit from the corpus).
- Fact sheets carry no footnote tags or counts and do not mark which numbers the original states in the text (that lives in `H_manifest.md`, which the writer never reads). The writer never opens `_original.txt`, `H_manifest.md`, `_KEY_.json` or `judge/`.
- No deliberate typos or slips to fool the judges; no editing of a text after seeing the judges' verdicts.
- 3 independent judges; reference texts from units not being tested. Scores from round 6 onward are not strictly comparable with rounds 1–5 (stricter protocol).
- Trend over rounds 1–9: 4.0 → plateau 5.5–6.3. Judges' strongest remaining tell: his slips and factual errors, which we do not imitate. Diminishing returns past this ceiling.
- Meta-lesson (repeated): overcorrection is the recurring failure — a rate becomes a quota, a regression-table rule gets applied to descriptive tables, material moves between text and footnotes for LENGTH. Rules serve content, checked against the corpus.
