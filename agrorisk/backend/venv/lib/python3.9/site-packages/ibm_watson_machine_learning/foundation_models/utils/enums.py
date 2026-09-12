#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

from enum import Enum
from ibm_watson_machine_learning.foundation_models.utils.utils import get_all_supported_tasks_dict

__all__ = [
    "ModelTypes",
    "DecodingMethods",
    "PromptTuningTypes",
    "PromptTuningInitMethods",
    "TuneExperimentTasks"
    "PromptTemplateFormats"
]


class ModelTypes(Enum):
    """Supported foundation models."""
    FLAN_T5_XXL = "google/flan-t5-xxl"
    FLAN_UL2 = "google/flan-ul2"
    MT0_XXL = "bigscience/mt0-xxl"
    GPT_NEOX = 'eleutherai/gpt-neox-20b'
    MPT_7B_INSTRUCT2 = 'ibm/mpt-7b-instruct2'
    STARCODER = 'bigcode/starcoder'
    LLAMA_2_70B_CHAT = 'meta-llama/llama-2-70b-chat'
    LLAMA_2_13B_CHAT = 'meta-llama/llama-2-13b-chat'
    GRANITE_13B_INSTRUCT = 'ibm/granite-13b-instruct-v1'
    GRANITE_13B_CHAT = 'ibm/granite-13b-chat-v1'
    FLAN_T5_XL = 'google/flan-t5-xl'
    GRANITE_13B_CHAT_V2 = 'ibm/granite-13b-chat-v2'
    GRANITE_13B_INSTRUCT_V2 = 'ibm/granite-13b-instruct-v2'


class DecodingMethods(Enum):
    """Supported decoding methods for text generation."""
    SAMPLE = "sample"
    GREEDY = "greedy"


class PromptTuningTypes:
    PT = "prompt_tuning"


class PromptTuningInitMethods:
    """Supported methods for prompt initialization in prompt tuning."""
    RANDOM = "random"
    TEXT = "text"
    # PRESET ?


TuneExperimentTasks = Enum(value='TuneExperimentTasks',
                           names=get_all_supported_tasks_dict())
class PromptTemplateFormats(Enum):
    """Supported formats of loaded prompt template."""
    PROMPTTEMPLATE = "prompt"
    STRING = "string"
    LANGCHAIN = "langchain"
