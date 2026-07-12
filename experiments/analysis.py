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
        out.setdefault(key, []).append((float(sub["human_score"]), float(row["score"])))
    return out


def compute_phase1_metrics(
    phase1_rows: list[dict],
    submissions_by_id: dict[str, dict],
) -> dict[str, dict[str, float]]:
    """Per-scenario accuracy metrics over (human, LLM) pairs.

    Returns {scenario_id: {n, n_total, schema_valid_rate, mae, mae_normalized,
    pearson, icc, icc_ci_lo, icc_ci_hi}}.

    `n` is the number of schema-valid rows that fed into MAE/Pearson/ICC.
    `n_total` is the number of rows attempted for the scenario (valid + invalid).
    `schema_valid_rate` is n / n_total — a deployability metric measuring how
    often the prompt produces parseable output. A prompt that grades accurately
    but fails to parse 30% of the time is a worse production prompt than one
    that fails 5%, even if MAE looks similar on the valid subset.
    """
    pairs = per_scenario_pairs(phase1_rows, submissions_by_id)

    # Per-scenario totals (including invalid rows) for the schema_valid_rate.
    totals: dict[str, int] = {}
    for row in phase1_rows:
        sid = row.get("scenario_id")
        if not sid:
            continue
        totals[sid] = totals.get(sid, 0) + 1

    out: dict[str, dict[str, float]] = {}
    seen = set(pairs) | set(totals)
    for scenario_id in seen:
        pp = pairs.get(scenario_id, [])
        n_valid = len(pp)
        n_total = totals.get(scenario_id, n_valid)
        if pp:
            humans = [h for h, _ in pp]
            llms = [l for _, l in pp]
            mae_val = metrics.mae(humans, llms)
            pearson_val = metrics.pearson(humans, llms)
            matrix = [[h, l] for h, l in pp]
            if len(pp) >= 2:
                icc, (ci_lo, ci_hi) = compute_icc(matrix)
            else:
                icc, ci_lo, ci_hi = float("nan"), float("nan"), float("nan")
        else:
            mae_val = float("nan")
            pearson_val = float("nan")
            icc, ci_lo, ci_hi = float("nan"), float("nan"), float("nan")
        out[scenario_id] = {
            "n": n_valid,
            "n_total": n_total,
            "schema_valid_rate": (n_valid / n_total) if n_total else float("nan"),
            "mae": mae_val,
            "mae_normalized": mae_val / 100.0 if mae_val == mae_val else float("nan"),
            "pearson": pearson_val,
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

    # Residual SS is the denominator of partial eta-squared. Located as the
    # "Residual" row in statsmodels' anova_lm output.
    residual_ss = 0.0
    for source, r in table.iterrows():
        if str(source).lower() == "residual":
            residual_ss = float(r["sum_sq"])
            break

    rows_out: list[dict] = []
    for source, r in table.iterrows():
        ss = float(r["sum_sq"])
        is_residual = str(source).lower() == "residual"
        # partial η² = SS_effect / (SS_effect + SS_residual)
        if is_residual or (ss + residual_ss) == 0:
            partial_eta = float("nan")
        else:
            partial_eta = ss / (ss + residual_ss)
        rows_out.append(
            {
                "source": str(source),
                "sum_sq": ss,
                "df": float(r["df"]),
                "F": float(r["F"]) if not pd.isna(r["F"]) else float("nan"),
                "p": float(r["PR(>F)"]) if not pd.isna(r["PR(>F)"]) else float("nan"),
                "partial_eta_sq": partial_eta,
            }
        )
    return {"n": int(len(df)), "table": rows_out}


# Parse rate threshold below which a scenario is considered undeployable and
# disqualified from the composite ranking. Picked at 0.90 to encode the
# deployment reality that ≥10% parse failure rate is operationally unusable.
# Disqualified scenarios still appear in the ranking but are sorted below all
# survivors via a large penalty.
PARSE_RATE_FLOOR = 0.90

# Weights for the z-scored components among parse-floor survivors. MAE is
# weighted 2× Pearson because absolute grading error is the primary accuracy
# signal — Pearson captures ordering alignment as a secondary check. With
# this weighting, a 1σ improvement on MAE counts twice as much as a 1σ
# improvement on Pearson r.
MAE_WEIGHT = 2.0
PEARSON_WEIGHT = 1.0

# Penalty added to disqualified scenarios' composite. Chosen large enough that
# any survivor (whose weighted z-score sum lies in roughly [-5, +5]) outranks
# any disqualified scenario, while still preserving relative ordering among
# disqualified scenarios via their underlying z-scores.
_DISQUALIFICATION_PENALTY = 100.0


def _composite_stats(
    scenario_metrics: dict[str, dict[str, float]],
) -> dict[str, tuple[float, float]] | None:
    """Compute (mean, std) of MAE and Pearson penalty across parse-floor survivors.

    Statistics are derived **only from scenarios that pass the
    `PARSE_RATE_FLOOR` deployability gate** — because the composite ranking
    is fundamentally about choosing among deployable candidates. Including
    sub-threshold scenarios in the z-score baseline would distort the
    comparison among the actually-usable scenarios.

    Falls back to all rankable scenarios if no scenario passes the floor
    (e.g. early during development before any prompt is mature).

    Returns `None` if no scenarios are rankable at all.
    """
    rankable = [
        m for m in scenario_metrics.values()
        if m.get("n", 0) > 0 and m["mae"] == m["mae"]
    ]
    if not rankable:
        return None
    survivors = [
        m for m in rankable
        if m.get("schema_valid_rate", 0.0) >= PARSE_RATE_FLOOR
    ]
    pool = survivors if survivors else rankable
    n = len(pool)
    mae_vals = [m["mae"] / 100.0 for m in pool]
    pearson_vals = [
        1.0 - m.get("pearson", 0.0)
        if m.get("pearson", 0.0) == m.get("pearson", 0.0)
        else 0.0
        for m in pool
    ]

    def _mean_std(vals: list[float]) -> tuple[float, float]:
        if n < 2:
            return (sum(vals) / n if n else 0.0, 1.0)
        mean = sum(vals) / n
        var = sum((v - mean) ** 2 for v in vals) / (n - 1)
        std = math.sqrt(var)
        # Guard against zero std (all scenarios identical on this axis) —
        # z would be undefined; std=1 makes that component contribute 0.
        return (mean, std if std > 1e-12 else 1.0)

    return {
        "mae": _mean_std(mae_vals),
        "pearson": _mean_std(pearson_vals),
        "n_survivors": (float(len(survivors)), 0.0),  # carried for the formatter
    }


def composite_score(
    m: dict[str, float],
    stats: dict[str, tuple[float, float]] | None = None,
) -> float:
    """Single source of truth for the scenario-picker composite (lower = better).

    Two-tier selection logic:

    1. **Parse rate is a hard deployability gate.** Scenarios with
       `parse_rate < PARSE_RATE_FLOOR` (default 0.90) are disqualified —
       their composite gets a large penalty so any survivor outranks them.
       This encodes the production reality that a prompt failing to parse
       >10% of the time is operationally unusable regardless of its
       accuracy on the parses that succeed.

    2. **Among survivors, MAE is weighted 2× Pearson** in a z-score-normalised
       sum. MAE is the primary accuracy signal; Pearson is a secondary
       ordering check. A 1σ improvement on MAE counts twice as much as a
       1σ improvement on Pearson r.

    Formula::

        if parse_rate < PARSE_RATE_FLOOR:
            composite = _DISQUALIFICATION_PENALTY + (floor − parse_rate)·10
                        + (MAE_WEIGHT · z_mae + PEARSON_WEIGHT · z_pearson)
        else:
            composite = MAE_WEIGHT · z_mae + PEARSON_WEIGHT · z_pearson

    Among survivors the composite typically lies in roughly [-5, +5] —
    negative = better than the survivor-cohort average on the weighted sum.

    If `stats` is None, falls back to a raw normalised sum (used when only
    a single scenario is being scored, where z-scoring is undefined).

    Returns `+inf` for scenarios that cannot be ranked (no valid rows / NaN MAE).
    """
    if m.get("n", 0) == 0 or m["mae"] != m["mae"]:  # NaN check
        return float("inf")
    mae_norm = m["mae"] / 100.0
    parse_rate = m.get("schema_valid_rate", 0.0)
    pearson = m.get("pearson", float("nan"))
    pearson_penalty = (1.0 - pearson) if pearson == pearson else 0.0

    if stats is None:
        # Fallback for single-scenario scoring — no cohort to z-score against.
        return (
            MAE_WEIGHT * mae_norm
            + (1.0 - parse_rate)
            + PEARSON_WEIGHT * pearson_penalty
        )

    mae_mean, mae_std = stats["mae"]
    pearson_mean, pearson_std = stats["pearson"]
    z_mae = (mae_norm - mae_mean) / mae_std
    z_pearson = (pearson_penalty - pearson_mean) / pearson_std
    base = MAE_WEIGHT * z_mae + PEARSON_WEIGHT * z_pearson

    if parse_rate < PARSE_RATE_FLOOR:
        # Disqualified. Large penalty pushes below any survivor;
        # the gap-below-floor term preserves ordering among disqualified.
        return base + _DISQUALIFICATION_PENALTY + (PARSE_RATE_FLOOR - parse_rate) * 10
    return base


def pick_best_scenario(scenario_metrics: dict[str, dict[str, float]]) -> str:
    """Pick the best scenario by the composite quality score (lower = better).

    See `composite_score` for the formula. Scenarios with no valid rows (n=0)
    are excluded — they cannot be ranked.
    """
    rankable = {
        s: m for s, m in scenario_metrics.items()
        if m["n"] > 0 and m["mae"] == m["mae"]  # exclude n=0 / NaN MAE
    }
    if not rankable:
        raise ValueError("No scenarios with valid rows to pick from.")
    stats = _composite_stats(scenario_metrics)
    return min(rankable, key=lambda s: composite_score(rankable[s], stats))


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
    min_replicates: int = 2,
) -> tuple[list[list[float]], list[str]]:
    """Build an n×k matrix of LLM scores from Phase 2 rows.

    Rows = submissions (sorted by submission_id), columns = replicate index.
    Returns (matrix, submission_ids).

    Replicates may have schema-invalid rows that are excluded. The matrix is
    built with k = (median number of valid replicates per submission) and
    submissions that have at least k valid replicates contribute their first
    k. Submissions with fewer than `min_replicates` valid reps are dropped —
    a row with only one valid score has no variance to contribute.
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

    counts = sorted(len(by_submission[s]) for s in submission_ids)
    # Pick the largest k such that the majority of submissions have at least k.
    # Walking from full down: prefer balanced higher-k over unbalanced lower-k.
    k = 0
    for candidate in range(counts[-1], min_replicates - 1, -1):
        eligible = sum(1 for c in counts if c >= candidate)
        if eligible >= max(2, len(counts) // 2):
            k = candidate
            break
    if k == 0:
        logger.warning(
            "Phase 2 has too few replicates per submission to compute ICC "
            "(max=%d, min=%d, min_replicates=%d)",
            counts[-1], counts[0], min_replicates,
        )
        return [], []

    matrix: list[list[float]] = []
    keep_ids: list[str] = []
    dropped: list[tuple[str, int]] = []
    for sid in submission_ids:
        row_dict = by_submission[sid]
        if len(row_dict) < k:
            dropped.append((sid, len(row_dict)))
            continue
        # Use the lowest k replicate indices that this submission has.
        ordered_reps = sorted(row_dict.keys())[:k]
        matrix.append([row_dict[r] for r in ordered_reps])
        keep_ids.append(sid)

    if dropped:
        logger.warning(
            "Phase 2 — dropped %d submission(s) with <%d valid replicates "
            "from ICC matrix: %s",
            len(dropped), k, ", ".join(f"{s}({c})" for s, c in dropped[:5]),
        )
    logger.info(
        "Phase 2 — ICC matrix built: %d submissions × %d replicates", len(matrix), k,
    )
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


def compute_timing_stats(
    rows: list[dict],
) -> dict[str, dict]:
    """Compute per-scenario latency stats from Phase 1 rows.

    Only rows with a non-null ``latency_ms`` field are included.  Returns a
    dict keyed by scenario_id; also includes a ``"__phase2__"`` key when
    called on Phase 2 rows (which have a single scenario).

    Each value has:
        n          – number of timed rows
        mean_ms    – arithmetic mean latency in ms
        p50_ms     – median
        p95_ms     – 95th-percentile
        total_ms   – sum (wall time if all requests ran serially)
        total_min  – total_ms / 60_000
    """
    by_scenario: dict[str, list[float]] = {}
    for row in rows:
        lat = row.get("latency_ms")
        if lat is None:
            continue
        sid = row.get("scenario_id") or "__phase2__"
        by_scenario.setdefault(sid, []).append(float(lat))

    out: dict[str, dict] = {}
    for sid, lats in by_scenario.items():
        lats_s = sorted(lats)
        n = len(lats_s)
        out[sid] = {
            "n": n,
            "mean_ms": sum(lats_s) / n,
            "p50_ms": lats_s[n // 2],
            "p95_ms": lats_s[min(int(0.95 * n), n - 1)],
            "total_ms": sum(lats_s),
            "total_min": sum(lats_s) / 60_000,
        }
    return out


def format_phase1_table(
    scenario_metrics: dict[str, dict[str, float]],
    case_avg_mae: dict[str, float],
    best_scenario_id: str,
    worst_case_id: str,
    timing_stats: dict[str, dict] | None = None,
) -> str:
    width = 108
    lines = []
    lines.append("=" * width)
    lines.append("PHASE 1 — accuracy + deployability")
    lines.append("=" * width)
    header = (
        f"{'scenario':<10} {'n/total':>9}  {'parse%':>7}  {'MAE':>7}  "
        f"{'Pearson':>8}  {'ICC(A,1)':>9}  {'ICC 95% CI':<19}"
    )
    lines.append(header)
    lines.append("-" * width)
    for sid in sorted(scenario_metrics):
        m = scenario_metrics[sid]
        marker = "  <-- best" if sid == best_scenario_id else ""
        ci = f"[{m['icc_ci_lo']:.3f}, {m['icc_ci_hi']:.3f}]"
        n_total = int(m.get("n_total", m["n"]))
        parse_rate = m.get("schema_valid_rate", float("nan")) * 100
        mae_str = (
            f"{m['mae']:>7.3f}" if m["mae"] == m["mae"] else f"{'—':>7}"
        )
        pearson_str = (
            f"{m['pearson']:>8.3f}" if m["pearson"] == m["pearson"] else f"{'—':>8}"
        )
        icc_str = (
            f"{m['icc']:>9.3f}" if m["icc"] == m["icc"] else f"{'—':>9}"
        )
        lines.append(
            f"{sid:<10} {int(m['n']):>4}/{n_total:<4}  {parse_rate:>6.1f}%  "
            f"{mae_str}  {pearson_str}  {icc_str}  {ci:<19}{marker}"
        )
    lines.append("")
    lines.append(f"{'case':<10} {'avg MAE':>10}")
    lines.append("-" * width)
    for pid in sorted(case_avg_mae):
        marker = "  <-- worst" if pid == worst_case_id else ""
        lines.append(f"{pid:<10} {case_avg_mae[pid]:>10.3f}{marker}")

    if timing_stats:
        lines.append("")
        lines.append("PHASE 1 — per-inference latency  (direct mode only; null for batch)")
        lines.append("-" * width)
        t_header = (
            f"{'scenario':<10} {'n_timed':>8}  {'mean ms':>8}  {'p50 ms':>7}  "
            f"{'p95 ms':>7}  {'total min':>10}  {'serial wall':>12}"
        )
        lines.append(t_header)
        lines.append("-" * width)
        for sid in sorted(timing_stats):
            if sid == "__phase2__":
                continue
            t = timing_stats[sid]
            lines.append(
                f"{sid:<10} {t['n']:>8}  {t['mean_ms']:>8.0f}  {t['p50_ms']:>7.0f}  "
                f"{t['p95_ms']:>7.0f}  {t['total_min']:>10.1f}  "
                f"{'(serial sum)':>12}"
            )
        all_total_ms = sum(
            t["total_ms"] for sid, t in timing_stats.items() if sid != "__phase2__"
        )
        lines.append("-" * width)
        lines.append(
            f"{'TOTAL':<10} {'':>8}  {'':>8}  {'':>7}  {'':>7}  "
            f"{all_total_ms/60_000:>10.1f}  {'(all 8 sc.)':>12}"
        )

    lines.append("=" * width)
    return "\n".join(lines)


def _significance_marker(p: float) -> str:
    """Star markers for ANOVA p-values (standard convention)."""
    if p != p:  # NaN
        return ""
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    if p < 0.1:
        return "."
    return "ns"


def _eta_sq_label(eta: float) -> str:
    """Cohen (1988) effect size buckets for partial η²."""
    if eta != eta:
        return ""
    if eta < 0.01:
        return "trivial"
    if eta < 0.06:
        return "small"
    if eta < 0.14:
        return "medium"
    return "large"


def _summarize_anova(anova: dict) -> list[str]:
    """Group ANOVA sources by significance and produce a plain-language summary.

    Returns a list of indented lines ready to append to the summary. Splits
    sources into:
      - significant main effects (p < 0.05, no ":" in name)
      - significant interactions (p < 0.05, contains ":")
      - non-significant (p ≥ 0.05)
    Then emits a one-line "key finding" naming the most influential factors.
    """
    sig_main: list[tuple[str, float, float, float]] = []  # (name, F, p, η²p)
    sig_inter: list[tuple[str, float, float, float]] = []
    nonsig: list[str] = []
    for r in anova.get("table", []):
        name = str(r["source"])
        if name.lower() == "residual":
            continue
        if r["F"] != r["F"]:
            continue
        clean = name.replace("C(", "").replace(")", "")
        p = r["p"]
        eta = r.get("partial_eta_sq", float("nan"))
        entry = (clean, r["F"], p, eta)
        if p != p:
            nonsig.append(clean)
        elif p < 0.05:
            (sig_inter if ":" in clean else sig_main).append(entry)
        else:
            nonsig.append(clean)

    out: list[str] = []
    if sig_main:
        names = ", ".join(
            f"{n} ({_significance_marker(p)}, η²p={eta:.3f})"
            for n, _f, p, eta in sig_main
        )
        out.append(f"      Significant main effects : {names}")
    else:
        out.append("      Significant main effects : (none)")

    if sig_inter:
        names = ", ".join(
            f"{n} ({_significance_marker(p)}, η²p={eta:.3f})"
            for n, _f, p, eta in sig_inter
        )
        out.append(f"      Significant interactions : {names}")

    if nonsig:
        out.append(f"      No measurable effect     : {', '.join(nonsig)}")

    # Key-finding one-liner: name the largest significant effect by η²p.
    all_sig = sig_main + sig_inter
    if all_sig:
        all_sig.sort(key=lambda t: -(t[3] if t[3] == t[3] else 0))
        top = all_sig[0]
        out.append(
            f"      Key finding              : "
            f"MAE reduction primarily attributable to "
            f"{', '.join(n for n, _f, _p, _e in all_sig)}"
        )
        if not sig_inter:
            out.append(
                "      (no significant interactions → factors act independently)"
            )
    else:
        out.append(
            "      Key finding              : no factor produced a "
            "statistically detectable effect"
        )
    return out


def format_phase1_anova(anova: dict | None) -> str:
    width = 96
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
    lines.append(
        f"{'source':<32} {'sum_sq':>10}  {'df':>6}  {'F':>8}  "
        f"{'p':>8}  {'sig':<4} {'η²p':>6}  {'effect':<8}"
    )
    lines.append("-" * width)
    for r in anova["table"]:
        f_str = "       —" if r["F"] != r["F"] else f"{r['F']:>8.3f}"
        p_str = "       —" if r["p"] != r["p"] else f"{r['p']:>8.4f}"
        sig = _significance_marker(r["p"])
        eta = r.get("partial_eta_sq", float("nan"))
        eta_str = "    —" if eta != eta else f"{eta:>6.3f}"
        eta_label = _eta_sq_label(eta)
        lines.append(
            f"{r['source']:<32} {r['sum_sq']:>10.3f}  "
            f"{r['df']:>6.0f}  {f_str}  {p_str}  {sig:<4} {eta_str}  {eta_label:<8}"
        )
    lines.append("-" * width)
    lines.append(
        "  sig codes: *** p<0.001  ** p<0.01  * p<0.05  . p<0.1  ns p≥0.1"
    )
    lines.append(
        "  η²p (partial eta²) effect size: trivial <0.01  small <0.06  "
        "medium <0.14  large ≥0.14"
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
    phase1_timing: dict[str, dict] | None = None,
    phase2_timing: dict[str, dict] | None = None,
    anova: dict | None = None,
    temperatures: list[float] | None = None,
) -> str:
    """One-page summary printed after both phases complete.

    `temperatures` is the set of distinct sampling temperatures recorded in
    the result rows (see runner `_row_from_response`). A single value means a
    clean run; multiple values flag rows graded under different temperatures.
    """
    width = 70
    lines: list[str] = []
    lines.append("=" * width)
    lines.append("EXPERIMENT SUMMARY")
    lines.append("=" * width)

    # --- run provenance: sampling temperature ---
    # Key for these experiments: a temp=0 run is deterministic (consistency
    # trivially perfect), so the Phase 2 ICC is only meaningful at temp>0.
    if temperatures:
        temp_str = ", ".join(f"{t:g}" for t in temperatures)
        if len(temperatures) > 1:
            temp_str += "  (⚠ mixed across rows)"
    else:
        temp_str = "unrecorded (run predates temperature logging)"
    lines.append("")
    lines.append(f"  Sampling temperature : {temp_str}")

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

    # --- Composite picker config (transparency for thesis defense) ---
    lines.append("")
    lines.append("  Composite picker config (how the winner was chosen):")
    lines.append(
        f"    Parse rate floor : ≥ {PARSE_RATE_FLOOR*100:.0f}%  "
        f"(deployability gate — sub-floor scenarios disqualified)"
    )
    lines.append(
        f"    Weights          : MAE×{MAE_WEIGHT:g}  +  (1−r)×{PEARSON_WEIGHT:g}  "
        f"on z-scored values across survivors"
    )
    lines.append(
        f"    Formula          : {MAE_WEIGHT:g}·z_MAE + {PEARSON_WEIGHT:g}·z_(1−r); "
        f"lower z = better"
    )
    lines.append("")
    lines.append(
        "  Phase 1 — accuracy + deployability (n={}/{} parsed)".format(
            int(m.get("n", 0)), int(m.get("n_total", m.get("n", 0)))
        )
    )
    lines.append(
        f"    Parse rate       : {m.get('schema_valid_rate', float('nan')) * 100:.1f}%"
    )
    lines.append(
        f"    MAE              : {m.get('mae', float('nan')):.2f} pts  "
        f"({m.get('mae_normalized', float('nan')):.4f} normalised)"
    )
    lines.append(f"    Pearson r        : {m.get('pearson', float('nan')):.3f}")
    lines.append(
        f"    ICC(A,1)         : {m.get('icc', float('nan')):.3f}  "
        f"[{m.get('icc_ci_lo', float('nan')):.3f}, {m.get('icc_ci_hi', float('nan')):.3f}]"
    )

    # --- phase 2 consistency ---
    p2_label = (
        "excellent"
        if phase2_icc >= 0.9
        else (
            "good"
            if phase2_icc >= 0.75
            else "moderate" if phase2_icc >= 0.5 else "poor"
        )
    )
    lines.append("")
    lines.append(f"  Phase 2 — consistency ({phase2_n} submissions × {phase2_k} reps)")
    lines.append(
        f"    ICC(A,1)         : {phase2_icc:.3f}  "
        f"(95% CI {phase2_icc_ci[0]:.3f} … {phase2_icc_ci[1]:.3f})"
    )
    lines.append(f"    Interpretation   : {p2_label}  (Koo & Li 2016)")

    # --- ranking of all scenarios ---
    stats = _composite_stats(scenario_metrics)
    floor_pct = int(PARSE_RATE_FLOOR * 100)
    lines.append("")
    lines.append(
        f"  All scenarios ranked by composite (parse_rate ≥ {floor_pct}% gate; "
        f"then {MAE_WEIGHT:g}·z_MAE + {PEARSON_WEIGHT:g}·z_(1−r); lower = better):"
    )
    ranked = sorted(
        scenario_metrics.items(),
        key=lambda kv: composite_score(kv[1], stats),
    )
    for rank, (sid, sm) in enumerate(ranked, 1):
        sc_r = scenarios_by_id.get(sid)
        label_str = f"  ({sc_r.label})" if sc_r else ""
        marker = "  <-- winner" if sid == best_scenario_id else ""
        parse_pct = sm.get("schema_valid_rate", float("nan")) * 100
        mae_str = f"{sm['mae']:.2f}" if sm["mae"] == sm["mae"] else "—"
        r_str = f"{sm['pearson']:.3f}" if sm["pearson"] == sm["pearson"] else "—"
        icc_str = f"{sm['icc']:.3f}" if sm["icc"] == sm["icc"] else "—"
        comp = composite_score(sm, stats)
        # Distinguish disqualified scenarios visually.
        disqualified = (
            sm.get("schema_valid_rate", 0.0) < PARSE_RATE_FLOOR
            and sm.get("n", 0) > 0
        )
        if comp == float("inf"):
            comp_str = "—"
        elif disqualified:
            comp_str = "disqual."
        else:
            comp_str = f"{comp:+.3f}"
        lines.append(
            f"    {rank}. {sid}{label_str:<22}  parse {parse_pct:>5.1f}%  "
            f"MAE {mae_str}  r {r_str}  ICC {icc_str}  z {comp_str}{marker}"
        )

    # --- ANOVA: per-factor attribution of grading error ---
    if anova and anova.get("table"):
        lines.append("")
        lines.append(
            f"  3-way ANOVA on |human − LLM|  (n={anova['n']}, factors: "
            f"rubric × cot × fewshot)"
        )
        # Pretty-print each non-residual source with significance + effect size.
        # Skip rows where everything is NaN (single-level / un-fittable).
        rendered_any = False
        for r in anova["table"]:
            if str(r["source"]).lower() == "residual":
                continue
            if r["F"] != r["F"]:
                continue
            sig = _significance_marker(r["p"])
            eta = r.get("partial_eta_sq", float("nan"))
            eta_str = "—" if eta != eta else f"{eta:.3f}"
            eta_label = _eta_sq_label(eta)
            # Trim C(...) wrapper for readability.
            src = r["source"].replace("C(", "").replace(")", "")
            lines.append(
                f"    {src:<26}  F={r['F']:>7.2f}  p={r['p']:>7.4f} {sig:<4}  "
                f"η²p={eta_str:<6}  ({eta_label})"
            )
            rendered_any = True
        if rendered_any:
            lines.append(
                "    legend: *** p<0.001  ** p<0.01  * p<0.05  . p<0.1  ns p≥0.1"
            )
            lines.append("")
            lines.append("    Interpretation:")
            lines.extend(_summarize_anova(anova))

    # --- timing ---
    if phase1_timing or phase2_timing:
        lines.append("")
        lines.append("  Timing  (direct mode only; null = batch / old run)")
        if phase1_timing:
            best_t = phase1_timing.get(best_scenario_id)
            all_p1_total_ms = sum(
                t["total_ms"]
                for sid, t in phase1_timing.items()
                if sid != "__phase2__"
            )
            lines.append("    Phase 1 (all scenarios, serial):")
            lines.append(f"      Total wall time    : {all_p1_total_ms/60_000:.1f} min")
            if best_t:
                lines.append(
                    f"    Winner ({best_scenario_id}) per-request:"
                )
                lines.append(
                    f"      mean {best_t['mean_ms']:.0f} ms  "
                    f"p50 {best_t['p50_ms']:.0f} ms  "
                    f"p95 {best_t['p95_ms']:.0f} ms  "
                    f"(n={best_t['n']})"
                )
        if phase2_timing:
            p2t = phase2_timing.get("__phase2__") or next(iter(phase2_timing.values()), None)
            if p2t:
                lines.append("    Phase 2 per-request:")
                lines.append(
                    f"      mean {p2t['mean_ms']:.0f} ms  "
                    f"p50 {p2t['p50_ms']:.0f} ms  "
                    f"p95 {p2t['p95_ms']:.0f} ms  "
                    f"total {p2t['total_min']:.1f} min  (n={p2t['n']})"
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
    timing_stats: dict[str, dict] | None = None,
) -> str:
    label = (
        "excellent"
        if icc >= 0.9
        else "good" if icc >= 0.75 else "moderate" if icc >= 0.5 else "poor"
    )
    lines = [
        "=" * 70,
        "PHASE 2 — consistency (winner stress test)",
        "=" * 70,
        f"scenario     : {best_scenario_id}",
        f"worst case   : {worst_case_id}",
        f"matrix       : n={n} submissions × k={k} replicates",
        f"ICC(A,1)     : {icc:.3f}  (95% CI {icc_ci[0]:.3f} … {icc_ci[1]:.3f})",
        f"interpretation : {label}  (Koo & Li 2016)",
    ]
    if timing_stats:
        t = timing_stats.get("__phase2__") or next(iter(timing_stats.values()), None)
        if t:
            lines.append(
                f"latency      : mean {t['mean_ms']:.0f} ms  "
                f"p50 {t['p50_ms']:.0f} ms  "
                f"p95 {t['p95_ms']:.0f} ms  "
                f"total {t['total_min']:.1f} min  (n={t['n']} timed)"
            )
    lines.append("=" * 70)
    return "\n".join(lines)
