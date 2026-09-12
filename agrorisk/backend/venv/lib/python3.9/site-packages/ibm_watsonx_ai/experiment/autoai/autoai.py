#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2020- 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

from ibm_watson_machine_learning.experiment.autoai.autoai import AutoAI

from ibm_watsonx_ai.utils.autoai.enums import (
    TShirtSize, ClassificationAlgorithms, RegressionAlgorithms, ForecastingAlgorithms, PredictionType, Metrics, \
    Transformers, DataConnectionTypes, PipelineTypes, SamplingTypes)

from ibm_watsonx_ai.utils.change_methods_docstring import change_docstrings

__all__ = [
    "AutoAI"
]

@change_docstrings
class AutoAI(AutoAI):
    """AutoAI class for pipeline models optimization automation.

    :param wml_credentials: credentials to watsonx.ai instance
    :type wml_credentials: dict

    :param project_id: ID of the watsonx.ai project
    :type project_id: str, optional

    :param space_id: ID of the watsonx.ai Space
    :type space_id: str, optional

    :param verify: user can pass as verify one of following:

        - the path to a CA_BUNDLE file
        - the path of directory with certificates of trusted CAs
        - `True` - default path to truststore will be taken
        - `False` - no verification will be made
    :type verify: bool or str, optional

    **Example**

    .. code-block:: python

        from ibm_watsonx_ai.experiment import AutoAI

        experiment = AutoAI(
            wml_credentials={
                "apikey": "...",
                "iam_apikey_description": "...",
                "iam_apikey_name": "...",
                "iam_role_crn": "...",
                "iam_serviceid_crn": "...",
                "instance_id": "...",
                "url": "https://us-south.ml.cloud.ibm.com"
            },
            project_id="...",
            space_id="...")
    """
    # note: initialization of AutoAI enums as class properties

    # note: Enums with estimators can be overwritten  in _init based on environment type (CPD or Cloud)
    ClassificationAlgorithms = ClassificationAlgorithms
    RegressionAlgorithms = RegressionAlgorithms
    ForecastingAlgorithms = ForecastingAlgorithms
    # end note
    TShirtSize = TShirtSize
    PredictionType = PredictionType
    Metrics = Metrics
    Transformers = Transformers
    DataConnectionTypes = DataConnectionTypes
    PipelineTypes = PipelineTypes
    SamplingTypes = SamplingTypes


