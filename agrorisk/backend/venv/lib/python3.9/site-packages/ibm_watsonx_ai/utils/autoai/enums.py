#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

from ibm_watson_machine_learning.utils.autoai.enums import *
from ibm_watson_machine_learning.utils.autoai.enums import (BatchedClassificationAlgorithms,
                                                            BatchedRegressionAlgorithms)

from ibm_watsonx_ai.utils.change_methods_docstring import copy_enum

__all__ = [
    "ClassificationAlgorithms",
    "ClassificationAlgorithmsCP4D",
    "RegressionAlgorithms",
    "RegressionAlgorithmsCP4D",
    "ForecastingAlgorithms",
    "ForecastingAlgorithmsCP4D",
    "PredictionType",
    "Metrics",
    "Transformers",
    "DataConnectionTypes",
    "RunStateTypes",
    "PipelineTypes",
    "Directions",
    "TShirtSize",
    "MetricsToDirections",
    'PositiveLabelClass',
    'VisualizationTypes',
    'SamplingTypes',
    'ImputationStrategy',
    'ForecastingPipelineTypes',
    'TimeseriesAnomalyPredictionPipelineTypes',
    'TimeseriesAnomalyPredictionAlgorithms'
    
]

from ibm_watsonx_ai.utils.change_methods_docstring import copy_enum
import sys

for enum_name in __all__:
     enum = sys.modules[__name__].__dict__[enum_name]
     sys.modules[__name__].__dict__[enum_name] = copy_enum(enum)

sys.modules[__name__].__dict__['BatchedClassificationAlgorithms'] = copy_enum(BatchedClassificationAlgorithms)
sys.modules[__name__].__dict__['BatchedRegressionAlgorithms'] = copy_enum(BatchedRegressionAlgorithms)