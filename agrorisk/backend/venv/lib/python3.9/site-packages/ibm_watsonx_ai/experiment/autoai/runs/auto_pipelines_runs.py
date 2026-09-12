#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2020- 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

__all__ = [
    "AutoPipelinesRuns"
]

from ibm_watson_machine_learning.experiment.autoai.runs.auto_pipelines_runs import AutoPipelinesRuns

from ibm_watsonx_ai.utils.change_methods_docstring import change_docstrings

@change_docstrings
class AutoPipelinesRuns(AutoPipelinesRuns):
    """AutoPipelinesRuns class is used to work with historical Optimizer runs.

    :param engine: WMLEngine to handle WML operations
    :type engine: WMLEngine

    :param filter: filter, user can choose which runs to fetch specifying AutoPipelines name
    :type filter: str, optional
    """
    pass