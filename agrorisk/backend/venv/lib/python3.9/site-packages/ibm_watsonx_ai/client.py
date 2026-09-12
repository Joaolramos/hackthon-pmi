#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

from ibm_watsonx_ai.repository import Repository
from ibm_watsonx_ai.model_definition import ModelDefinition
from ibm_watsonx_ai.deployments import Deployments
from ibm_watsonx_ai.factsheets import Factsheets
from ibm_watsonx_ai.training import Training
from ibm_watsonx_ai.platform_spaces import PlatformSpaces
from ibm_watsonx_ai.assets import Assets
from ibm_watsonx_ai.connections import Connections
from ibm_watsonx_ai.Set import Set
from ibm_watsonx_ai.sw_spec import SwSpec
from ibm_watsonx_ai.hw_spec import HwSpec
from ibm_watsonx_ai.pkg_extn import PkgExtn
from ibm_watsonx_ai.shiny import Shiny
from ibm_watsonx_ai.script import Script
from ibm_watsonx_ai.instance_new_plan import ServiceInstanceNewPlan

from ibm_watsonx_ai.export_assets import Export
from ibm_watsonx_ai.import_assets import Import



'''
.. module:: APIClient
   :platform: Unix, Windows
   :synopsis: watsonx.ai API Client.

.. moduleauthor:: IBM
'''

from ibm_watson_machine_learning.client import APIClient

from ibm_watsonx_ai.utils.change_methods_docstring import change_docstrings

@change_docstrings
class APIClient(APIClient):
   pass
        