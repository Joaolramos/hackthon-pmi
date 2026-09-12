#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

from abc import ABC, abstractmethod
from typing import Union, List, Optional
from ibm_watson_machine_learning.wml_resource import WMLResource

__all__ = [
    "FMModelInference"
]

from ibm_watson_machine_learning import APIClient
from ibm_watson_machine_learning.wml_client_error import WMLClientError, ParamOutOfRange, InvalidMultipleArguments
from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes, DecodingMethods
from ibm_watson_machine_learning.foundation_models.utils.utils import get_model_specs
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames
from ibm_watson_machine_learning.messages.messages import Messages
from .base_model_inference import BaseModelInference


class FMModelInference(BaseModelInference):
    """Base abstract class for the model interface."""

    def __init__(self,
                 *,
                 model_id: str = None,
                 params: dict = None,
                 api_client: APIClient = None) -> None:

        self.model_id = model_id
        if isinstance(self.model_id, ModelTypes):
            self.model_id = self.model_id.value

        self.params = params
        FMModelInference._validate_type(params, u'params', dict, False)

        self._client = api_client

        from ibm_watson_machine_learning.foundation_models import get_model_specs
        if self.model_id not in [model_spec['model_id'] for model_spec in get_model_specs(self._client.wml_credentials.get('url')).get('resources', [])]:
            raise WMLClientError(error_msg=f"Model '{self.model_id}' is not supported for this environment")

        if not self._client.CLOUD_PLATFORM_SPACES and self._client.CPD_version < 4.8:
            raise WMLClientError(error_msg="Operation is unsupported for this release.")

        BaseModelInference.__init__(self, __name__, self._client)

    def get_details(self):
        """Get model's details

        :return: details of model or deployment
        :rtype: dict
        """
        models = get_model_specs(self._client.wml_credentials['url']).get('resources', [])
        return next((item for item in models if item['model_id'] == self.model_id), None)

    def generate(self,
                 prompt,
                 params: dict = None,
                 guardrails: bool = False,
                 guardrails_hap_params: Optional[dict] = None,
                 guardrails_pii_params: Optional[dict] = None,
                 concurrency_limit: int = 10) -> Union[dict, List[dict]]:
        """
        Given a text prompt as input, and parameters the selected inference
        will generate a completion text as generated_text response.
        """
        self._validate_type(prompt, u'prompt', [str, list], True, raise_error_for_list=True)
        generate_text_url = self._client.service_instance._href_definitions.get_fm_generation_href('text')
        return self._generate_with_url(prompt=prompt,
                                       params=params,
                                       generate_url=generate_text_url,
                                       guardrails=guardrails,
                                       guardrails_hap_params=guardrails_hap_params,
                                       guardrails_pii_params=guardrails_pii_params,
                                       concurrency_limit=concurrency_limit)

    def generate_text_stream(self,
                             prompt,
                             params=None,
                             raw_response=False,
                             guardrails: bool = False,
                             guardrails_hap_params: Optional[dict] = None,
                             guardrails_pii_params: Optional[dict] = None):
        """
        Given a text prompt as input, and parameters the selected inference
        will generate a completion text as generator.
        """
        self._validate_type(prompt, u'prompt', str, True)
        generate_text_stream_url = self._client.service_instance._href_definitions.get_fm_generation_href(
            f'text_stream')

        return self._generate_stream_with_url(prompt=prompt,
                                              params=params,
                                              raw_response=raw_response,
                                              generate_stream_url=generate_text_stream_url,
                                              guardrails=guardrails,
                                              guardrails_hap_params=guardrails_hap_params,
                                              guardrails_pii_params=guardrails_pii_params)

    def get_identifying_params(self) -> dict:
        """Represent Model Inference's setup in dictionary"""
        return {
            "model_id": self.model_id,
            "params": self.params,
            "project_id": self._client.default_project_id,
            "space_id": self._client.default_space_id
        }

    def _prepare_inference_payload(self,
                                   prompt: str,
                                   params: dict = None,
                                   guardrails: bool = False,
                                   guardrails_hap_params: Optional[dict] = None,
                                   guardrails_pii_params: Optional[dict] = None) -> dict:
        payload = {
            "model_id": self.model_id,
            "input": prompt,
        }
        if guardrails:
            default_moderations_params = {
                'input': True,
                'output': True
                }
            payload.update({
                "moderations": {
                    "hap": (default_moderations_params | (guardrails_hap_params or {})),
                    "pii": (default_moderations_params | (guardrails_pii_params or {}))
                    }
                })

        if params:
            payload['parameters'] = params
        elif self.params:
            payload['parameters'] = self.params

        if 'parameters' in payload and GenTextParamsMetaNames.DECODING_METHOD in payload[
            'parameters']:
            if isinstance(payload['parameters'][GenTextParamsMetaNames.DECODING_METHOD], DecodingMethods):
                payload['parameters'][GenTextParamsMetaNames.DECODING_METHOD] = \
                    payload['parameters'][GenTextParamsMetaNames.DECODING_METHOD].value

        if self._client.default_project_id:
            payload['project_id'] = self._client.default_project_id
        elif self._client.default_space_id:
            payload['space_id'] = self._client.default_space_id

        if 'parameters' in payload and 'return_options' in payload['parameters']:
            if not (payload['parameters']['return_options'].get("input_text", False) or
                    payload['parameters']['return_options'].get("input_tokens", False)):
                raise WMLClientError(Messages.get_message(message_id="fm_required_parameters_not_provided"))

        return payload
