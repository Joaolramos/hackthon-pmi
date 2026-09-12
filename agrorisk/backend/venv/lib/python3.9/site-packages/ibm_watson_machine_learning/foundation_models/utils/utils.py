#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------
from string import Formatter
from typing import Any, Sequence, List, Dict
from dataclasses import dataclass, KW_ONLY, asdict
from json import loads as json_loads

from ibm_watson_machine_learning._wrappers import requests
from ibm_watson_machine_learning.helpers import DataConnection
from ibm_watson_machine_learning.messages.messages import Messages
from ibm_watson_machine_learning.wml_client_error import WMLClientError
from ibm_watson_machine_learning.utils.autoai.utils import load_file_from_file_system_nonautoai
from ibm_watson_machine_learning.utils.autoai.enums import DataConnectionTypes

@dataclass
class PromptTuningParams:
    base_model: dict
    _: KW_ONLY
    accumulate_steps: int = None
    batch_size: int = None
    init_method: str = None
    init_text: str = None
    learning_rate: float = None
    max_input_tokens: int = None
    max_output_tokens: int = None
    num_epochs: int = None
    task_id: str = None
    tuning_type: str = None
    verbalizer: str = None

    def to_dict(self):
        return {key: value for key, value in asdict(self).items() if value is not None}


def _get_foundation_models_spec(url, operation_name):
    response = requests.get(url,
                            params={"version": "2023-09-30"},
                            headers={'X-WML-User-Client': 'PythonClient'})
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        raise WMLClientError(Messages.get_message(message_id="fm_prompt_tuning_no_foundation_models"))
    else:
        msg = f"{operation_name} failed. Reason: {response.text}"
        raise WMLClientError(msg)


def get_model_specs(url):
    try:
        return _get_foundation_models_spec(f"{url}/ml/v1-beta/foundation_model_specs",
                                           "Get available foundation models")
    except WMLClientError as e:
        raise WMLClientError(Messages.get_message(url, message_id="fm_prompt_tuning_no_model_specs"), e)


def get_supported_tasks(url) -> dict:
    try:
        return _get_foundation_models_spec(f"{url}/ml/v1-beta/foundation_model_tasks",
                                           "Get tasks that are supported by the foundation models.")
    except WMLClientError as e:
        raise WMLClientError(Messages.get_message(url, message_id="fm_prompt_tuning_no_supported_tasks"), e)


def get_all_supported_tasks_dict() -> dict:
    tasks_dict = dict()
    for task_spec in get_supported_tasks("https://us-south.ml.cloud.ibm.com").get('resources', []):
        tasks_dict[task_spec['label'].replace("-", "_").replace(" ", "_").upper()] = task_spec['task_id']
    return tasks_dict


def load_request_json(run_id, wml_client, run_params = None) -> dict:
    if run_params is None:
        run_params = wml_client.training.get_details(run_id)

    model_request_path = run_params['entity'].get('results_reference', {}).get('location', {}).get('model_request_path')

    if model_request_path is None:
        raise WMLClientError("Missing model_request_path in run_params. Verify if the training run has been completed.")

    if wml_client.CLOUD_PLATFORM_SPACES:
        results_reference = DataConnection._from_dict(run_params['entity']['results_reference'])

        if run_params['entity']['results_reference']['type'] == DataConnectionTypes.CA:
            results_reference.location.file_name = model_request_path
        else:
            results_reference.location.path = model_request_path

        results_reference.set_client(wml_client)
        request_json_bytes = results_reference.read(raw=True, binary=True)

        # download from cos

    elif wml_client.CPD_version >= 4.8:
        asset_parts = model_request_path.split('/')
        model_request_asset_url = '/'.join(asset_parts[asset_parts.index('assets') + 1:])
        request_json_bytes = load_file_from_file_system_nonautoai(wml_client=wml_client,
                                                                  file_path=model_request_asset_url).read()
    else:
        raise WMLClientError("Unsupported environment for this action")

    return json_loads(request_json_bytes.decode())


def is_training_prompt_tuning(training_id, wml_client):
    """Returns True if training_id is connected to prompt tuning"""
    if training_id is None:
        return False
    run_params = wml_client.training.get_details(training_uid=training_id)
    return bool(run_params['entity'].get('prompt_tuning'))

class TemplateFormatter(Formatter):
    def check_unused_args(self, 
                          used_args: List[(int | str)], 
                          args: Sequence, 
                          kwargs: Dict[str, Any]) -> None:
        """Check for unused args."""
        extra_args = set(kwargs).difference(used_args)
        if extra_args:
            raise KeyError(extra_args)
