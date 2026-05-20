"""Assemble the 6 per-problem review fragments into one master document.

Recomputes every summary statistic directly from the table rows (the agent
summary lines had some wrong flag counts), then writes grade-review.md.
"""
from __future__ import annotations

import re
from pathlib import Path

REVIEW_DIR = Path("experiments/dataset/_review")
OUT = Path("experiments/dataset/grade-review.md")

frag_paths = [REVIEW_DIR / f"P{i}-review.md" for i in range(1, 7)]


def parse_fragment(path: Path):
    lines = path.read_text(encoding="utf-8").splitlines()
    title = lines[0].lstrip("# ").strip()
    hdr_idx = next(
        i for i, l in enumerate(lines)
        if "Total (you)" in l and l.strip().startswith("|")
    )
    header = [c.strip() for c in lines[hdr_idx].strip().strip("|").split("|")]
    col = {name: i for i, name in enumerate(header)}
    iy, im, ifl, iid = (col["Total (you)"], col["Total (me)"],
                        col["Flag"], col["ID"])
    rows = []
    for l in lines[hdr_idx + 2:]:
        s = l.strip()
        if not s.startswith("|"):
            break
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < len(header):
            continue
        rows.append({
            "id": cells[iid],
            "you": int(cells[iy]),
            "me": int(cells[im]),
            "flag": "\U0001f6a9" in cells[ifl],
        })
    return {"title": title, "lines": lines, "rows": rows}


def stats(rows):
    n = len(rows)
    flagged = sum(1 for r in rows if r["flag"])
    you_mean = sum(r["you"] for r in rows) / n
    me_mean = sum(r["me"] for r in rows) / n
    abs_delta = sum(abs(r["you"] - r["me"]) for r in rows) / n
    signed = sum(r["you"] - r["me"] for r in rows) / n
    return n, flagged, you_mean, me_mean, abs_delta, signed


frags = [parse_fragment(p) for p in frag_paths]

# ---- executive summary -------------------------------------------------
exec_rows = []
all_rows = []
tot_n = tot_flag = 0
sum_you = sum_me = sum_absd = 0.0
for frag in frags:
    rows = frag["rows"]
    pid = frag["title"].split(" — ")[0]
    name = frag["title"].split(" — ")[1].rsplit(" (", 1)[0]
    n, flagged, ym, mm, ad, sd = stats(rows)
    exec_rows.append((pid, name, n, flagged, ym, mm, sd, ad))
    tot_n += n
    tot_flag += flagged
    sum_you += sum(r["you"] for r in rows)
    sum_me += sum(r["me"] for r in rows)
    sum_absd += sum(abs(r["you"] - r["me"]) for r in rows)
    for r in rows:
        all_rows.append({**r, "pid": pid})

ov_you = sum_you / tot_n
ov_me = sum_me / tot_n
ov_absd = sum_absd / tot_n
ov_sd = (sum_you - sum_me) / tot_n

# ---- biggest discrepancies --------------------------------------------
top = sorted(all_rows, key=lambda r: abs(r["you"] - r["me"]), reverse=True)[:20]

# ---- build document ----------------------------------------------------
out = []
out.append("# Grade Review — Human vs. Independent LLM Re-grade")
out.append("")
out.append("_Generated 2026-05-17 · 144 submissions across 6 problems._")
out.append("")
out.append(
    "Every submission was re-graded independently against the same per-problem "
    "rubric, then compared to the human grader's scores. The rubric was "
    "softened mid-review to grade **demonstrated algorithmic intent over "
    "executability** — a localized syntax / parse / compile error in "
    "otherwise readable code is now a bounded Code Quality deduction (capped "
    "at −5/100), not a Correctness zero. A row is **flagged \U0001f6a9** "
    "when the totals differ by ≥ 10 points, the human's per-criterion "
    "breakdown is internally inconsistent, or a documented semantic defect "
    "(wrong algorithm, crash, data race, deadlock, mis-eviction, logic bug) "
    "is not reflected in the score."
)
out.append("")
out.append("In every per-problem table, a criterion cell reads `you→me` "
           "(your sub-score, then mine); a single number means we agreed. "
           "`Δ` = your total − my total (a **positive Δ means you "
           "scored higher than I would**).")
out.append("")
out.append("## Executive summary")
out.append("")
out.append("| Problem | N | Flagged | Your mean | My mean | Mean Δ (you−me) | Mean \\|Δ\\| |")
out.append("|---|---|---|---|---|---|---|")
for pid, name, n, flagged, ym, mm, sd, ad in exec_rows:
    out.append(f"| {pid} {name} | {n} | {flagged} | {ym:.1f} | {mm:.1f} "
               f"| {sd:+.1f} | {ad:.1f} |")
out.append(f"| **All** | **{tot_n}** | **{tot_flag}** | **{ov_you:.1f}** "
           f"| **{ov_me:.1f}** | **{ov_sd:+.1f}** | **{ov_absd:.1f}** |")
out.append("")
out.append(f"**{tot_flag} of {tot_n} submissions are flagged.** Under the "
           "softened rubric, the dominant pattern is over-scoring of code "
           "with **real semantic defects** — wrong algorithm, crashes, "
           "deadlocks, data races, mis-eviction, off-by-one logic bugs — "
           "where the human kept near-full Correctness. A secondary pattern "
           "is **under-scoring clean correct alternatives** (hash+DLL caches "
           "in P3, the augmented BST in P5, a modern-Go solution in P6, the "
           "cleanest `reduce` solutions in P1). Localized syntax / compile "
           "failures are no longer themselves a flag source — they are "
           "bounded at −5 via Code Quality and the affected rows now sit "
           "within tolerance of the human score.")
out.append("")
out.append("### Where to look first")
out.append("")
out.append("- **P6** has the highest mean \\|Δ\\| "
           f"({exec_rows[5][7]:.1f}) — concurrency bugs (deadlocks, races, "
           "panics, goroutine leaks) were repeatedly given 60-tier scores.")
out.append("- **P4** flags concentrate on **wrong-algorithm** submissions "
           "(BFS / Bellman-Ford / DFS scored as Dijkstra) and Dijkstra-shaped "
           "implementations with real correctness bugs (`dist[source] = "
           "LLONG_MAX`, missing re-push, mark-before-pop).")
out.append("- **P3** flags split both directions: documented eviction / "
           "infinite-loop defects over-scored, and clean hash+DLL caches "
           "under-scored.")
out.append("- **P5** is the most consistent (mean \\|Δ\\| "
           f"{exec_rows[4][7]:.1f}); only {exec_rows[4][3]} rows need a look.")
out.append("")
out.append("## Top 20 discrepancies")
out.append("")
out.append("| Problem | Submission | Total (you) | Total (me) | Δ | Issue |")
out.append("|---|---|---|---|---|---|")
issue_by_id = {}
for frag in frags:
    block = "\n".join(frag["lines"])
    for m in re.finditer(r"^- \*\*(?P<id>[\w]+)\*\*.*?\):\s*(?P<txt>.+)$",
                         block, re.MULTILINE):
        issue_by_id[m.group("id")] = m.group("txt").strip()
for r in top:
    d = r["you"] - r["me"]
    issue = issue_by_id.get(r["id"], "")
    if issue:
        parts = re.split(r"(?<=[.])\s", issue)
        issue = parts[0]
        # skip uninformative lead-ins ("Largest gap in the set.")
        if len(issue) < 40 and len(parts) > 1:
            issue = parts[1]
    else:
        issue = "see section below"
    if len(issue) > 110:
        issue = issue[:107] + "..."
    out.append(f"| {r['pid']} | `{r['id']}` | {r['you']} | {r['me']} "
               f"| {d:+d} | {issue} |")
out.append("")
out.append("---")
out.append("")

# ---- per-problem sections (replace the Summary line with recomputed) ---
for frag, (pid, name, n, flagged, ym, mm, sd, ad) in zip(frags, exec_rows):
    lines = list(frag["lines"])
    for i, l in enumerate(lines):
        if l.startswith("**Summary:**"):
            lines[i] = (f"**Summary:** flagged {flagged}/{n} · mean "
                        f"\\|Δ\\| {ad:.1f} · your mean {ym:.1f} "
                        f"· my mean {mm:.1f}")
            break
    out.append("\n".join(lines).rstrip())
    out.append("")
    out.append("---")
    out.append("")

OUT.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
print(f"wrote {OUT} ({len(out)} blocks)")
print(f"total flagged: {tot_flag}/{tot_n}")
for pid, name, n, flagged, ym, mm, sd, ad in exec_rows:
    print(f"  {pid}: n={n} flagged={flagged} you={ym:.1f} me={mm:.1f} "
          f"|d|={ad:.1f}")
