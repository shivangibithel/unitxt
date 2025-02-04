from functools import singledispatch
from typing import List, Optional

import pandas as pd

from .operator import SequentialOperator
from .stream import MultiStream


@singledispatch
def evaluate(
    dataset, metric_names: List[str], compute_conf_intervals: Optional[bool] = False
):
    """Placeholder for overloading the function, supporting both dataframe input and list input."""
    pass


@evaluate.register
def _(
    dataset: list,
    metric_names: List[str],
    compute_conf_intervals: Optional[bool] = False,
):
    global_scores = {}
    for metric_name in metric_names:
        multi_stream = MultiStream.from_iterables({"test": dataset}, copying=True)
        metrics_operator = SequentialOperator(steps=[metric_name])

        if not compute_conf_intervals:
            first_step = metrics_operator.steps[0]
            n_resamples = first_step.disable_confidence_interval_calculation()

        instances = list(metrics_operator(multi_stream)["test"])
        for entry, instance in zip(dataset, instances):
            entry[metric_name] = instance["score"]["instance"]["score"]

        if len(instances) > 0:
            global_scores[metric_name] = instances[0]["score"].get("global", {})

        # To overcome issue #325: the modified metric artifact is cached and
        # a sequential retrieval of an artifact with the same name will
        # retrieve the metric with the previous modification.
        # This reverts the confidence interval change and restores the initial metric.
        if not compute_conf_intervals:
            first_step.set_n_resamples(n_resamples)

    return dataset, global_scores


@evaluate.register
def _(
    dataset: pd.DataFrame,
    metric_names: List[str],
    compute_conf_intervals: Optional[bool] = False,
):
    results, global_scores = evaluate(
        dataset.to_dict("records"),
        metric_names=metric_names,
        compute_conf_intervals=compute_conf_intervals,
    )
    return pd.DataFrame(results), pd.DataFrame(global_scores)
