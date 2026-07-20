"""Accuracy and consistency metrics for the grading experiment.

Phase 1 (per scenario):
    pearson(human, llm)  — pattern alignment, range [-1, 1]
    mae(human, llm)      — absolute error, lower is better

Phase 2 (per scenario, on the shared consistency case):
    icc_a1(matrix)       — Two-Way Mixed, Absolute Agreement, single rater
                           rows = submissions, cols = repeated runs
"""

import math
from collections.abc import Sequence


def pearson(x: Sequence[float], y: Sequence[float]) -> float:
    n = len(x)
    if n != len(y) or n < 2:
        raise ValueError("x and y must have the same length, n >= 2")
    sx, sy = sum(x), sum(y)
    sxy = sum(xi * yi for xi, yi in zip(x, y))
    sxx = sum(xi * xi for xi in x)
    syy = sum(yi * yi for yi in y)
    num = n * sxy - sx * sy
    den = math.sqrt((n * sxx - sx * sx) * (n * syy - sy * sy))
    return num / den if den else 0.0


def mae(x: Sequence[float], y: Sequence[float]) -> float:
    n = len(x)
    if n != len(y) or n == 0:
        raise ValueError("x and y must have the same length, n >= 1")
    return sum(abs(xi - yi) for xi, yi in zip(x, y)) / n


def icc_a1(matrix: Sequence[Sequence[float]]) -> float:
    """ICC(A,1) — Two-Way Mixed, Absolute Agreement, single rater.

    matrix: rows = subjects (submissions), cols = runs (replicates).
    Requires a balanced matrix (every row has the same number of columns).
    """
    n = len(matrix)
    if n < 2:
        raise ValueError("need n >= 2 subjects (rows)")
    k = len(matrix[0])
    if k < 2:
        raise ValueError("need k >= 2 runs (columns)")
    if any(len(row) != k for row in matrix):
        raise ValueError("matrix must be balanced (all rows same length)")

    grand = sum(sum(row) for row in matrix) / (n * k)
    row_means = [sum(row) / k for row in matrix]
    col_means = [sum(matrix[i][j] for i in range(n)) / n for j in range(k)]

    ss_rows = k * sum((rm - grand) ** 2 for rm in row_means)
    ss_cols = n * sum((cm - grand) ** 2 for cm in col_means)
    ss_total = sum(
        (matrix[i][j] - grand) ** 2 for i in range(n) for j in range(k)
    )
    ss_error = ss_total - ss_rows - ss_cols

    ms_bs = ss_rows / (n - 1)
    ms_bm = ss_cols / (k - 1)
    ms_e = ss_error / ((n - 1) * (k - 1))

    num = ms_bs - ms_e
    den = ms_bs + (k - 1) * ms_e + (k / n) * (ms_bm - ms_e)
    return num / den if den else 0.0
