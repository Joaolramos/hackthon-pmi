#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------


from ibm_watson_machine_learning.helpers import (get_credentials_from_config, 
                                                 pipeline_to_script,
                                                  get_wmls_configuration)

from ibm_watsonx_ai.utils.change_methods_docstring import copy_func


get_credentials_from_config  = copy_func(get_credentials_from_config)
pipeline_to_script = copy_func(pipeline_to_script)
get_wmls_configuration = copy_func(get_wmls_configuration)