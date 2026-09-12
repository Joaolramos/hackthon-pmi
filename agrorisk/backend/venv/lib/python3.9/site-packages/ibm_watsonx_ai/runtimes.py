#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------


from ibm_watson_machine_learning.runtimes import Runtimes

from ibm_watsonx_ai.utils.change_methods_docstring import change_docstrings

@change_docstrings
class Runtimes(Runtimes):
    """Create Runtime Specs and associated Custom Libraries.

    .. note::
        There are a list of pre-defined runtimes available. To see the list of pre-defined runtimes, use:

        .. code-block:: python

            client.runtimes.list(pre_defined=True)
    """
    pass