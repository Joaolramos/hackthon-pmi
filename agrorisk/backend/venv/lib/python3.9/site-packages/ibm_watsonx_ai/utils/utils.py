#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

from ibm_watson_machine_learning.utils.utils import *

from ibm_watsonx_ai.utils.change_methods_docstring import copy_func, change_docstrings



get_type_of_details = copy_func(get_type_of_details)
load_model_from_directory = copy_func(load_model_from_directory)
save_model_to_file = copy_func(save_model_to_file)
format_metrics = copy_func(format_metrics)
group_metrics = copy_func(group_metrics)
get_file_from_cos = copy_func(get_file_from_cos)
extract_model_from_repository = copy_func(extract_model_from_repository)
extract_mlmodel_from_archive = copy_func(extract_mlmodel_from_archive)
get_model_filename = copy_func(get_model_filename)
convert_metadata_to_parameters = copy_func(convert_metadata_to_parameters)
is_lib_installed = copy_func(is_lib_installed)
prepare_interaction_props_for_cos = copy_func(prepare_interaction_props_for_cos)
modify_details_for_script_and_shiny = copy_func(modify_details_for_script_and_shiny)


@change_docstrings
class NextResourceGenerator(NextResourceGenerator):
    """Generator class to produce next list of resources from REST API."""
    pass

@change_docstrings
class DisableWarningsLogger(DisableWarningsLogger):
    """Class which disables logging warnings (for example for silent handling WMLClientErrors in try except).

    **Example**

    .. code-block:: python

        try:
            with DisableWarningsLogger():
                throw_wml_error()
        except WMLClientError:
            success = False

    """
    pass

