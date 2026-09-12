#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------


from ibm_watson_machine_learning.helpers.connections.flight_service import (FlightConnection, FakeCallback, DEFAULT_PARTITIONS_NUM,
                                                                            DEFAULT_BATCH_SIZE_FLIGHT_COMMAND,
                                                                            DEFAULT_BATCH_SIZE_FLIGHT_COMMAND_BINARY_READ)

                                                                            

from ibm_watsonx_ai.utils.change_methods_docstring import change_docstrings


class FakeCallback(FakeCallback):
    pass

@change_docstrings
class FlightConnection(FlightConnection):
    """FlightConnection object unify the work for data reading from different types of data sources,
    including databases. It uses a Flight Service and `pyarrow` library to connect and transfer the data.

    .. note::
        All available and supported connection types could be found on:
        https://connectivity-matrix.us-south.cf.test.appdomain.cloud

    :param headers: authorization headers to connect with Flight Service
    :type headers: dict

    :param project_id: ID of project
    :type project_id: str

    :param space_id: ID of space
    :type space_id: str

    :param label: Y column name, it is required for subsampling
    :type label: str

    :param sampling_type: a sampling strategy required of choice
    :type sampling_type: str

    :param learning_type: type of the dataset: 'classification', 'multiclass', 'regression', needed for resampling,
        if value is equal to None 'first_n_records' strategy will be used no mather what is specified in
        'sampling_type'
    :type learning_type: str

    :param data_location: data location information passed by user
    :type data_location: dict, optional

    :param enable_subsampling: tells to activate sampling mode for large data
    :type enable_subsampling: bool, optional

    :param callback: required for sending messages
    :type callback: StatusCallback, optional

    :param data_batch_size_limit: upper limit for data in one batch of data that should be downloaded in Bytes,
        default: 1GB
    :type data_batch_size_limit: int, optional

    :param logical_batch_size_limit: upper limit for logical batch when subsampling is turned on (in Bytes),
        default 2GB, the logical batch is the batch that is merged to the subsampled batch (eg. 2GB + 1GB) and then
        subsampling is performed on top of that 3GBs and 1GB batch (subsampled one) is rewritten again
    :type logical_batch_size_limit: int, optional

    :param flight_parameters: pure unchanged flight service parameters that need to be passed to the service
    :type flight_parameters: dict, optional

    :param fallback_to_one_connection: indicates if in case of failure we should switch to the one connection
        and try again, default `True`
    :type fallback_to_one_connection: bool, optional

    :param return_subsampling_stats: indicates whether return batch data stats: dataset size, no. of batches,
        applicable only if subsampling is enabled, default `False`
    :type return_subsampling_stats: bool, optional

    :param total_size_limit: upper limit for overall data that should be downloaded in Bytes, default: 1GB,
        if more than one of: `total_size_limit`, `total_nrows_limit`, `total_percentage_limit` are set,
        then data are limited to the lower threshold, if None, then all data are downloaded in batches
        in `iterable_read` method
    :type total_size_limit: int, optional

    :param total_nrows_limit: upper limit for overall data that should be downloaded in number of rows,
        if more than one of: `total_size_limit`, `total_nrows_limit`, `total_percentage_limit` are set,
        then data are limited to the lower threshold
    :type total_nrows_limit: int, optional

    :param total_percentage_limit: upper limit for overall data that should be downloaded in percent of all dataset,
        must be a float number between 0 and 1, if more than one of: `total_size_limit`, `total_nrows_limit`,
        `total_percentage_limit` are set, then data are limited to the lower threshold
    :type total_percentage_limit: float, optional
    """
    pass