#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

__all__ = ["ExperimentIterableDataset"]

from ibm_watson_machine_learning.data_loaders.datasets.experiment import (ExperimentIterableDataset, DEFAULT_SAMPLE_SIZE_LIMIT,
                                                                DEFAULT_REDUCED_SAMPLE_SIZE_LIMIT, DEFAULT_SAMPLING_TYPE)

from ibm_watsonx_ai.utils.change_methods_docstring import change_docstrings

DEFAULT_SAMPLE_SIZE_LIMIT = DEFAULT_SAMPLE_SIZE_LIMIT
DEFAULT_REDUCED_SAMPLE_SIZE_LIMIT = DEFAULT_REDUCED_SAMPLE_SIZE_LIMIT
DEFAULT_SAMPLING_TYPE = DEFAULT_SAMPLING_TYPE

@change_docstrings
class ExperimentIterableDataset(ExperimentIterableDataset):
    """
        This dataset is intended to be an Iterable stream from Flight Service.
        It should iterate over flight logical batches and manages by Connection class
        how batches are downloaded and created. It should take into consideration only 2 batches at a time.
        If we have 2 batches already downloaded, it should block further download
        and wait for first batch to be consumed.

        Example
        -------
        >>> experiment_metadata = {
        >>>     "prediction_column": 'species',
        >>>     "prediction_type": "classification",
        >>>     "project_id": os.environ.get('PROJECT_ID'),
        >>>     'wml_credentials': wml_credentials
        >>> }

        >>> connection = DataConnection(data_asset_id='5d99c11a-2060-4ef6-83d5-dc593c6455e2')


        >>># default sampling - read first 1GB of data
        >>> iterable_dataset = ExperimentIterableDataset(connection=connection,
        >>>                                              enable_sampling=True,
        >>>                                              sampling_type='first_n_records',
        >>>                                              sample_size_limit = 1GB,
        >>>                                              experiment_metadata=experiment_metadata)

        >>># read all data records in batches / no subsampling
        >>> iterable_dataset = ExperimentIterableDataset(connection=connection,
        >>>                                              enable_sampling=False,
        >>>                                               experiment_metadata=experiment_metadata)

        >>># stratified/random sampling
        >>> iterable_dataset = ExperimentIterableDataset(connection=connection,
        >>>                                              enable_sampling=True,
        >>>                                              sampling_type='stratified',
        >>>                                              sample_size_limit = 1GB,
        >>>                                              experiment_metadata=experiment_metadata)

    """
    pass