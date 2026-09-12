#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2021- 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------
from enum import Enum


class SpecStates(Enum):
    SUPPORTED = 'supported'
    DEPRECATED = 'deprecated'
    CONSTRICTED = 'constricted'
    RETIRED = 'retired'

    UNSUPPORTED = 'unsupported'
    CREATE_UNSUPPORTED = 'create-unsupported'
