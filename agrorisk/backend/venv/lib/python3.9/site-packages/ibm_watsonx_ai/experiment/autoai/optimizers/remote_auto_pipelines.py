#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2020- 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------
from ibm_watson_machine_learning.experiment.autoai.optimizers.remote_auto_pipelines import RemoteAutoPipelines

from ibm_watsonx_ai.utils.change_methods_docstring import change_docstrings

__all__ = [
    "RemoteAutoPipelines"
]

@change_docstrings
class RemoteAutoPipelines(RemoteAutoPipelines):
    """RemoteAutoPipelines class for pipeline operation automation.

    :param name: name for the AutoPipelines
    :type name: str

    :param prediction_type: type of the prediction
    :type prediction_type: PredictionType

    :param prediction_column: name of the target/label column
    :type prediction_column: str

    :param scoring: type of the metric to optimize with
    :type scoring: Metrics

    :param engine: engine for remote work
    :type engine: WMLEngine

    :param desc: description
    :type desc: str, optional

    :param holdout_size: percentage of the entire dataset to leave as a holdout, default 0.1
    :type holdout_size: float, optional

    :param max_num_daub_ensembles: maximum number (top-K ranked by DAUB model selection) of the selected algorithm,
        or estimator types, for example `LGBMClassifierEstimator`, `XGBoostClassifierEstimator`, or
        `LogisticRegressionEstimator` to use in pipeline composition, the default is `None` that means
        the true default value will be determined by the internal different algorithms, where only
        the highest ranked by model selection algorithm type is used
    :type max_num_daub_ensembles: int, optional

    :param train_sample_rows_test_size: training data sampling percentage
    :type train_sample_rows_test_size: float, optional

    :param include_only_estimators: list of estimators to include in computation process
    :type include_only_estimators: list[ClassificationAlgorithms or RegressionAlgorithms], optional

    :param cognito_transform_names: list of transformers to include in the feature enginnering computation process,
        see: AutoAI.Transformers
    :type cognito_transform_names: list[Transformers], optional

    :param csv_separator: the separator, or list of separators to try for separating columns in a CSV file,
        not used if the file_name is not a CSV file, default is ','
    :type csv_separator: list[str] or str, optional

    :param excel_sheet: name of the excel sheet to use, only use when xlsx file is an input,
        support for number of the sheet is deprecated, by default first sheet is used
    :type excel_sheet: str, optional

    :param encoding: encoding type for CSV training file
    :type encoding: str, optional

    :param positive_label: the positive class to report when binary classification, when multiclass or regression,
        this will be ignored
    :type positive_label: str, optional

    :param t_shirt_size: the size of the remote AutoAI POD instance (computing resources),
        only applicable to a remote scenario
    :type t_shirt_size: TShirtSize, optional

    :param data_join_graph: a graph object with definition of join structure for multiple input data sources,
        data preprocess step for multiple files
    :type data_join_graph: DataJoinGraph, optional

    """
    pass