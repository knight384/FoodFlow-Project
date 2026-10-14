"""
Forecasting evaluation harness (ML & Testing Plan v1.0 Sections 6.3, 7).

Implements the selection PROCESS documented in ML & Testing Plan v1.0
Section 6.3:
    1. Establish baseline (algorithm.recent_period_mean).
    2. Prepare data (preprocessing.get_historical_series).
    3. Time-based train/evaluation split (NOT random — forecasting is
       time-ordered; Section 6.3 step 3).
    4. Fit/apply candidates on the training portion.
    5. Evaluate against the held-out portion using MAE/MAPE (Section 7).
    6. Compare — see algorithm.py's module docstring for the actual
       result and selection.

This module is reusable both for the one-time model-selection exercise
(documented in algorithm.py and the Phase 5 verification report) and as
a regression check (tests/test_forecasting.py asserts the baseline
continues to perform at least as well as the candidate on the seeded
demo dataset — protecting the documented selection rationale from
silently going stale).
"""

import statistics
from dataclasses import dataclass
from datetime import date as date_type

from app.modules.forecasting.algorithm import day_of_week_seasonal_mean, recent_period_mean

DEFAULT_TRAIN_SPLIT_RATIO = 0.8


@dataclass
class EvaluationResult:
    baseline_mae: float
    candidate_mae: float
    baseline_mape: float
    candidate_mape: float
    n_evaluated: int


def _mae(errors: list[float]) -> float:
    return statistics.mean(abs(e) for e in errors) if errors else float("nan")


def _mape(pairs: list[tuple[float, float]]) -> float:
    """
    Skips pairs where the actual value is 0 (percentage error is
    undefined there) — the same documented limitation noted for the
    Comparison module's zero-forecast edge case (ML & Testing Plan v1.0
    Section 7.2).
    """
    values = [abs((actual - predicted) / actual) * 100 for actual, predicted in pairs if actual != 0]
    return statistics.mean(values) if values else float("nan")


def evaluate_series(
    series: list[tuple[date_type, float]],
    window: int,
    train_split_ratio: float = DEFAULT_TRAIN_SPLIT_RATIO,
) -> EvaluationResult | None:
    """
    Evaluates baseline vs. candidate on a single (location, meal type)
    series using a time-based split. Returns None if the series is too
    short to produce a meaningful held-out evaluation portion (fewer
    than 2 points on either side of the split).
    """
    series_sorted = sorted(series, key=lambda r: r[0])
    split_index = int(len(series_sorted) * train_split_ratio)
    train = series_sorted[:split_index]
    holdout = series_sorted[split_index:]

    if len(train) < 2 or len(holdout) < 2:
        return None

    baseline_errors: list[float] = []
    candidate_errors: list[float] = []
    baseline_pairs: list[tuple[float, float]] = []
    candidate_pairs: list[tuple[float, float]] = []

    for eval_date, actual in holdout:
        baseline_pred = recent_period_mean(train, window)
        candidate_pred = day_of_week_seasonal_mean(train, eval_date, window)

        baseline_errors.append(actual - baseline_pred)
        candidate_errors.append(actual - candidate_pred)
        baseline_pairs.append((actual, baseline_pred))
        candidate_pairs.append((actual, candidate_pred))

    return EvaluationResult(
        baseline_mae=_mae(baseline_errors),
        candidate_mae=_mae(candidate_errors),
        baseline_mape=_mape(baseline_pairs),
        candidate_mape=_mape(candidate_pairs),
        n_evaluated=len(holdout),
    )


def evaluate_all_series(
    series_by_key: dict[tuple, list[tuple[date_type, float]]],
    window: int,
    train_split_ratio: float = DEFAULT_TRAIN_SPLIT_RATIO,
) -> EvaluationResult | None:
    """
    Aggregates baseline-vs-candidate evaluation across multiple series
    (e.g., every (location, meal type) combination with sufficient
    demo data), matching how the documented Phase 5 comparison was
    produced.
    """
    all_baseline_errors: list[float] = []
    all_candidate_errors: list[float] = []
    all_baseline_pairs: list[tuple[float, float]] = []
    all_candidate_pairs: list[tuple[float, float]] = []

    for series in series_by_key.values():
        series_sorted = sorted(series, key=lambda r: r[0])
        split_index = int(len(series_sorted) * train_split_ratio)
        train = series_sorted[:split_index]
        holdout = series_sorted[split_index:]
        if len(train) < 2 or len(holdout) < 2:
            continue

        for eval_date, actual in holdout:
            baseline_pred = recent_period_mean(train, window)
            candidate_pred = day_of_week_seasonal_mean(train, eval_date, window)
            all_baseline_errors.append(actual - baseline_pred)
            all_candidate_errors.append(actual - candidate_pred)
            all_baseline_pairs.append((actual, baseline_pred))
            all_candidate_pairs.append((actual, candidate_pred))

    if not all_baseline_errors:
        return None

    return EvaluationResult(
        baseline_mae=_mae(all_baseline_errors),
        candidate_mae=_mae(all_candidate_errors),
        baseline_mape=_mape(all_baseline_pairs),
        candidate_mape=_mape(all_candidate_pairs),
        n_evaluated=len(all_baseline_errors),
    )
