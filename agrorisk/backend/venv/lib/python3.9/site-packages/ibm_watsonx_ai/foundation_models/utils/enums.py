#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes, DecodingMethods

from ibm_watsonx_ai.utils.change_methods_docstring import copy_enum

__all__ = [
    "ModelTypes",
    "DecodingMethods",
]

ModelTypes = copy_enum(ModelTypes)

DecodingMethods = copy_enum(DecodingMethods)
