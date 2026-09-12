#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

__all__ = ["ExperimentDataLoader"]

from ibm_watson_machine_learning.data_loaders.experiment import ExperimentDataLoader, custom_collate

from ibm_watsonx_ai.utils.change_methods_docstring import change_docstrings, copy_func

@change_docstrings
class ExperimentDataLoader(ExperimentDataLoader):
    """Experiment Data Loader based on torch DataLoader.
    It interacts with the Flight Service to provide data batch stream

    **Example**

    .. code-block:: python

        experiment_metadata = {
            "prediction_column": 'species',
            "prediction_type": "classification",
            "project_id": os.environ.get('PROJECT_ID'),
            'wml_credentials': wml_credentials
        }

        connection = DataConnection(data_asset_id='5d99c11a-2060-4ef6-83d5-dc593c6455e2')


        iterable_dataset = ExperimentIterableDataset(connection=connection,
                                                     enable_sampling=False,
                                                     experiment_metadata=experiment_metadata)

        data_loader = ExperimentDataLoader(dataset=iterable_dataset)

        for data in data_loader:
            print(data)
    """
    pass

custom_collate = copy_func(custom_collate)
