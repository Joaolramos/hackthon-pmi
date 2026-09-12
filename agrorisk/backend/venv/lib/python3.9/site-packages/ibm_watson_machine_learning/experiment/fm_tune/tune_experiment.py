#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

from enum import Enum

from ibm_watson_machine_learning.foundation_models.prompt_tuner import PromptTuner
from ibm_watson_machine_learning.foundation_models.utils.enums import PromptTuningTypes, PromptTuningInitMethods, TuneExperimentTasks
from ibm_watson_machine_learning.experiment.base_experiment import BaseExperiment
from ibm_watson_machine_learning.wml_client_error import WMLClientError
from ibm_watson_machine_learning import APIClient

from .tune_runs import TuneRuns


class TuneExperiment(BaseExperiment):

    def __init__(self,
                 wml_credentials: dict,
                 project_id: str = None,
                 space_id: str = None,
                 verify=None) -> None:

        self.client = APIClient(wml_credentials, verify=verify)
        if not self.client.CLOUD_PLATFORM_SPACES and self.client.CPD_version < 4.8:
            raise WMLClientError(error_msg="Operation is unsupported for this release.")

        if project_id:
            self.client.set.default_project(project_id)
        else:
            self.client.set.default_space(space_id)

        self.PromptTuningTypes = PromptTuningTypes
        self.PromptTuningInitMethods = PromptTuningInitMethods

        # Note: Dynamically create enum with supported ENUM Tasks
        self.Tasks = TuneExperimentTasks
        # --- end note

        self.runs = TuneRuns(wml_client=self.client)

    def runs(self, *, filter: str) -> 'TuneRuns':
        """Get the historical tuning runs but with name filter."""
        return TuneRuns(client=self.client, filter=filter)

    def prompt_tuner(self,
                     name: str,  # Note: Rest API does not require name,
                     task_id: str,
                     description: str = None,
                     base_model: str = None,
                     accumulate_steps: int = None,
                     batch_size: int = None,
                     init_method: str = None,
                     init_text: str = None,
                     learning_rate: float = None,
                     max_input_tokens: int = None,
                     max_output_tokens: int = None,
                     num_epochs: int = None,
                     verbalizer: str = None,
                     tuning_type: str = None,
                     auto_update_model: bool = True,
                     group_by_name: bool = False) -> PromptTuner:

        if isinstance(task_id, TuneExperimentTasks):
            task_id = task_id.value

        if isinstance(base_model, Enum):
            base_model = base_model.value

        prompt_tuner = PromptTuner(name=name,
                                   task_id=task_id,
                                   description=description,
                                   base_model=base_model,
                                   accumulate_steps=accumulate_steps,
                                   batch_size=batch_size,
                                   init_method=init_method,
                                   init_text=init_text,
                                   learning_rate=learning_rate,
                                   max_input_tokens=max_input_tokens,
                                   max_output_tokens=max_output_tokens,
                                   num_epochs=num_epochs,
                                   tuning_type=tuning_type,
                                   verbalizer=verbalizer,
                                   auto_update_model=auto_update_model,
                                   group_by_name=group_by_name)

        prompt_tuner._client = self.client

        return prompt_tuner
