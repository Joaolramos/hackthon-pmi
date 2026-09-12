#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

from __future__ import print_function

from ibm_watson_machine_learning.foundation_models import Model
from ibm_watsonx_ai.utils.change_methods_docstring import change_docstrings

@change_docstrings
class Model(Model):
    """Instantiate the model interface.

    .. hint::
        To use the Model class with LangChain, use the :func:`to_langchain() <ibm_watsonx_ai.foundation_models.Model.to_langchain>` function.

    :param model_id: the type of model to use
    :type model_id: str

    :param credentials: credentials to watsonx.ai instance
    :type credentials: dict

    :param params: parameters to use during generate requests
    :type params: dict, optional

    :param project_id: ID of the watsonx.ai project
    :type project_id: str, optional

    :param space_id: ID of the watsonx.ai space
    :type space_id: str, optional

    :param verify: user can pass as verify one of following:

        - the path to a CA_BUNDLE file
        - the path of directory with certificates of trusted CAs
        - `True` - default path to truststore will be taken
        - `False` - no verification will be made
    :type verify: bool or str, optional

    .. note::
        One of these parameters is required: ['project_id ', 'space_id']

    .. hint::
        You can copy the project_id from Project's Manage tab (Project -> Manage -> General -> Details).

    **Example**

    .. code-block:: python

        from ibm_watsonx_ai.foundation_models import Model
        from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
        from ibm_watsonx_ai.foundation_models.utils.enums import ModelTypes, DecodingMethods

        # To display example params enter
        GenParams().get_example_values()

        generate_params = {
            GenParams.MAX_NEW_TOKENS: 25
        }

        model = Model(
            model_id=ModelTypes.FLAN_UL2,
            params=generate_params,
            credentials={
                "apikey": "***",
                "url": "https://us-south.ml.cloud.ibm.com"
            },
            project_id="*****"
            )
    """
    pass