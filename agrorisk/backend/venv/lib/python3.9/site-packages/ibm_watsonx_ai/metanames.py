#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

from ibm_watson_machine_learning.metanames import (MetaProp, MetaNamesBase,
                                                   TrainingConfigurationMetaNames, TrainingConfigurationMetaNamesCp4d30,
                                                   ExperimentMetaNames, PipelineMetanames,
                                                   LearningSystemMetaNames, MemberMetaNames,
                                                   ModelMetaNames, PayloadLoggingMetaNames,
                                                   FunctionMetaNames, FunctionNewMetaNames,
                                                   ScoringMetaNames, DecisionOptimizationMetaNames,
                                                   RuntimeMetaNames, LibraryMetaNames,
                                                   SpacesMetaNames, ExportMetaNames,
                                                   SpacesPlatformMetaNames, SpacesPlatformMemberMetaNames,
                                                   AssetsMetaNames, SwSpecMetaNames,
                                                   ScriptMetaNames, ShinyMetaNames,
                                                   PkgExtnMetaNames, HwSpecMetaNames,
                                                   ModelDefinitionMetaNames, ConnectionMetaNames,
                                                   DeploymentMetaNames, DeploymentNewMetaNames,
                                                   Migrationv4GACloudMetaNames, RemoteTrainingSystemMetaNames,
                                                   ExportMetaNames, VolumeMetaNames,
                                                   GenTextParamsMetaNames, GenTextReturnOptMetaNames,
                                                   FactsheetsMetaNames)

from ibm_watsonx_ai.utils.change_methods_docstring import change_docstrings

@change_docstrings
class MetaProp(MetaProp):
   __doc__ = MetaProp.__doc__
       
@change_docstrings
class MetaNamesBase(MetaNamesBase):
    __doc__ = MetaNamesBase.__doc__

class TrainingConfigurationMetaNames(TrainingConfigurationMetaNames):
    __doc__ = TrainingConfigurationMetaNames.__doc__

class TrainingConfigurationMetaNamesCp4d30(TrainingConfigurationMetaNamesCp4d30):
    __doc__ = TrainingConfigurationMetaNamesCp4d30.__doc__

class ExperimentMetaNames(ExperimentMetaNames):
    __doc__ = ExportMetaNames.__doc__

class PipelineMetanames(PipelineMetanames):
    __doc__ = PipelineMetanames.__doc__

class LearningSystemMetaNames(LearningSystemMetaNames):
    __doc__ = LearningSystemMetaNames.__doc__

class MemberMetaNames(MemberMetaNames):
    __doc__ = MemberMetaNames.__doc__

class ModelMetaNames(ModelMetaNames):
    __doc__ = ModelMetaNames.__doc__
    
class PayloadLoggingMetaNames(PayloadLoggingMetaNames):
    __doc__ = PayloadLoggingMetaNames.__doc__

class FunctionMetaNames(FunctionMetaNames):
    __doc__ = FunctionMetaNames.__doc__

class FunctionNewMetaNames(FunctionNewMetaNames):
    __doc__ = FunctionNewMetaNames.__doc__

class ScoringMetaNames(ScoringMetaNames):
    __doc__ = ScoringMetaNames.__doc__

class DecisionOptimizationMetaNames(DecisionOptimizationMetaNames):
    __doc__ = DecisionOptimizationMetaNames.__doc__

class RuntimeMetaNames(RuntimeMetaNames):
    __doc__ = RuntimeMetaNames.__doc__

class LibraryMetaNames(LibraryMetaNames):
    __doc__ = LibraryMetaNames.__doc__

class SpacesMetaNames(SpacesMetaNames):
    __doc__ = SpacesMetaNames.__doc__

class ExportMetaNames(ExportMetaNames):
    __doc__ = ExportMetaNames.__doc__

class SpacesPlatformMetaNames(SpacesPlatformMetaNames):
    __doc__ = SpacesPlatformMetaNames.__doc__

class SpacesPlatformMemberMetaNames(SpacesPlatformMemberMetaNames):
    __doc__ = SpacesPlatformMemberMetaNames.__doc__

class AssetsMetaNames(AssetsMetaNames):
   __doc__ = AssetsMetaNames.__doc__


## update this later #Todo
class SwSpecMetaNames(SwSpecMetaNames):
    __doc__ = SwSpecMetaNames.__doc__

class ScriptMetaNames(ScriptMetaNames):
    __doc__ = ScriptMetaNames.__doc__

class ShinyMetaNames(ShinyMetaNames):
    __doc__ = ShinyMetaNames.__doc__

class PkgExtnMetaNames(PkgExtnMetaNames):
    __doc__ = PkgExtnMetaNames.__doc__

## update this later #Todo
class HwSpecMetaNames(HwSpecMetaNames):
    __doc__ = HwSpecMetaNames.__doc__

class ModelDefinitionMetaNames(ModelDefinitionMetaNames):
    __doc__ = ModelDefinitionMetaNames.__doc__

class ConnectionMetaNames(ConnectionMetaNames):
    __doc__ = ConnectionMetaNames.__doc__

class DeploymentMetaNames(DeploymentMetaNames):
    __doc__ = DeploymentMetaNames.__doc__

class DeploymentNewMetaNames(DeploymentNewMetaNames):
    __doc__ = DeploymentNewMetaNames.__doc__

class Migrationv4GACloudMetaNames(Migrationv4GACloudMetaNames):
    __doc__ = Migrationv4GACloudMetaNames.__doc__

class RemoteTrainingSystemMetaNames(RemoteTrainingSystemMetaNames):
    __doc__ = RemoteTrainingSystemMetaNames.__doc__

class ExportMetaNames(ExportMetaNames):
    __doc__ = ExportMetaNames.__doc__

class VolumeMetaNames(VolumeMetaNames):
    __doc__ = VolumeMetaNames.__doc__

class FactsheetsMetaNames(FactsheetsMetaNames):
    __doc__ = FactsheetsMetaNames.__doc__

class GenTextParamsMetaNames(GenTextParamsMetaNames):
    __doc__ = GenTextParamsMetaNames.__doc__

class GenTextReturnOptMetaNames(GenTextReturnOptMetaNames):
    __doc__ = GenTextReturnOptMetaNames.__doc__
