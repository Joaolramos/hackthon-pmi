#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2020- 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

from ibm_watson_machine_learning.experiment.autoai.optimizers.local_auto_pipelines import LocalAutoPipelines

from ibm_watsonx_ai.utils.change_methods_docstring import change_docstrings

__all__ = [
    "LocalAutoPipelines"
]
DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

@change_docstrings
class LocalAutoPipelines(LocalAutoPipelines):
    """LocalAutoPipelines class for pipeline operation automation.

    :param name: name for the AutoPipelines
    :type name: str

    :param prediction_type: type of the prediction
    :type prediction_type: PredictionType

    :param prediction_column: name of the target/label column
    :type prediction_column: str

    :param scoring: type of the metric to optimize with
    :type scoring: Metrics

    :param desc: description
    :type desc: str, optional

    :param holdout_size: percentage of the entire dataset to leave as a holdout
    :type holdout_size: float, optional

    :param max_num_daub_ensembles: maximum number (top-K ranked by DAUB model selection) of the selected algorithm,
        or estimator types, for example `LGBMClassifierEstimator`, `XGBoostClassifierEstimator`,
        or `LogisticRegressionEstimator` to use in pipeline composition, the default is None that means
        the true default value will be determined by the internal different algorithms,
        where only the highest ranked by model selection algorithm type is used
    :type max_num_daub_ensembles: int, optional

    :param train_sample_rows_test_size: training data sampling percentage
    :type train_sample_rows_test_size: float, optional

    :param include_only_estimators: list of estimators to include in computation process
    :type include_only_estimators: list[ClassificationAlgorithms or RegressionAlgorithms], optional

    :param cognito_transform_names: list of transformers to include in the feature enginnering computation process,
        see: AutoAI.Transformers
    :type cognito_transform_names: list[Transformers], optional

    :param _data_clients: internal argument to auto-gen notebooks
    :type _data_clients: list[client or resource], optional

    :param _result_client: internal argument to auto-gen notebooks
    :type _result_client: client or resource, optional

    :param _force_local_scenario: internal argument to force local scenario enablement
    :type _force_local_scenario: bool, optional
    """
    pass