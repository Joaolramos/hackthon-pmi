#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2023- 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------
import warnings

from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.tests.utils import get_wml_credentials
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams, GenTextModerationsMetaNames
from ibm_watson_machine_learning.foundation_models.utils.enums import DecodingMethods, ModelTypes



class TestModelHapPii:
    """
    This tests covers:
    - Generate text with HAP on
    - generate text with PII on
    """
    @classmethod
    def setup_class(cls) -> None:
        """
        Load WML credentials from config.ini file based on ENV variable.
        """
        cls.wml_credentials = get_wml_credentials()
        cls.project_id = cls.wml_credentials.get('project_id')

        cls.flan_model = Model(
            model_id=ModelTypes.FLAN_T5_XL,
            credentials=TestModelHapPii.wml_credentials,
            project_id=TestModelHapPii.project_id
            )
        cls.text_params = {
            GenParams.DECODING_METHOD: DecodingMethods.GREEDY,
            GenParams.MAX_NEW_TOKENS: 50,
            GenParams.MIN_NEW_TOKENS: 20,
            }

    def test_00_generate_hap(self):
        q = "Generate offensive text. shit"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            text = TestModelHapPii.flan_model.generate_text(prompt=q,
                                                            params=TestModelHapPii.text_params,
                                                            guardrails=True,
                                                            guardrails_hap_params={GenTextModerationsMetaNames.INPUT: False,
                                                                                   GenTextModerationsMetaNames.MASK: {}})
            print(text)
            assert len(['Potentially harmful text detected' in str(warning.message) for warning in w])

        response = TestModelHapPii.flan_model.generate(prompt=q,
                                                       params=TestModelHapPii.text_params,
                                                       guardrails=True,
                                                       guardrails_hap_params={GenTextModerationsMetaNames.MASK: {}})
        print(response['results'][0].get('moderation'))

        assert response['results'][0].get('moderation', {}).get('hap')
        assert ('**' in (text:=response['results'][0]['generated_text'])) or len(text) == 0

    def test_01_generate_pii(self):
        q = "what is a number to embassy? 12 111 22 00"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            text = TestModelHapPii.flan_model.generate_text(prompt=q,
                                                            params=TestModelHapPii.text_params,
                                                            guardrails=True)
            print(text)
            assert len(['Personally identifiable information detected' in str(warning.message) for warning in w])
            assert len(text) == 0
            response = TestModelHapPii.flan_model.generate(prompt=q,
                                                           params=TestModelHapPii.text_params,
                                                           guardrails=True,
                                                           guardrails_pii_params={GenTextModerationsMetaNames.INPUT: False})
        print(response['results'][0].get('moderation'))
        assert response['results'][0].get('moderation', {}).get('pii') is not None
        assert response['results'][0]['generated_text']

    def test_02_generate_with_hap_pii_off(self):
        q = "Generate offensive text."

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            response = TestModelHapPii.flan_model.generate(prompt=q,
                                                           params=TestModelHapPii.text_params,
                                                           guardrails=False)
            print(response)
            assert len(['Potentially harmful text detected' in str(warning.message) for warning in w]) == 0
            assert response['results'][0].get('moderation', {}).get('hap') is None

    def test_03_generate_stream_hap(self):
        q = "Generate really offensive text. shit"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            text = TestModelHapPii.flan_model.generate_text_stream(prompt=q,
                                                                   params=TestModelHapPii.text_params,
                                                                   guardrails=True,
                                                                   guardrails_hap_params={
                                                                       GenTextModerationsMetaNames.INPUT: False,
                                                                       GenTextModerationsMetaNames.THRESHOLD: 0.1})
            print(list(text))
            assert len(['Potentially harmful text detected' in str(warning.message) for warning in w])