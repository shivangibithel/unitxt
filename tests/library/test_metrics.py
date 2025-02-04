from math import isnan

from src.unitxt.logging_utils import get_logger
from src.unitxt.metrics import (
    Accuracy,
    F1Macro,
    F1MacroMultiLabel,
    F1Micro,
    F1MicroMultiLabel,
    F1Weighted,
    FixedGroupAbsvalNormCohensHParaphraseAccuracy,
    FixedGroupAbsvalNormCohensHParaphraseStringContainment,
    FixedGroupAbsvalNormHedgesGParaphraseAccuracy,
    FixedGroupAbsvalNormHedgesGParaphraseStringContainment,
    FixedGroupMeanAccuracy,
    FixedGroupMeanBaselineAccuracy,
    FixedGroupMeanBaselineStringContainment,
    FixedGroupMeanParaphraseAccuracy,
    FixedGroupMeanParaphraseStringContainment,
    FixedGroupMeanStringContainment,
    FixedGroupNormCohensHParaphraseAccuracy,
    FixedGroupNormCohensHParaphraseStringContainment,
    FixedGroupNormHedgesGParaphraseAccuracy,
    FixedGroupNormHedgesGParaphraseStringContainment,
    FixedGroupPDRParaphraseAccuracy,
    FixedGroupPDRParaphraseStringContainment,
    GroupMeanAccuracy,
    GroupMeanStringContainment,
    GroupMeanTokenOverlap,
    KendallTauMetric,
    RocAuc,
    Rouge,
    Squad,
    TokenOverlap,
)
from src.unitxt.test_utils.metrics import apply_metric
from tests.utils import UnitxtTestCase

logger = get_logger()

# values of inputs that are common to grouped_mean type InstanceMetric
GROUPED_INSTANCE_PREDICTIONS = [
    "A B",
    "BC D",
    "C",
    "123",
    "BCD",
    "10",
    "  BD",
    "AB",
    "I am a dog",
    "AB C",
    "AB 1",
    "GMA",
    "0.123",
    "BD",
    "abc",
]

GROUPED_INSTANCE_REFERENCES = [
    ["B", "AB", "A"],
    ["A", "BC D", "BC DF"],
    ["c", " C"],
    ["13", "23", "234"],
    ["  ", " BD", " BDA"],
    ["1", "10", "100"],
    ["A", "B", "BD"],
    ["ABC", "ab", "BC"],
    ["I am a person", "I AM A DOG", "ABC"],
    ["AB CD", "AB", "ab"],
    ["AB 1", "AB1"],
    [" GMA 123", "GMA"],
    ["123", "0.12"],
    ["BDE", "BCE", "bdefs"],
    [" abcdefg", "AB", "abcd"],
]

# task_data, consisting of a group_id (group instance scores by this, then apply aggregation function)
# and variant_type (for metrics that compare, say original vs paraphrase instance score)
# create 4 groups, of sizes 5,5,4,1
GROUPED_INSTANCE_ADDL_INPUTS = [
    {"group_id": "group1", "variant_type": "original"},
    {"group_id": "group1", "variant_type": "paraphrase"},
    {"group_id": "group1", "variant_type": "paraphrase"},
    {"group_id": "group1", "variant_type": "paraphrase"},
    {"group_id": "group1", "variant_type": "paraphrase"},
    {"group_id": "group2", "variant_type": "original"},
    {"group_id": "group2", "variant_type": "paraphrase"},
    {"group_id": "group2", "variant_type": "paraphrase"},
    {"group_id": "group2", "variant_type": "paraphrase"},
    {"group_id": "group2", "variant_type": "paraphrase"},
    {"group_id": "group3", "variant_type": "original"},
    {"group_id": "group3", "variant_type": "paraphrase"},
    {"group_id": "group3", "variant_type": "paraphrase"},
    {"group_id": "group3", "variant_type": "paraphrase"},
    {"group_id": "group4", "variant_type": "original"},
]


class TestMetrics(UnitxtTestCase):
    def test_accuracy(self):
        metric = Accuracy()

        predictions = ["A", "B", "C"]
        references = [["B", "C"], ["A"], ["B", "C"]]

        outputs = apply_metric(
            metric=metric, predictions=predictions, references=references
        )

        expected_global_result = {
            "accuracy": 1 / 3,
            "score": 1 / 3,
            "score_name": "accuracy",
        }

        global_result = outputs[0]["score"]["global"].copy()
        # Only check the keys that are expected, i.e. exist in expected_global_result
        global_result = {
            key: value
            for key, value in global_result.items()
            if key in expected_global_result
        }
        self.assertDictEqual(global_result, expected_global_result)

        instance_targets = [
            {"accuracy": 0.0, "score": 0.0, "score_name": "accuracy"},
            {"accuracy": 0.0, "score": 0.0, "score_name": "accuracy"},
            {"accuracy": 1.0, "score": 1.0, "score_name": "accuracy"},
        ]
        for output, target in zip(outputs, instance_targets):
            self.assertDictEqual(output["score"]["instance"], target)

    def test_squad(self):
        metric = Squad()
        predictions = ["1976", "Beyonce", "climate change"]
        references = [["1976"], ["Beyoncé and Bruno Mars"], ["climate change"]]
        instance_targets = [
            {"exact_match": 100.0, "f1": 100.0, "score": 100.0, "score_name": "f1"},
            {"exact_match": 0.0, "f1": 0.0, "score": 0.0, "score_name": "f1"},
            {"exact_match": 100.0, "f1": 100.0, "score": 100.0, "score_name": "f1"},
        ]
        global_target = 100 * 2 / 3
        outputs = apply_metric(
            metric=metric, predictions=predictions, references=references
        )

        self.assertAlmostEqual(global_target, outputs[0]["score"]["global"]["score"])
        for output, target in zip(outputs, instance_targets):
            self.assertEqual(output["score"]["instance"], target)

    def test_f1_micro(self):
        metric = F1Micro()
        references = [["cat"], ["dog"], ["dog"], ["dog"], ["cat"], ["cat"]]
        predictions = ["cat", "cat", "dog", "dog", "cat", "cat"]
        # F1 micro is equal to accuracy in multi class setting  (5/6)
        global_target = 0.8333333
        outputs = apply_metric(
            metric=metric, predictions=predictions, references=references
        )
        self.assertAlmostEqual(global_target, outputs[0]["score"]["global"]["score"])
        self.assertEqual("f1_micro", outputs[0]["score"]["global"]["score_name"])
        self.assertEqual("f1_micro", outputs[0]["score"]["instance"]["score_name"])

    def test_f1_macro(self):
        metric = F1Macro()
        references = [["cat"], ["dog"], ["dog"], ["dog"], ["cat"], ["cat"]]
        predictions = ["cat", "cat", "dog", "dog", "cat", "cat"]
        # recall class 'dog'  = 2/3  = 0.666        precision= 2/2 = 1    f1 = 0.8
        # recall class 'cat'  = 3/3  = 1            precision= 3/4 = 0.75 f1 = 0.857142857143
        # macro f1 = (0.8+0.847)/2
        global_target = 0.82857142
        global_target_dog = 0.8
        global_target_cat = 0.857142857143

        outputs = apply_metric(
            metric=metric, predictions=predictions, references=references
        )
        self.assertAlmostEqual(global_target, outputs[0]["score"]["global"]["score"])
        self.assertAlmostEqual(
            global_target_dog, outputs[0]["score"]["global"]["f1_dog"]
        )
        self.assertAlmostEqual(
            global_target_cat, outputs[0]["score"]["global"]["f1_cat"]
        )
        self.assertEqual("f1_macro", outputs[0]["score"]["global"]["score_name"])
        self.assertEqual("f1_macro", outputs[0]["score"]["instance"]["score_name"])

    def test_f1_weighted(self):
        metric = F1Weighted()
        references = [
            ["cat"],
            ["dog"],
            ["dog"],
            ["dog"],
            ["cat"],
            ["cat"],
            ["dog"],
            ["dog"],
        ]
        predictions = ["cat", "cat", "dog", "cat", "cat", "cat", "cat", "dog"]
        # recall class 'dog'  = 2/5  = 0.4          precision= 2/2 = 1    f1 = 0.66666666
        # recall class 'cat'  = 3/3  = 1            precision= 3/6 = 0.5  f1 = 0.57142857
        # weighted f1 = (0.375 * 0.66666666) + (0.625 * 0.57142857) = 0.60714285
        global_target = 0.60714285

        outputs = apply_metric(
            metric=metric, predictions=predictions, references=references
        )
        self.assertAlmostEqual(global_target, outputs[0]["score"]["global"]["score"])
        self.assertEqual("f1_weighted", outputs[0]["score"]["global"]["score_name"])
        self.assertEqual("f1_weighted", outputs[0]["score"]["instance"]["score_name"])

    def test_f1_macro_with_ood_predictions(self):
        metric = F1Macro()
        references = [["cat"], ["dog"], ["dog"], ["dog"], ["cat"], ["cat"]]
        predictions = ["cat", "2", "dog", "dog", "cat", "cat"]
        # recall class 'dog'  = 2/3  = 0.666        precision= 2/2 = 1    f1 = 0.8
        # recall class 'cat'  = 3/3  = 1            precision= 3/3 = 1    f1  =1
        # macro f1 = 0.9
        global_target = 0.9
        global_target_dog = 0.8
        global_target_cat = 1

        outputs = apply_metric(
            metric=metric, predictions=predictions, references=references
        )
        self.assertAlmostEqual(
            global_target_dog, outputs[0]["score"]["global"]["f1_dog"]
        )
        self.assertAlmostEqual(
            global_target_cat, outputs[0]["score"]["global"]["f1_cat"]
        )
        self.assertAlmostEqual(global_target, outputs[0]["score"]["global"]["score"])
        self.assertEqual("f1_macro", outputs[0]["score"]["global"]["score_name"])
        self.assertEqual("f1_macro", outputs[0]["score"]["instance"]["score_name"])

    def test_f1_macro_multilabel(self):
        metric = F1MacroMultiLabel()
        references = [
            [["cat", "dog"]],
            [["dog"]],
            [["dog"]],
            [["dog"]],
            [["cat"]],
            [["cat"]],
        ]
        predictions = [["cat"], ["2"], ["cat", "dog"], ["dog"], ["cat"], ["cat"]]
        # recall class 'dog'  = 2/4  = 0.5          precision= 2/2 = 1       f1 = 0.666666666667
        # recall class 'cat'  = 3/3  = 1            precision= 3/4 = 0.75    f1 = 0.857142857143
        # macro f1 = 0.9
        global_target = 0.76190476
        global_target_dog = 0.666666666667
        global_target_cat = 0.857142857143

        outputs = apply_metric(
            metric=metric, predictions=predictions, references=references
        )
        self.assertAlmostEqual(
            global_target_dog, outputs[0]["score"]["global"]["f1_dog"]
        )
        self.assertAlmostEqual(
            global_target_cat, outputs[0]["score"]["global"]["f1_cat"]
        )
        self.assertAlmostEqual(global_target, outputs[0]["score"]["global"]["score"])
        self.assertEqual("f1_macro", outputs[0]["score"]["global"]["score_name"])
        self.assertEqual("f1_macro", outputs[0]["score"]["instance"]["score_name"])

    def test_f1_micro_multilabel(self):
        metric = F1MicroMultiLabel()
        references = [
            [["cat", "dog"]],
            [["dog"]],
            [["dog"]],
            [["dog"]],
            [["cat"]],
            [["cat"]],
        ]
        predictions = [["cat"], ["2"], ["cat", "dog"], ["dog"], ["cat"], ["cat"]]
        # cat     TP=3  FP=1  FN=0  TN=2
        # dog     TP=2  FP=0  FN=2  TN=2
        # total   TP=5  FP=1  FN=2  TN=4
        # precision = TP / (FP + TP) = 5 / 6 = 0.8333333333
        # recall = TP /( FN + TP) =  5 / 7 = 0.7142857
        global_target = 0.769230760933

        outputs = apply_metric(
            metric=metric, predictions=predictions, references=references
        )
        self.assertAlmostEqual(global_target, outputs[0]["score"]["global"]["score"])

    def test_f1_micro_multilabel_error_format(self):
        metric = F1MicroMultiLabel()
        references = [["A B"], ["BC D"], ["C"], ["123"]]
        predictions = [
            ["B", "AB", "A"],
            ["A", "bC", "BC DF"],
            ["c", " C"],
            [13, 23, 234],
        ]
        with self.assertRaises(Exception) as cm:
            apply_metric(metric=metric, predictions=predictions, references=references)

        self.assertEqual(
            str(cm.exception),
            "Each reference is expected to be a list of strings in F1 multi label metric. Received reference: 'A B'",
        )

        references2 = [["A", "B"], ["BC", "D"], ["C"], ["123"]]

        with self.assertRaises(Exception) as cm:
            apply_metric(metric=metric, predictions=predictions, references=references2)

        self.assertEqual(
            str(cm.exception),
            "Only a single reference per prediction is allowed in F1 multi label metric. Received reference: ['A', 'B']",
        )

        references3 = [[["A"]], [["BC"]], [["C"]], [["123"]]]  # OK references

        with self.assertRaises(Exception) as cm:
            apply_metric(metric=metric, predictions=predictions, references=references3)

        self.assertEqual(
            str(cm.exception),
            "Each prediction is expected to be a list of strings in F1 multi label metric. Received prediction: '[13, 23, 234]'",
        )

    def test_f1_macro_multilabel_with_nones(self):
        metric = F1MacroMultiLabel()

        references = [[[]]]
        predictions = [[]]
        global_target = float("nan")
        outputs = apply_metric(
            metric=metric, predictions=predictions, references=references
        )
        self.assertTrue(isnan(outputs[0]["score"]["global"]["score"]))

        references = [[[]]]
        predictions = [["x", "y"]]
        outputs = apply_metric(
            metric=metric, predictions=predictions, references=references
        )
        self.assertTrue(isnan(outputs[0]["score"]["global"]["score"]))

        references = [[[]]]
        predictions = [[], "x", "y"]
        outputs = apply_metric(
            metric=metric, predictions=predictions, references=references
        )
        self.assertTrue(isnan(outputs[0]["score"]["global"]["score"]))

        references = [[["x"]], [["y"]]]
        predictions = [["x"], ["x"]]
        global_target = 0.33333333333
        # Recall(x) = 1.0 Precion(x) = 0.5   --> F1(x) = 0.66666
        # recall(y) = 0.0 Precision(x) = NAN --> F1(y) = 0
        outputs = apply_metric(
            metric=metric, predictions=predictions, references=references
        )
        self.assertAlmostEqual(global_target, outputs[0]["score"]["global"]["score"])

        references = [[[]], [["x"]], [["y"]], [[]], [[]]]
        predictions = [[], ["x"], ["x"], [], []]
        outputs = apply_metric(
            metric=metric, predictions=predictions, references=references
        )
        self.assertAlmostEqual(global_target, outputs[0]["score"]["global"]["score"])

    def test_f1_micro_multilabel_with_nones(self):
        metric = F1MicroMultiLabel()
        references = [[[]]]
        predictions = [["cat", "dog"]]

        outputs = apply_metric(
            metric=metric, predictions=predictions, references=references
        )
        self.assertTrue(isnan(outputs[0]["score"]["global"]["score"]))

        references = [[[]]]
        predictions = [[]]
        outputs = apply_metric(
            metric=metric, predictions=predictions, references=references
        )
        self.assertTrue(isnan(outputs[0]["score"]["global"]["score"]))

        references = [[["sad"]], [["sad"]]]
        predictions = [["dog", "fustrated"], ["sad"]]
        # TP = 1 FN = 1 FP=0 .. precision=100 recall=0.5
        # sad  TP=1  FP=1  FN=0  TN=1
        #
        # precision = TP / (FP + TP) = 1 / 2 = 0.5
        # recall = TP /( FN + TP) =  1 / 1 = 1

        global_target = 0.66666666
        outputs = apply_metric(
            metric=metric, predictions=predictions, references=references
        )
        self.assertAlmostEqual(global_target, outputs[0]["score"]["global"]["score"])

        references = [[[]], [["sad"]]]
        predictions = [["dog", "fustrated"], ["sad"]]
        # precision = TP / (FP + TP) = 1 / 1 = 1
        # recall = TP /( FN + TP) =  1 / 1 = 1

        global_target = 1
        outputs = apply_metric(
            metric=metric, predictions=predictions, references=references
        )
        self.assertAlmostEqual(global_target, outputs[0]["score"]["global"]["score"])

    def test_f1_multiple_use(self):
        metric = F1MacroMultiLabel()
        references = [[["cat", "dog"]]]
        predictions = [["cat"]]
        # recall class 'dog'  = 0/1 = 0             precision= 0/0 = 1       f1 = 0
        # recall class 'cat'  = 1/1 = 1             precision= 1/1 = 1       f1 = 1
        global_target = 0.5
        outputs = apply_metric(
            metric=metric, predictions=predictions, references=references
        )
        self.assertAlmostEqual(global_target, outputs[0]["score"]["global"]["score"])
        references = [[["horse"]]]
        predictions = [["horse"]]
        global_target = 1
        outputs = apply_metric(
            metric=metric, predictions=predictions, references=references
        )
        self.assertAlmostEqual(global_target, outputs[0]["score"]["global"]["score"])

    def test_rouge(self):
        metric = Rouge()
        references = [["hello", "there"], ["general kenobi", "general yoda"]]
        predictions = ["hello there", "general kenobi"]
        outputs = apply_metric(
            metric=metric, predictions=predictions, references=references
        )
        global_target = 5 / 6
        self.assertAlmostEqual(global_target, outputs[0]["score"]["global"]["score"])

    def test_rouge_l(self):
        metric = Rouge(
            n_resamples=None,  # disable confidence interval calculation which fails for this metric configuration
            use_aggregator=False,
            rouge_types=["rougeL"],
        )
        references = [["hello", "there"], ["general kenobi", "general yoda"]]
        predictions = ["hello there", "general kenobi"]
        outputs = apply_metric(
            metric=metric, predictions=predictions, references=references
        )
        global_target = [2 / 3, 1.0]
        self.assertListEqual(global_target, outputs[0]["score"]["global"]["score"])

    def test_token_overlap(self):
        metric = TokenOverlap()
        predictions = ["hello there general dude", "foo bar foobar"]
        references = [
            ["hello there general kenobi", "hello there!"],
            ["foo bar foobar", "foo bar"],
        ]
        outputs = apply_metric(
            metric=metric, predictions=predictions, references=references
        )
        global_targets = {"f1": 7 / 8, "precision": 7 / 8, "recall": 1}
        for target, value in global_targets.items():
            self.assertAlmostEqual(value, outputs[0]["score"]["global"][target])

    def test_roc_auc(self):
        metric = RocAuc()
        predictions = ["0.2", "0.8", "1.0"]
        references = [["1.0"], ["0.0"], ["1.0"]]
        outputs = apply_metric(
            metric=metric, predictions=predictions, references=references
        )
        global_target = 0.5
        self.assertAlmostEqual(global_target, outputs[0]["score"]["global"]["score"])

    def test_kendalltau(self):
        metric = KendallTauMetric()
        predictions = ["1.0", "2.0", "1.0"]
        references = [["-1.0"], ["1.0"], ["0.0"]]
        outputs = apply_metric(
            metric=metric, predictions=predictions, references=references
        )
        global_target = 0.81649658092772
        self.assertAlmostEqual(global_target, outputs[0]["score"]["global"]["score"])

    def test_grouped_instance_metrics(self):
        accuracy_metrics = [
            FixedGroupMeanAccuracy(),
            GroupMeanAccuracy(),
            FixedGroupMeanStringContainment(),
            GroupMeanStringContainment(),
            FixedGroupMeanBaselineAccuracy(),
            FixedGroupMeanParaphraseAccuracy(),
            FixedGroupMeanBaselineStringContainment(),
            FixedGroupMeanParaphraseStringContainment(),
            GroupMeanTokenOverlap(),
            FixedGroupNormCohensHParaphraseAccuracy(),
            FixedGroupNormCohensHParaphraseStringContainment(),
            FixedGroupPDRParaphraseAccuracy(),
            FixedGroupPDRParaphraseStringContainment(),
            FixedGroupNormHedgesGParaphraseAccuracy(),
            FixedGroupNormHedgesGParaphraseStringContainment(),
            FixedGroupAbsvalNormCohensHParaphraseAccuracy(),
            FixedGroupAbsvalNormCohensHParaphraseStringContainment(),
            FixedGroupAbsvalNormHedgesGParaphraseAccuracy(),
            FixedGroupAbsvalNormHedgesGParaphraseStringContainment(),
        ]
        global_targets = [
            0.225,
            0.225,
            0.4875,
            0.4875,
            0.5,
            0.19444444444444442,
            0.75,
            0.5555555555555555,
            0.5083333333333333,
            -0.4249467048786864,
            -0.4639421840102023,
            0.8333333333333334,
            0.4444444444444445,
            -0.34565986391520215,
            -0.08060156608173413,
            0.6471689271009087,
            0.4639421840102023,
            0.3832160660602437,
            0.08060156608173413,
        ]
        for metric, target in zip(accuracy_metrics, global_targets):
            outputs = apply_metric(
                metric=metric,
                predictions=GROUPED_INSTANCE_PREDICTIONS,
                references=GROUPED_INSTANCE_REFERENCES,
                task_data=GROUPED_INSTANCE_ADDL_INPUTS,
            )
            self.assertAlmostEqual(
                target,
                outputs[0]["score"]["global"]["score"],
                msg=f"metric {metric.__class__.__name__} output {outputs[0]['score']['global']['score_name']} does not equal the expected value {target}",
            )

    def test_grouped_instance_metric_errors(self):
        """Test certain value and assertion error raises for grouped instance metrics (with group_mean reduction)."""
        from dataclasses import field
        from statistics import mean
        from typing import List

        class NoAggFuncReduction(Accuracy):
            implemented_reductions: List[str] = field(
                default_factory=lambda: ["mean", "group_mean", "some_other_func"]
            )
            reduction_map = {"some_other_func": {"agg_func": ["mean", mean, False]}}

        with self.assertRaises(ValueError):
            # should raise error because no aggregation_function will be defined, since only mean and group_mean are implemented
            metric = NoAggFuncReduction()
            apply_metric(
                metric=metric,
                predictions=GROUPED_INSTANCE_PREDICTIONS,
                references=GROUPED_INSTANCE_REFERENCES,
                task_data=GROUPED_INSTANCE_ADDL_INPUTS,
            )

        class NoAggFunc(Accuracy):
            reduction_map = {"group_mean": {"func": ["mean", mean]}}

        with self.assertRaises(AssertionError):
            # should raise error because no "agg_func" field in group_mean
            metric = NoAggFunc()
            apply_metric(
                metric=metric,
                predictions=GROUPED_INSTANCE_PREDICTIONS,
                references=GROUPED_INSTANCE_REFERENCES,
                task_data=GROUPED_INSTANCE_ADDL_INPUTS,
            )

        class NoCallableAggFunc(Accuracy):
            reduction_map = {"group_mean": {"agg_func": ["mean", "some string", False]}}

        with self.assertRaises(AssertionError):
            # should raise error because second field of agg_func should be callable
            metric = NoCallableAggFunc()
            apply_metric(
                metric=metric,
                predictions=GROUPED_INSTANCE_PREDICTIONS,
                references=GROUPED_INSTANCE_REFERENCES,
                task_data=GROUPED_INSTANCE_ADDL_INPUTS,
            )

        class NoBooleanGrouping(Accuracy):
            reduction_map = {"group_mean": {"agg_func": ["mean", mean, 1]}}

        with self.assertRaises(AssertionError):
            # should raise error because third field in agg_func is not boolean
            metric = NoBooleanGrouping()
            apply_metric(
                metric=metric,
                predictions=GROUPED_INSTANCE_PREDICTIONS,
                references=GROUPED_INSTANCE_REFERENCES,
                task_data=GROUPED_INSTANCE_ADDL_INPUTS,
            )


class TestConfidenceIntervals(UnitxtTestCase):
    def test_confidence_interval_off(self):
        """Test that when metric.n_resamples is set to None, no confidence intervals are computed."""
        # Test one GlobalMetric and one InstanceMetric
        for metric in [Accuracy(), F1Macro()]:
            metric.disable_confidence_interval_calculation()
            outputs = apply_metric(metric=metric, predictions=["A"], references=[["A"]])

            global_result = outputs[0]["score"]["global"]
            # Check there are no confidence intervals in the result
            for key in global_result:
                self.assertTrue("ci_low" not in key)
                self.assertTrue("ci_high" not in key)

    def test_instance_metric_confidence_interval(self):
        """Test the calculation of confidence intervals for an instance metric (Accuracy is used as an instance of an InstanceMetric)."""
        self._test_confidence_interval(
            metric=Accuracy(),
            expected_ci_low=0.71,
            expected_ci_high=0.87,
        )

    def test_instance_metric_with_multiple_scores_confidence_interval(self):
        self._test_confidence_interval(
            metric=TokenOverlap(),
            expected_ci_low=0.71,
            expected_ci_high=0.87,
        )

    def test_global_metric_confidence_interval(self):
        """Test the calculation of confidence intervals for global metrics (F1Macro and F1Micro are used as instances of a GlobalMetric)."""
        f1_macro_low, f1_macro_high = 0.8809213119223925, 0.9439681645177271
        self._test_confidence_interval(
            metric=F1Macro(),
            expected_ci_low=f1_macro_low,
            expected_ci_high=f1_macro_high,
        )
        f1_micro_low, f1_micro_high = 0.8439306358381503, 0.9223675337263242
        self._test_confidence_interval(
            metric=F1Micro(),
            expected_ci_low=f1_micro_low,
            expected_ci_high=f1_micro_high,
        )

        # Now reverse the order and check things don't change
        self._test_confidence_interval(
            metric=F1Micro(),
            expected_ci_low=f1_micro_low,
            expected_ci_high=f1_micro_high,
        )
        self._test_confidence_interval(
            metric=F1Macro(),
            expected_ci_low=f1_macro_low,
            expected_ci_high=f1_macro_high,
        )

    def _test_confidence_interval(self, metric, expected_ci_low, expected_ci_high):
        """Test the calculation of confidence intervals for a given metric."""
        predictions = ["A", "B", "C", "D", "E"] * 20  # 100 predictions
        references = [["B"], ["B"], ["C"], ["D"], ["E"]] * 20  # 80% are correct (4/5)

        outputs = apply_metric(
            metric=metric, predictions=predictions, references=references
        )

        expected_global_result = {
            f"{metric.main_score}_ci_low": expected_ci_low,
            f"{metric.main_score}_ci_high": expected_ci_high,
            "score_ci_low": expected_ci_low,
            "score_ci_high": expected_ci_high,
        }

        global_result = outputs[0]["score"]["global"].copy()
        logger.info(global_result)
        for score_name, score_value in global_result.items():
            if score_name in expected_global_result:
                # Verify that the output value is as the expected value
                self.assertAlmostEqual(
                    score_value, expected_global_result[score_name], places=5
                )
            else:
                # An output score that is not expected
                # This is ok if the score_name is not related to confidence intervals
                # Otherwise, there was some confidence interval calculation that was not supposed to occur.
                self.assertTrue(
                    ("ci_low" not in score_name and "ci_high" not in score_name)
                    or score_name not in metric.ci_scores,
                    msg=f"Unexpected confidence interval score '{score_name}'.",
                )

    def test_grouped_instance_metric_confidence_interval(self):
        """Test the calculation of confidence intervals for grouped instance metrics (sub-types of InstanceMetric with group_mean reduction)."""
        self._test_grouped_instance_confidence_interval(
            metric=FixedGroupMeanAccuracy(),
            expected_ci_low=0.1,
            expected_ci_high=0.48178555627359004,
        )

        self._test_grouped_instance_confidence_interval(
            metric=GroupMeanAccuracy(),
            expected_ci_low=0.025,
            expected_ci_high=0.44105968464125495,
        )

        self._test_grouped_instance_confidence_interval(
            metric=FixedGroupMeanStringContainment(),
            expected_ci_low=0.0,
            expected_ci_high=0.675,
        )

        self._test_grouped_instance_confidence_interval(
            metric=GroupMeanStringContainment(),
            expected_ci_low=0.15556138609239942,
            expected_ci_high=0.707936507936508,
        )

        self._test_grouped_instance_confidence_interval(
            metric=FixedGroupMeanBaselineAccuracy(),
            expected_ci_low=0.0,
            expected_ci_high=1.0,
        )

        self._test_grouped_instance_confidence_interval(
            metric=FixedGroupMeanParaphraseAccuracy(),
            expected_ci_low=0.0,
            expected_ci_high=0.3333333333333333,
        )

        self._test_grouped_instance_confidence_interval(
            metric=FixedGroupMeanBaselineStringContainment(),
            expected_ci_low=0.25,
            expected_ci_high=1.0,
        )

        self._test_grouped_instance_confidence_interval(
            metric=FixedGroupMeanParaphraseStringContainment(),
            expected_ci_low=0.5,
            expected_ci_high=0.6666666666666666,
        )

        self._test_grouped_instance_confidence_interval(
            metric=FixedGroupNormCohensHParaphraseAccuracy(),
            expected_ci_low=-1.0,
            expected_ci_high=0.33333333333333337,
        )

        # note, this metric has an issue where the ci_high on PCs on Travis slightly diverges from the local results
        # hence this test may fail on a PC
        self._test_grouped_instance_confidence_interval(
            metric=FixedGroupNormCohensHParaphraseStringContainment(),
            expected_ci_low=-0.49999999999999994,
            expected_ci_high=-0.39182655203060723,
        )

        self._test_grouped_instance_confidence_interval(
            metric=FixedGroupPDRParaphraseAccuracy(),
            expected_ci_low=0.6666666666666666,
            expected_ci_high=1.0,
        )

        self._test_grouped_instance_confidence_interval(
            metric=FixedGroupPDRParaphraseStringContainment(),
            expected_ci_low=0.3333333333333333,
            expected_ci_high=0.5,
        )

        self._test_grouped_instance_confidence_interval(
            metric=FixedGroupNormHedgesGParaphraseAccuracy(),
            expected_ci_low=-1.0,
            expected_ci_high=0.01892225367237965,
        )

        self._test_grouped_instance_confidence_interval(
            metric=FixedGroupNormHedgesGParaphraseStringContainment(),
            expected_ci_low=-0.09757387538180902,
            expected_ci_high=-0.046656947481584346,
        )

        # absolute value of Hedges' g and Cohen's h
        self._test_grouped_instance_confidence_interval(
            metric=FixedGroupAbsvalNormCohensHParaphraseAccuracy(),
            expected_ci_low=0.33333333333333337,
            expected_ci_high=1.0,
        )

        self._test_grouped_instance_confidence_interval(
            metric=FixedGroupAbsvalNormCohensHParaphraseStringContainment(),
            expected_ci_low=0.39182655203060723,
            expected_ci_high=0.49999999999999994,
        )

        self._test_grouped_instance_confidence_interval(
            metric=FixedGroupAbsvalNormHedgesGParaphraseAccuracy(),
            expected_ci_low=0.05633430321756243,
            expected_ci_high=1.0,
        )

        self._test_grouped_instance_confidence_interval(
            metric=FixedGroupAbsvalNormHedgesGParaphraseStringContainment(),
            expected_ci_low=0.046656947481584346,
            expected_ci_high=0.09757387538180902,
        )

        # pass global dict because there are additional fields other than the main score
        self._test_grouped_instance_confidence_interval(
            metric=GroupMeanTokenOverlap(),
            expected_global_result={
                "group_mean_recall": 0.525,
                "group_mean_f1": 0.5083333333333333,
                "score": 0.5083333333333333,
                "score_name": "group_mean_f1",
                "group_mean_precision": 0.5,
                "group_mean_recall_ci_low": 0.25,
                "group_mean_recall_ci_high": 0.7083333333333334,
                "group_mean_f1_ci_low": 0.22302503471948287,
                "group_mean_f1_ci_high": 0.6805555555555555,
                "score_ci_low": 0.22302503471948287,
                "score_ci_high": 0.6805555555555555,
                "group_mean_precision_ci_low": 0.20949399775845196,
                "group_mean_precision_ci_high": 0.6666666666666666,
            },
        )

    def _test_grouped_instance_confidence_interval(
        self,
        metric,
        expected_ci_low=0.0,
        expected_ci_high=1.0,
        expected_global_result=None,
    ):
        """Test the calculation of confidence intervals for a given metric with group_mean reduction."""
        outputs = apply_metric(
            metric=metric,
            predictions=GROUPED_INSTANCE_PREDICTIONS,
            references=GROUPED_INSTANCE_REFERENCES,
            task_data=GROUPED_INSTANCE_ADDL_INPUTS,
        )
        # get first element of reduction_map values
        reduction_params = next(iter(metric.reduction_map.values()))
        prefix = "fixed_group" if reduction_params["agg_func"][2] else "group"
        group_score_name = "_".join(
            [
                prefix,
                metric.reduction_map["group_mean"]["agg_func"][0],
                metric.main_score,
            ]
        )

        if expected_global_result is None:
            expected_global_result = {
                f"{group_score_name}_ci_low": expected_ci_low,
                f"{group_score_name}_ci_high": expected_ci_high,
                "score_ci_low": expected_ci_low,
                "score_ci_high": expected_ci_high,
            }

        global_result = outputs[0]["score"]["global"].copy()
        logger.info(global_result)
        for score_name, score_value in global_result.items():
            if score_name in expected_global_result:
                self.assertAlmostEqual(
                    score_value,
                    expected_global_result[score_name],
                    places=5,
                    msg=f"{group_score_name} score mismatch for {metric.__class__.__name__}, got {expected_global_result[score_name]} but expected {score_value}",
                )
            else:
                # An output score that is not expected
                # This is ok if the score_name is not related to confidence intervals
                # Otherwise, there was some confidence interval calculation that was not supposed to occur.
                self.assertTrue(
                    "ci_low" not in score_name and "ci_high" not in score_name,
                    msg=f"Unexpected confidence interval score '{score_name}'.",
                )
