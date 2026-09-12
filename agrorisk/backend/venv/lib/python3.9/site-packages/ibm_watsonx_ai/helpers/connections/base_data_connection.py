__all__ = [
    "BaseDataConnection"
]

#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2020- 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

from ibm_watson_machine_learning.helpers.connections.base_data_connection import BaseDataConnection

from ibm_watsonx_ai.utils.change_methods_docstring import change_docstrings

@change_docstrings
class BaseDataConnection(BaseDataConnection):
    """Base class for DataConnection."""
    pass