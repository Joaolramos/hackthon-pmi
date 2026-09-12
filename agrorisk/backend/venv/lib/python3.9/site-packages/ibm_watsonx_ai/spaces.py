#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

from ibm_watson_machine_learning.spaces import Spaces
from ibm_watsonx_ai.metanames import SpacesMetaNames, MemberMetaNames, ExportMetaNames

from ibm_watsonx_ai.utils.change_methods_docstring import change_docstrings

@change_docstrings
class Spaces(Spaces):
    """Store and manage spaces. This is applicable only for IBM Cloud Pak® for Data."""

    ConfigurationMetaNames = SpacesMetaNames()
    """MetaNames for spaces creation."""
    MemberMetaNames = MemberMetaNames()
    """MetaNames for space members creation."""
    ExportMetaNames = ExportMetaNames()
    """MetaNames for spaces export."""
