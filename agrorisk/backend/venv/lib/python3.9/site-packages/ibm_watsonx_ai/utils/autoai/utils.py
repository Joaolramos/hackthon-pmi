#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------


__all__ = [
    'fetch_pipelines',
    'load_file_from_file_system',
    'load_file_from_file_system_nonautoai',
    'NextRunDetailsGenerator',
    'prepare_auto_ai_model_to_publish_normal_scenario',
    'prepare_auto_ai_model_to_publish_notebook_normal_scenario',
    'prepare_auto_ai_model_to_publish',
    'remove_file',
    'ProgressGenerator',
    'is_ipython',
    'try_import_lale',
    'try_load_dataset',
    'check_dependencies_versions',
    'try_import_autoai_libs',
    'try_import_autoai_ts_libs',
    'try_import_tqdm',
    'try_import_xlrd',
    'try_import_openpyxl',
    'try_import_graphviz',
    'prepare_cos_client',
    'create_model_download_link',
    'create_summary',
    'prepare_auto_ai_model_to_publish_notebook',
    'get_node_and_runtime_index',
    'download_experiment_details_from_file',
    'prepare_model_location_path',
    'download_wml_pipeline_details_from_file',
    'init_cos_client',
    'check_graphviz_binaries',
    'try_import_joblib',
    'get_sw_spec_and_type_based_on_sklearn',
    'validate_additional_params_for_optimizer',
    'is_list_composed_from_enum',
    'validate_optimizer_enum_values',
    'all_logging_disabled',
    'check_if_ts_pipeline_is_winner',
    'get_values_for_imputation_strategy',
    'translate_imputation_string_strategy_to_enum',
    'translate_estimator_string_to_enum',
    'translate_batched_estimator_string_to_enum',
    'convert_dataframe_to_fields_values_payload',
    'get_autoai_run_id_from_experiment_metadata'
]

from ibm_watson_machine_learning.utils.autoai import utils 
from inspect import getmembers, isfunction

from ibm_watsonx_ai.utils.change_methods_docstring import copy_func
import sys

for function in getmembers(utils, isfunction):
    if "ibm_watson_machine_learning" in function[1].__module__:
        sys.modules[__name__].__dict__[function[0]] = copy_func(function[1])
