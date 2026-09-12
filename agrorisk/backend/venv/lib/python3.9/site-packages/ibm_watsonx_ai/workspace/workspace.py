#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

from ibm_watson_machine_learning.workspace import WorkSpace

from ibm_watsonx_ai.utils.change_methods_docstring import change_docstrings

@change_docstrings
class WorkSpace(WorkSpace):
    """WorkSpace class for watsonx.ai authentication and project/space manipulation."""
    pass