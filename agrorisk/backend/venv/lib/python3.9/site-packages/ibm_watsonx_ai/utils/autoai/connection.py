#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------



__all__ = [
    "validate_source_data_connections",
    "create_results_data_connection",
    "validate_results_data_connection",
    "create_deployment_output_data_connection",
    "validate_deployment_output_connection",
    "get_max_sample_size_limit"
]


from ibm_watson_machine_learning.utils.autoai import connection
from inspect import getmembers, isfunction

from ibm_watsonx_ai.utils.change_methods_docstring import copy_func
import sys

for function in getmembers(connection, isfunction):
    if "ibm_watson_machine_learning" in function[1].__module__:
        sys.modules[__name__].__dict__[function[0]] = copy_func(function[1])