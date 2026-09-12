#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2020- 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

__all__ = [
    "WebService"
]
from ibm_watson_machine_learning.deployment import WebService
from ibm_watsonx_ai.utils.change_methods_docstring import change_docstrings

@change_docstrings
class WebService(WebService):
    """An Online Deployment class aka. WebService.
    With this class object you can manage any online (WebService) deployment.

    :param source_wml_credentials: credentials to watsonx.ai instance where training was performed
    :type source_wml_credentials: dict

    :param source_project_id: ID of the watsonx.ai project where training was performed
    :type source_project_id: str, optional

    :param source_space_id: ID of the watsonx.ai Space where training was performed
    :type source_space_id: str, optional

    :param target_wml_credentials: credentials to watsonx.ai instance where you want to deploy
    :type target_wml_credentials: dict

    :param target_project_id: ID of the watsonx.ai project where you want to deploy
    :type target_project_id: str, optional

    :param target_space_id: ID of the watsonx.ai Space where you want to deploy
    :type target_space_id: str, optional
    """
    pass