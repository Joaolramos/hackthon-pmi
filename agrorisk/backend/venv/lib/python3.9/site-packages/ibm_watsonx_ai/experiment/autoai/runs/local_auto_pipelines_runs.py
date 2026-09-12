#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2020- 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

__all__ = [
    "LocalAutoPipelinesRuns"
]

from ibm_watson_machine_learning.experiment.autoai.runs.local_auto_pipelines_runs import LocalAutoPipelinesRuns

from ibm_watsonx_ai.utils.change_methods_docstring import change_docstrings

@change_docstrings
class LocalAutoPipelinesRuns(LocalAutoPipelinesRuns):
    """LocalAutoPipelinesRuns class is used to work with historical Optimizer runs (local optimizer and
    with with data from COS, without watsonx.ai API interaction).

    :param filter: filter, user can choose which runs to fetch specifying experiment name (option not yet available)
    :type filter: str, optional
    """

    pass