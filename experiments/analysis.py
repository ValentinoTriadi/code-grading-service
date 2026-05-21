"""Phase-end analysis: compute Pearson/MAE per scenario, ICC for the winner.

Pure-Python ICC (in `experiments.metrics`) is the load-bearing implementation.
If `pingouin` is installed it is used additionally to compute a 95% CI; otherwise
a normal-approximation CI is reported.
"""

from __future__ import annotations

import logging
import math

from experiments import metrics

logger = logging.getLogger(__name__)


def per_scenario_pairs(
    phase1_rows: list[dict],
    submissions_by_id: dict[str, dict],
) -> dict[str, list[tuple[float, float]]]:
    """Group (human_score, llm_score) pairs by scenario_id, dropping invalid rows."""
    by_scenario: dict[str, list[tuple[float, float]]] = {}
    for row in phase1_rows:
        if not row.get("schema_valid"):
            continue
        scenario_id = row.get("scenario_id")
        submission_id = row.get("submission_id")
        if scenario_id is None or submission_id is None:
            continue
        sub = submissions_by_id.get(submission_id)
        if sub is None or sub.get("human_score") is None:
            continue
        by_scenario.setdefault(scenario_id, []).append(
            (float(sub["human_score"]), float(row["score"]))
        )
    return by_scenario


def per_scenario_problem_pairs(
    phase1_rows: list[dict],
    submissions_by_id: dict[str, dict],
) -> dict[tuple[str, str], list[tuple[float, float]]]:
    """Group (human, llm) pairs by (scenario_id, problem_id)."""
    out: dict[tuple[str, str], list[tuple[float, float]]] = {}
    for row in phase1_rows:
        if not row.get("schema_valid"):
            continue
        scenario_id = row.get("scenario_id")
        submission_id = row.get("submission_id")
        if scenario_id is None or submission_id is None:
            continue
        sub = submissions_by_id.get(submission_id)
        if sub is None or sub.get("human_score") is None:
            continue
        key = (scenario_id, sub["problem_id"])
        out.setdefault(key, []).append(
            (float(sub["human_score"]), float(row["score"]))
        )
    return out


def compute_phase1_metrics(
    phase1_rows: list[dict],
    submissions_by_id: dict[str, dict],
) -> dict[str, dict[str, float]]:
    """Per-scenario accuracy metrics over (human, LLM) pairs.

    Returns {scenario_id: {n, mae, mae_normalized, pearson, icc, icc_ci_lo, icc_ci_hi}}.

    `mae_normalized = mae / 100` so the 0–1 convention from the brief is satisfied.
    `icc` is ICC(A,1) computed on a n×2 [human, llm] matrix per scenario — a
    second accuracy view alongside MAE/Pearson, asking "do the human and the
    LLM agree on absolute scores, treating them as two raters?"
    """
    pairs = per_scenario_pairs(phase1_rows, submissions_by_id)
    out: dict[str, dict[str, float]] = {}
    for scenario_id, pp in pairs.items():
        humans = [h for h, _ in pp]
        llms = [l for _, l in pp]
        m = metrics.mae(humans, llms)
        matrix = [[h, l] for h, l in pp]
        if len(pp) >= 2:
            icc, (ci_lo, ci_hi) = compute_icc(matrix)
        else:
            icc, ci_lo, ci_hi = float("nan"), float("nan"), float("nan")
        out[scenario_id] = {
            "n": len(pp),
            "mae": m,
            "mae_normalized": m / 100.0,
            "pearson": metrics.pearson(humans, llms),
            "icc": icc,
            "icc_ci_lo": ci_lo,
            "icc_ci_hi": ci_hi,
        }
    return out


def compute_phase1_anova(
    phase1_rows: list[dict],
    submissions_by_id: dict[str, dict],
    scenarios_by_id: dict,
) -> dict | None:
    """3-way ANOVA on per-row absolute error with factors {rubric, cot, fewshot}.

    Each schema-valid Phase 1 row contributes one observation: the response
    is `|human - llm|` and the three binary factors come from the scenario.
    Returns `{n, table: [{source, sum_sq, df, F, p}, ...]}`, or `None` if
    `statsmodels` is unavailable.
    """
    try:
        import pandas as pd
        import statsmodels.api as sm
        from statsmodels.formula.api import ols
    except Exception as exc:  # pragma: no cover — optional dep
        logger.info(
            "statsmodels unavailable (%s) — skipping 3-way ANOVA",
            exc.__class__.__name__,
        )
        return None

    records: list[dict] = []
    for row in phase1_rows:
        if not row.get("schema_valid"):
            continue
        sid = row.get("scenario_id")
        sub_id = row.get("submission_id")
        if sid is None or sub_id is None or sid not in scenarios_by_id:
            continue
        sub = submissions_by_id.get(sub_id)
        if sub is None or sub.get("human_score") is None:
            continue
        sc = scenarios_by_id[sid]
        records.append(
            {
                "abs_error": abs(float(sub["human_score"]) - float(row["score"])),
                "rubric": int(sc.structured_rubric),
                "cot": int(sc.cot),
                "fewshot": int(sc.few_shot),
            }
        )
    if not records:
        return None
    df = pd.DataFrame.from_records(records)
    model = ols("abs_error ~ C(rubric) * C(cot) * C(fewshot)", data=df).fit()
    table = sm.stats.anova_lm(model, typ=2)
    rows_out: list[dict] = []
    for source, r in table.iterrows():
        rows_out.append(
            {
                "source": str(source),
                "sum_sq": float(r["sum_sq"]),
                "df": float(r["df"]),
                "F": float(r["F"]) if not pd.isna(r["F"]) else float("nan"),
                "p": float(r["PR(>F)"]) if not pd.isna(r["PR(>F)"]) else float("nan"),
            }
        )
    return {"n": int(len(df)), "table": rows_out}


def pick_best_scenario(scenario_metrics: dict[str, dict[str, float]]) -> str:
    """Lowest MAE primary, highest Pearson r as tiebreaker."""
    return min(
        scenario_metrics,
        key=lambda s: (scenario_metrics[s]["mae"], -scenario_metrics[s]["pearson"]),
    )


def pick_worst_case(
    phase1_rows: list[dict],
    submissions_by_id: dict[str, dict],
) -> tuple[str, dict[str, float]]:
    """Return (worst_case_id, {problem_id: avg_mae_across_scenarios})."""
    pairs = per_scenario_problem_pairs(phase1_rows, submissions_by_id)
    case_maes: dict[str, list[float]] = {}
    for (_scenario, problem_id), pp in pairs.items():
        humans = [h for h, _ in pp]
        llms = [l for _, l in pp]
        case_maes.setdefault(problem_id, []).append(metrics.mae(humans, llms))
    avg = {p: sum(v) / len(v) for p, v in case_maes.items()}
    if not avg:
        raise ValueError("No valid (scenario, case) pairs to compute worst case from.")
    worst = max(avg, key=avg.get)
    return worst, avg


def build_icc_matrix(
    phase2_rows: list[dict],
) -> tuple[list[list[float]], list[str]]:
    """Build an n×k matrix of LLM scores from Phase 2 rows.

    Rows = submissions (sorted by submission_id), columns = replicate index.
    Returns (matrix, submission_ids).
    """
    by_submission: dict[str, dict[int, float]] = {}
    for row in phase2_rows:
        if not row.get("schema_valid"):
            continue
        sid = row["submission_id"]
        rep = int(row["replicate"])
        by_submission.setdefault(sid, {})[rep] = float(row["score"])

    submission_ids = sorted(by_submission)
    if not submission_ids:
        return [], []
    max_rep = max(max(by_submission[s].keys()) for s in submission_ids)
    matrix: list[list[float]] = []
    keep_ids: list[str] = []
    for sid in submission_ids:
        row_dict = by_submission[sid]
        if len(row_dict) < max_rep + 1:
            logger.warning(
                "Submission %s has %d/%d replicates — dropping from ICC matrix",
                sid,
                len(row_dict),
                max_rep + 1,
            )
            continue
        matrix.append([row_dict[r] for r in range(max_rep + 1)])
        keep_ids.append(sid)
    return matrix, keep_ids


def compute_icc(matrix: list[list[float]]) -> tuple[float, tuple[float, float]]:
    """Return (ICC(A,1), (ci_lo, ci_hi)).

    Prefers `pingouin.intraclass_corr` for the CI; falls back to a Fisher-z
    normal approximation if pingouin isn't installed.
    """
    point = metrics.icc_a1(matrix)
    n = len(matrix)
    k = len(matrix[0]) if matrix else 0

    try:
        import pandas as pd
        import pingouin as pg

        records = []
        for i, row in enumerate(matrix):
            for j, v in enumerate(row):
                records.append({"target": i, "rater": j, "score": v})
        df = pd.DataFrame.from_records(records)
        result = pg.intraclass_corr(
            data=df, targets="target", raters="rater", ratings="score"
        ).set_index("Type")
        # ICC(A,1) = ICC2 in pingouin's nomenclature (two-way mixed, single rater, absolute)
        row = result.loc["ICC2"]
        return float(row["ICC"]), (float(row["CI95%"][0]), float(row["CI95%"][1]))
    except Exception as exc:  # pragma: no cover — optional dep
        logger.info(
            "pingouin unavailable (%s); falling back to Fisher-z approximation",
            exc.__class__.__name__,
        )

    if n <= 3 or k < 2 or point >= 1.0 or point <= -1.0:
        return point, (point, point)
    z = 0.5 * math.log((1 + point) / (1 - point))
    se = 1 / math.sqrt(n - 3)
    lo = math.tanh(z - 1.96 * se)
    hi = math.tanh(z + 1.96 * se)
    return point, (lo, hi)


def format_phase1_table(
    scenario_metrics: dict[str, dict[str, float]],
    case_avg_mae: dict[str, float],
    best_scenario_id: str,
    worst_case_id: str,
) -> str:
    width = 92
    lines = []
    lines.append("=" * width)
    lines.append("PHASE 1 — accuracy")
    lines.append("=" * width)
    header = (
        f"{'scenario':<10} {'n':>4}  {'MAE':>7}  {'MAE/100':>8}  "
        f"{'Pearson':>8}  {'ICC(A,1)':>9}  {'ICC 95% CI':<19}"
    )
    lines.append(header)
    lines.append("-" * width)
    for sid in sorted(scenario_metrics):
        m = scenario_metrics[sid]
        marker = "  <-- best" if sid == best_scenario_id else ""
        ci = f"[{m['icc_ci_lo']:.3f}, {m['icc_ci_hi']:.3f}]"
        lines.append(
            f"{sid:<10} {int(m['n']):>4}  {m['mae']:>7.3f}  "
            f"{m['mae_normalized']:>8.4f}  {m['pearson']:>8.3f}  "
            f"{m['icc']:>9.3f}  {ci:<19}{marker}"
        )
    lines.append("")
    lines.append(f"{'case':<10} {'avg MAE':>10}")
    lines.append("-" * width)
    for pid in sorted(case_avg_mae):
        marker = "  <-- worst" if pid == worst_case_id else ""
        lines.append(f"{pid:<10} {case_avg_mae[pid]:>10.3f}{marker}")
    lines.append("=" * width)
    return "\n".join(lines)


def format_phase1_anova(anova: dict | None) -> str:
    width = 78
    lines: list[str] = []
    lines.append("=" * width)
    if anova is None:
        lines.append("PHASE 1 — 3-way ANOVA on |human − LLM|")
        lines.append("=" * width)
        lines.append(
            "skipped (install `statsmodels` to enable per-feature attribution)"
        )
        lines.append("=" * width)
        return "\n".join(lines)
    lines.append(f"PHASE 1 — 3-way ANOVA on |human − LLM|  (n={anova['n']})")
    lines.append("=" * width)
    lines.append(f"{'source':<32} {'sum_sq':>10}  {'df':>6}  {'F':>8}  {'p':>8}")
    lines.append("-" * width)
    for r in anova["table"]:
        f_str = "       —" if r["F"] != r["F"] else f"{r['F']:>8.3f}"  # NaN check
        p_str = "       —" if r["p"] != r["p"] else f"{r['p']:>8.4f}"
        lines.append(
            f"{r['source']:<32} {r['sum_sq']:>10.3f}  "
            f"{r['df']:>6.0f}  {f_str}  {p_str}"
        )
    lines.append("=" * width)
    return "\n".join(lines)


def format_final_summary(
    scenario_metrics: dict[str, dict[str, float]],
    best_scenario_id: str,
    worst_case_id: str,
    phase2_icc: float,
    phase2_icc_ci: tuple[float, float],
    phase2_n: int,
    phase2_k: int,
    scenarios_by_id: dict,
) -> str:
    """One-page summary printed after both phases complete."""
    width = 70
    lines: list[str] = []
    lines.append("=" * width)
    lines.append("EXPERIMENT SUMMARY")
    lines.append("=" * width)

    # --- best scenario block ---
    sc = scenarios_by_id.get(best_scenario_id)
    m = scenario_metrics.get(best_scenario_id, {})

    def _yn(v: bool) -> str:
        return "yes" if v else "no"

    lines.append("")
    lines.append(f"  Best scenario   : {best_scenario_id}  ({sc.label if sc else '?'})")
    if sc:
        lines.append(f"  Structured rubric : {_yn(sc.structured_rubric)}")
        lines.append(f"  Chain-of-thought  : {_yn(sc.cot)}")
        lines.append(f"  Few-shot examples : {_yn(sc.few_shot)}")
    lines.append("")
    lines.append("  Phase 1 — accuracy (human vs LLM, n={})".format(int(m.get("n", 0))))
    lines.append(f"    MAE              : {m.get('mae', float('nan')):.2f} pts  "
                 f"({m.get('mae_normalized', float('nan')):.4f} normalised)")
    lines.append(f"    Pearson r        : {m.get('pearson', float('nan')):.3f}")
    lines.append(f"    ICC(A,1)         : {m.get('icc', float('nan')):.3f}  "
                 f"[{m.get('icc_ci_lo', float('nan')):.3f}, {m.get('icc_ci_hi', float('nan')):.3f}]")

    # --- phase 2 consistency ---
    p2_label = (
        "excellent" if phase2_icc >= 0.9
        else "good" if phase2_icc >= 0.75
        else "moderate" if phase2_icc >= 0.5
        else "poor"
    )
    lines.append("")
    lines.append(f"  Phase 2 — consistency ({phase2_n} submissions × {phase2_k} reps)")
    lines.append(f"    ICC(A,1)         : {phase2_icc:.3f}  "
                 f"(95% CI {phase2_icc_ci[0]:.3f} … {phase2_icc_ci[1]:.3f})")
    lines.append(f"    Interpretation   : {p2_label}  (Koo & Li 2016)")

    # --- ranking of all scenarios ---
    lines.append("")
    lines.append("  All scenarios ranked by MAE:")
    ranked = sorted(scenario_metrics.items(), key=lambda kv: (kv[1]["mae"], -kv[1]["pearson"]))
    for rank, (sid, sm) in enumerate(ranked, 1):
        sc_r = scenarios_by_id.get(sid)
        label_str = f"  ({sc_r.label})" if sc_r else ""
        marker = "  <-- winner" if sid == best_scenario_id else ""
        lines.append(
            f"    {rank}. {sid}{label_str:<22}  MAE {sm['mae']:.2f}  "
            f"r {sm['pearson']:.3f}  ICC {sm['icc']:.3f}{marker}"
        )

    # --- worst case ---
    lines.append("")
    lines.append(f"  Worst case for Phase 2 : {worst_case_id}")

    lines.append("")
    lines.append("=" * width)
    return "\n".join(lines)


def format_phase2_summary(
    best_scenario_id: str,
    worst_case_id: str,
    icc: float,
    icc_ci: tuple[float, float],
    n: int,
    k: int,
) -> str:
    label = (
        "excellent" if icc >= 0.9
        else "good" if icc >= 0.75
        else "moderate" if icc >= 0.5
        else "poor"
    )
    return (
        "=" * 70 + "\n"
        "PHASE 2 — consistency (winner stress test)\n"
        "=" * 70 + "\n"
        f"scenario     : {best_scenario_id}\n"
        f"worst case   : {worst_case_id}\n"
        f"matrix       : n={n} submissions × k={k} replicates\n"
        f"ICC(A,1)     : {icc:.3f}  (95% CI {icc_ci[0]:.3f} … {icc_ci[1]:.3f})\n"
        f"interpretation : {label}  (Koo & Li 2016)\n"
        "=" * 70
    )
