#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

__all__ = [
    'get_project',
    'get_wmls_credentials_and_space_ids'
]


from ibm_watson_machine_learning.utils.autoai.watson_studio import get_project, get_wmls_credentials_and_space_ids

from ibm_watsonx_ai.utils.change_methods_docstring import copy_func

get_project = copy_func(get_project)
get_wmls_credentials_and_space_ids = copy_func(get_wmls_credentials_and_space_ids)