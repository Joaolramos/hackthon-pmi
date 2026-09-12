#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2020- 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

from ibm_watson_machine_learning.experiment.autoai.engines.wml_engine import WMLEngine

from ibm_watsonx_ai.utils.change_methods_docstring import change_docstrings

__all__ = [
    "WMLEngine"
]

@change_docstrings
class WMLEngine(WMLEngine):
    """WML Engine provides unified API to work with AutoAI Pipelines trainings on WML.

    :param workspace: WorkSpace object with wml client and all needed parameters
    :type workspace: WorkSpace
    """
    pass