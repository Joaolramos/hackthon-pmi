#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2020- 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

from ibm_watson_machine_learning.deployment.base_deployment import BaseDeployment

from ibm_watsonx_ai.utils.change_methods_docstring import change_docstrings

__all__ = [
    "BaseDeployment"
]

@change_docstrings
class BaseDeployment(BaseDeployment):
    """Base abstract class for Deployment."""
    pass