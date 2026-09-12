#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2022- 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

import unittest

from ibm_watson_machine_learning.tests.utils import get_wml_credentials, is_cp4d
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes, DecodingMethods
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning.metanames import GenTextReturnOptMetaNames as ReturnOpts
from ibm_watson_machine_learning.wml_client_error import WMLClientError


class TestTextGeneration(unittest.TestCase):
    """
    This tests covers:
    - ...
    """
    wml_credentials = None
    project_id = None
    space_id = None

    @classmethod
    def setUpClass(cls) -> None:
        """
        Load WML credentials from config.ini file based on ENV variable.
        """
        cls.wml_credentials = get_wml_credentials()
        cls.project_id = cls.wml_credentials.get('project_id')

    def test_01_create_flan_ul2_model(self):
        ul2_params = {
            GenParams.DECODING_METHOD: DecodingMethods.GREEDY,
            GenParams.MAX_NEW_TOKENS: 50,
            GenParams.STOP_SEQUENCES: ['\n\n']
        }

        if is_cp4d():
            with self.assertRaises(WMLClientError):
                _ = Model(model_id=ModelTypes.FLAN_UL2, params=ul2_params,
                          credentials=self.wml_credentials, project_id=self.project_id)


        else:
            flan_ul2_model = Model(
                model_id=ModelTypes.FLAN_UL2,
                params=ul2_params,
                credentials=self.wml_credentials,
                project_id=self.project_id)

            q = "What is 1 + 1?"

            ul2_text = flan_ul2_model.generate_text(prompt=q)
            print(ul2_text)

            ul2_response = flan_ul2_model.generate(prompt=q)
            print(ul2_response['results'][0]['generated_text'])

            self.assertEqual(ul2_text, ul2_response['results'][0]['generated_text'])
            self.assertEqual(flan_ul2_model.get_details()['model_id'], ModelTypes.FLAN_UL2.value)

            sample_q = "What is 1 + {}?"
            prompts = [sample_q.format(i) for i in range(20)]
            ul2_texts = flan_ul2_model.generate_text(prompt=prompts, concurrency_limit=5)
            self.assertEqual(len(prompts), len(ul2_texts),
                             msg="Length of texts list is not equal length of prompts list")

            ul2_responses = flan_ul2_model.generate(prompt=prompts, concurrency_limit=6)
            self.assertEqual(len(prompts), len(ul2_responses),
                             msg="Length of responses is not equal length of prompts list")

            for text, response in zip(ul2_texts, ul2_responses):
                self.assertEqual(text, response['results'][0]['generated_text'],
                                 msg=f"Methods outputs are not equal generate_text: {text}, generate: {response}")

    def test_02_create_gpt_neox_model(self):
        if is_cp4d():
            with self.assertRaises(WMLClientError):
                _ = Model(model_id=ModelTypes.GPT_NEOX, credentials=self.wml_credentials, project_id=self.project_id)
        else:
            gpt_neox_model = Model(
                model_id=ModelTypes.GPT_NEOX,
                credentials=self.wml_credentials,
                project_id=self.project_id)

            q = "What is 1 + 1?"

            text_params = {
                GenParams.DECODING_METHOD: DecodingMethods.GREEDY,
                GenParams.MAX_NEW_TOKENS: 10,
                GenParams.STOP_SEQUENCES: ["\n"]
            }
            neox_text = gpt_neox_model.generate_text(prompt=q, params=text_params)
            print(neox_text)

            text_params_updated = {
                GenParams.DECODING_METHOD: DecodingMethods.SAMPLE,
                GenParams.MAX_NEW_TOKENS: 10,
                GenParams.STOP_SEQUENCES: ["\n"],
                GenParams.TEMPERATURE: 0

            }

            neox_response = gpt_neox_model.generate(prompt=q, params=text_params_updated)
            print(neox_response['results'][0]['generated_text'])

            self.assertEqual(neox_text, neox_response['results'][0]['generated_text'])
            self.assertEqual(gpt_neox_model.get_details()['model_id'], ModelTypes.GPT_NEOX.value)

    def test_03_create_mt0_model(self):
        if is_cp4d():
            with self.assertRaises(WMLClientError):
                _ = Model(model_id=ModelTypes.MT0_XXL, credentials=self.wml_credentials, project_id=self.project_id)
        else:
            mt0_model = Model(
                model_id=ModelTypes.MT0_XXL,
                credentials=self.wml_credentials,
                project_id=self.project_id)

            q = "What is 1 + 1?"

            text_params = {
                GenParams.DECODING_METHOD: DecodingMethods.GREEDY,
                GenParams.MAX_NEW_TOKENS: 10,
                GenParams.STOP_SEQUENCES: ["\n"],
                GenParams.RETURN_OPTIONS: {
                    ReturnOpts.INPUT_TEXT: True,
                    ReturnOpts.GENERATED_TOKENS: True,
                    ReturnOpts.TOP_N_TOKENS: 1
                }
            }
            text = mt0_model.generate_text(prompt=q, params=text_params)
            print(text)
            self.assertIn(q, text)

            response = mt0_model.generate(prompt=q)
            print(response['results'][0]['generated_text'])

            self.assertIn(response['results'][0]['generated_text'], text)
            self.assertEqual(mt0_model.get_details()['model_id'], ModelTypes.MT0_XXL.value)

    def test_04_create_mpt_7b_model(self):
        mpt_7b_params = {
            GenParams.DECODING_METHOD: 'greedy',
            GenParams.MAX_NEW_TOKENS: 1,
            GenParams.MIN_NEW_TOKENS: 0,
        }

        if is_cp4d():
            with self.assertRaises(WMLClientError):
                _ = Model(model_id='ibm/mpt-7b-instruct2', params=mpt_7b_params,
                          credentials=self.wml_credentials, project_id=self.project_id)
        else:
            mpt_7b_model = Model(
                model_id='ibm/mpt-7b-instruct2',
                params=mpt_7b_params,
                credentials=self.wml_credentials,
                project_id=self.project_id)

            q = "1 + 1?"

            ul2_text = mpt_7b_model.generate_text(prompt=q)
            print(ul2_text)

            ul2_response = mpt_7b_model.generate(prompt=q)
            print(ul2_response['results'][0]['generated_text'])

            self.assertEqual(ul2_text, ul2_response['results'][0]['generated_text'])
            self.assertEqual(mpt_7b_model.get_details()['model_id'], ModelTypes.MPT_7B_INSTRUCT2.value)

    def test_05_create_flan_t5_model(self):
        if is_cp4d():
            with self.assertRaises(WMLClientError):
                _ = Model(model_id="google/flan-t5-xxl", credentials=self.wml_credentials, project_id=self.project_id)
        else:
            flan_t5_model = Model(
                model_id="google/flan-t5-xxl",
                credentials=self.wml_credentials,
                project_id=self.project_id)

            q = "What is 1 * 1?"

            text_params = {
                GenParams.DECODING_METHOD: "greedy",
                GenParams.MAX_NEW_TOKENS: 20,
                GenParams.MIN_NEW_TOKENS: 0,
                GenParams.RANDOM_SEED: 99,
                GenParams.STOP_SEQUENCES: ["\n"],
                GenParams.TEMPERATURE: 0,
                GenParams.TIME_LIMIT: 100,
                GenParams.TOP_K: 99,
                GenParams.TOP_P: 0.99,
                GenParams.REPETITION_PENALTY: 1.5,
                GenParams.TRUNCATE_INPUT_TOKENS: 299,
                GenParams.RETURN_OPTIONS: {
                    "input_text": True,
                    "generated_tokens": True,
                    "top_n_tokens": 1
                }
            }
            text = flan_t5_model.generate_text(prompt=q, params=text_params)
            print(text)
            self.assertIn(q, text)

            response = flan_t5_model.generate(prompt=q)
            print(response['results'][0]['generated_text'])

            self.assertIn(response['results'][0]['generated_text'], text)
            self.assertEqual(flan_t5_model.get_details()['model_id'], ModelTypes.FLAN_T5_XXL.value)

    def test_06_create_starcoder_model(self):
        if is_cp4d():
            with self.assertRaises(WMLClientError):
                _ = Model(model_id=ModelTypes.STARCODER, credentials=self.wml_credentials, project_id=self.project_id)
        else:
            starcoder = Model(
                model_id=ModelTypes.STARCODER,
                credentials=self.wml_credentials,
                project_id=self.project_id)

            q = """
    Using the directions below, generate Python code for the given task.

    Input:
    # Write a Python function that prints 'Hello World!' string 'n' times.

    Output:
    def print_n_times(n):
        for i in range(n):
            print("Hello World!")

    <end of code>

    Input:
    # Write a Python function, which generates sequence of prime numbers.
    # The function 'primes' will take the argument 'n', an int. It will return a list which contains all primes less than 'n'.

    Output:
            """

            text_params = {
                GenParams.DECODING_METHOD: "greedy",
                GenParams.MAX_NEW_TOKENS: 1000,
                GenParams.MIN_NEW_TOKENS: 1,
                GenParams.STOP_SEQUENCES: ["<end of code>"],
                GenParams.REPETITION_PENALTY: 1,
                GenParams.RETURN_OPTIONS: {
                    "input_text": True,
                    "generated_tokens": True,
                    "top_n_tokens": 1
                }
            }
            text = starcoder.generate_text(prompt=q, params=text_params)
            print("*** GENERATE_TEXT ***")
            print(text)
            self.assertIn(q, text)

            updated_text_params = {
                GenParams.DECODING_METHOD: "greedy",
                GenParams.MAX_NEW_TOKENS: 500,
                GenParams.MIN_NEW_TOKENS: 20,
                GenParams.STOP_SEQUENCES: ["<end of code>"],
                GenParams.REPETITION_PENALTY: 1
            }

            response = starcoder.generate(prompt=q, params=updated_text_params)
            print("*** GENERATE ***")
            print(response['results'][0]['generated_text'])

            self.assertIn(response['results'][0]['generated_text'], text)
            self.assertEqual(starcoder.get_details()['model_id'], ModelTypes.STARCODER.value)

    def test_07_create_llama2_70B_chat_model(self):
        if is_cp4d():
            with self.assertRaises(WMLClientError):
                _ = Model(model_id=ModelTypes.LLAMA_2_70B_CHAT, credentials=self.wml_credentials,
                          project_id=self.project_id)
        else:
            llama2 = Model(
                model_id=ModelTypes.LLAMA_2_70B_CHAT,
                credentials=self.wml_credentials,
                project_id=self.project_id)

            q = "Answer the question. What is 1 * 1?"

            text_params = {
                GenParams.RETURN_OPTIONS: {
                    "input_text": True,
                    "generated_tokens": True,
                    "top_n_tokens": 1
                }
            }
            text = llama2.generate_text(prompt=q, params=text_params)
            print("TEXT", text)
            self.assertIn(q, text)

            response = llama2.generate(prompt=q)
            print("RESPONSE", response['results'][0]['generated_text'])

            self.assertIn(response['results'][0]['generated_text'], text)
            self.assertEqual(llama2.get_details()['model_id'], ModelTypes.LLAMA_2_70B_CHAT.value)

    def test_08_create_granite_13b_instruct_model(self):
        if is_cp4d():
            with self.assertRaises(WMLClientError):
                _ = Model(model_id=ModelTypes.GRANITE_13B_INSTRUCT, credentials=self.wml_credentials,
                          project_id=self.project_id)
        else:

            granite_instruct = Model(
                model_id=ModelTypes.GRANITE_13B_INSTRUCT,
                credentials=self.wml_credentials,
                project_id=self.project_id)

            q = "Answer the question. What is 1 * 1?"

            text_params = {
                GenParams.RETURN_OPTIONS: {
                    "input_text": True,
                    "generated_tokens": True,
                    "top_n_tokens": 1
                }
            }
            text = granite_instruct.generate_text(prompt=q, params=text_params)
            print("TEXT", text)
            self.assertIn(q, text)

            response = granite_instruct.generate(prompt=q)
            print("RESPONSE", response['results'][0]['generated_text'])

            self.assertIn(response['results'][0]['generated_text'], text)
            self.assertEqual(granite_instruct.get_details()['model_id'], ModelTypes.GRANITE_13B_INSTRUCT.value)

    def test_09_create_granite_13b_chat_model(self):
        granite_chat = Model(
            model_id=ModelTypes.GRANITE_13B_CHAT,
            credentials=self.wml_credentials,
            project_id=self.project_id)

        q = "Answer the question. What is 1 * 1?"

        text_params = {
            GenParams.RETURN_OPTIONS: {
                "input_text": True,
                "generated_tokens": True,
                "top_n_tokens": 1
            }
        }
        text = granite_chat.generate_text(prompt=q, params=text_params)
        print("TEXT", text)
        self.assertIn(q, text)

        response = granite_chat.generate(prompt=q)
        print("RESPONSE", response['results'][0]['generated_text'])

        self.assertIn(response['results'][0]['generated_text'], text)
        self.assertEqual(granite_chat.get_details()['model_id'], ModelTypes.GRANITE_13B_CHAT.value)

    def test_10_generate_text_with_raw_response(self):

        ul2_params = {
            GenParams.DECODING_METHOD: DecodingMethods.GREEDY,
            GenParams.MAX_NEW_TOKENS: 50,
            GenParams.STOP_SEQUENCES: ['\n\n']
        }

        flan_t5_model = Model(
            model_id=ModelTypes.FLAN_T5_XL,
            params=ul2_params,
            credentials=self.wml_credentials,
            project_id=self.project_id)

        q = "What is 1 + 1?"

        ul2_raw_response_generate_text = flan_t5_model.generate_text(prompt=q, raw_response=True)

        ul2_response_generate = flan_t5_model.generate(prompt=q)

        self.assertEqual(ul2_raw_response_generate_text['results'], ul2_response_generate['results'])

        sample_q = "What is 1 + {}?"
        prompts = [sample_q.format(i) for i in range(20)]

        ul2_raw_response_generate_text = flan_t5_model.generate_text(prompt=prompts, concurrency_limit=5,
                                                                      raw_response=True)
        self.assertEqual(len(prompts), len(ul2_raw_response_generate_text),
                         msg="Length of texts list is not equal length of prompts list")

        ul2_response_generate = flan_t5_model.generate(prompt=prompts, concurrency_limit=6)
        self.assertEqual(len(prompts), len(ul2_response_generate),
                         msg="Length of responses is not equal length of prompts list")

        for text, response in zip(ul2_raw_response_generate_text, ul2_response_generate):
            self.assertEqual(text['results'][0]['generated_text'], response['results'][0]['generated_text'],
                             msg=f"Methods outputs are not equal generate_text: {text}, generate: {response}")

    def test_11_generate_text_stream(self):
        text_params = {
            GenParams.DECODING_METHOD: DecodingMethods.GREEDY,
            GenParams.MIN_NEW_TOKENS: 0,
            GenParams.MAX_NEW_TOKENS: 20
        }
        model = Model(
            model_id=ModelTypes.LLAMA_2_13B_CHAT,
            params=text_params,
            credentials=self.wml_credentials,
            project_id=self.project_id)

        q = "Write an epigram about the sun"
        text = model.generate_text(prompt=q)
        text_stream = model.generate_text_stream(prompt=q)

        linked_text_stream = ''
        for chunk in text_stream:
            assert isinstance(chunk, str), f"chunk expect type '{str}', actual '{type(chunk)}'"
            linked_text_stream += chunk

        assert text == linked_text_stream

    def test_12_create_flan_t5_xl_model(self):
        flan_t5_xl = Model(
            model_id=ModelTypes.FLAN_T5_XL,
            credentials=self.wml_credentials,
            project_id=self.project_id)
        q = "Answer the question. What is 1 * 1?"
        text_params = {
            GenParams.RETURN_OPTIONS: {
                "input_text": True,
                "generated_tokens": True,
                "top_n_tokens": 1
            }
        }
        text = flan_t5_xl.generate_text(prompt=q, params=text_params)
        print("TEXT", text)
        self.assertIn(q, text)
        response = flan_t5_xl.generate(prompt=q)
        print("RESPONSE", response['results'][0]['generated_text'])
        self.assertIn(response['results'][0]['generated_text'], text)
        self.assertEqual(flan_t5_xl.get_details()['model_id'], ModelTypes.FLAN_T5_XL.value)

    def test_13_generate_text_stream_with_raw_response(self):
        raw_response = True
        text_params = {
            GenParams.DECODING_METHOD: DecodingMethods.GREEDY,
            GenParams.MIN_NEW_TOKENS: 0,
            GenParams.MAX_NEW_TOKENS: 20
        }
        model_id = ModelTypes.LLAMA_2_13B_CHAT
        model = Model(
            model_id=model_id,
            params=text_params,
            credentials=self.wml_credentials,
            project_id=self.project_id)

        q = "Write an epigram about the sun"
        text = model.generate_text(prompt=q)
        text_stream = model.generate_text_stream(prompt=q, raw_response=raw_response)

        linked_text_stream = ''
        for ind, chunk in enumerate(text_stream):
            if ind == 0:
                assert isinstance(chunk, dict), f"chunk expect type '{dict}', actual '{type(chunk)}'"
                assert isinstance(chunk["model_id"], str), (f"model_id expect type '{str}', "
                                                            f"actual '{type(chunk['model_id'])}'")
                assert isinstance(chunk["created_at"], str), (f"created_at expect type '{str}', "
                                                              f"actual '{type(chunk['created_at'])}'")
                assert isinstance(chunk["results"], list), (f"results expect type '{list}', "
                                                            f"actual '{type(chunk['results'])}'")

                assert chunk["model_id"] == model_id.value, (f"Wrong model naming, expected `{model_id.value}`, "
                                                             f"actual `{chunk['model_id']}`")

            linked_text_stream += chunk['results'][0]['generated_text']

        assert text == linked_text_stream

