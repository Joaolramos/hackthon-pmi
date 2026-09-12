#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------
from ibm_watson_machine_learning.foundation_models.extensions.langchain import WatsonxLLM

from ibm_watsonx_ai.utils.change_methods_docstring import change_docstrings

@change_docstrings
class WatsonxLLM(WatsonxLLM):
    """
    `LangChain CustomLLM <https://python.langchain.com/docs/modules/model_io/models/llms/custom_llm>`_ wrapper for watsonx foundation models.

    :param model: foundation model inference object instance
    :type model: Model

    **Supported chain types:**
        * `LLMChain`,
        * `TransformChain`,
        * `SequentialChain`,
        * `SimpleSequentialChain`
        * `ConversationChain` (including `ConversationBufferMemory`)
        * `LLMMathChain` (``bigscience/mt0-xxl``, ``eleutherai/gpt-neox-20b``, ``ibm/mpt-7b-instruct2``, ``bigcode/starcoder``, ``meta-llama/llama-2-70b-chat``, ``ibm/granite-13b-instruct-v1`` models only)

    **Instantiate the WatsonxLLM interface**

    .. code-block:: python

        from ibm_watsonx_ai.foundation_models import Model
        from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
        from ibm_watsonx_ai.foundation_models.extensions.langchain import WatsonxLLM

        generate_params = {
            GenParams.MAX_NEW_TOKENS: 25
        }

        model = Model(
            model_id="google/flan-ul2",
            credentials={
                "apikey": "***",
                "url": "https://us-south.ml.cloud.ibm.com"
            },
            params=generate_params,
            project_id="*****"
        )

        custom_llm = WatsonxLLM(model=model)

    """
    pass