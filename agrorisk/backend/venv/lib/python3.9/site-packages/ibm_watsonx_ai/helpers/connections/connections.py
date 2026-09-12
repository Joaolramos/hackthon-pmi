__all__ = [
    "DataConnection",
    "S3Connection",
    "ConnectionAsset",
    "S3Location",
    "FSLocation",
    "AssetLocation",
    "CP4DAssetLocation",
    "WMLSAssetLocation",
    "CloudAssetLocation",
    "DeploymentOutputAssetLocation",
    "NFSConnection",
    "NFSLocation",
    'ConnectionAssetLocation',
    "DatabaseLocation",
    "ContainerLocation"
]

#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2023.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

from ibm_watson_machine_learning.helpers.connections import (DataConnection, S3Connection,
                                                             ConnectionAsset, S3Location,
                                                             FSLocation, AssetLocation,
                                                             CP4DAssetLocation, WMLSAssetLocation,
                                                             CloudAssetLocation, DeploymentOutputAssetLocation,
                                                             NFSConnection, NFSLocation, ConnectionAssetLocation,
                                                             DatabaseLocation, ContainerLocation)

from ibm_watsonx_ai.utils.change_methods_docstring import change_docstrings


@change_docstrings
class DataConnection(DataConnection):
    """Data Storage Connection class needed for WML training metadata (input data).

    :param connection: connection parameters of specific type
    :type connection: NFSConnection or ConnectionAsset, optional

    :param location: required location parameters of specific type
    :type location: Union[S3Location, FSLocation, AssetLocation]

    :param data_join_node_name: name(s) for node(s):

        - `None` - data file name will be used as node name
        - str - it will became node name
        - list[str] - multiple names passed, several nodes will have the same data connection
          (used for excel files with multiple sheets)
    :type data_join_node_name:  None or str or list[str], optional

    :param data_asset_id: data asset ID if DataConnection should be pointing out to data asset
    :type data_asset_id: str, optional
    """
    pass

# TODO: Remove S3 Implementation for connection
@change_docstrings
class S3Connection(S3Connection):
    """Connection class to COS data storage in S3 format.

    :param endpoint_url: S3 data storage url (COS)
    :type endpoint_url: str

    :param access_key_id: access_key_id of the S3 connection (COS)
    :type access_key_id: str, optional

    :param secret_access_key: secret_access_key of the S3 connection (COS)
    :type secret_access_key: str, optional

    :param api_key: API key of the S3 connection (COS)
    :type api_key: str, optional

    :param service_name: service name of the S3 connection (COS)
    :type service_name: str, optional

    :param auth_endpoint: authentication endpoint url of the S3 connection (COS)
    :type auth_endpoint: str, optional
    """
    pass

@change_docstrings
class S3Location(S3Location):
    """Connection class to COS data storage in S3 format.

    :param bucket: COS bucket name
    :type bucket: str

    :param path: COS data path in the bucket
    :type path: str

    :param excel_sheet: name of excel sheet if pointed dataset is excel file used for Batched Deployment scoring
    :type excel_sheet: str, optional

    :param model_location: path to the pipeline model in the COS
    :type model_location: str, optional

    :param training_status: path to the training status json in COS
    :type training_status: str, optional
    """
    pass

@change_docstrings
class ContainerLocation(ContainerLocation):
    """Connection class to default COS in user Project/Space."""
    pass

@change_docstrings
class FSLocation(FSLocation):
    """Connection class to File Storage in CP4D."""
    pass

@change_docstrings
class AssetLocation(AssetLocation):
    pass

@change_docstrings
class ConnectionAssetLocation(ConnectionAssetLocation):
    """Connection class to COS data storage.

    :param bucket: COS bucket name
    :type bucket: str

    :param file_name: COS data path in the bucket
    :type file_name: str

    :param model_location: path to the pipeline model in the COS
    :type model_location: str, optional

    :param training_status: path to the training status json in COS
    :type training_status: str, optional
    """
    pass

@change_docstrings
class ConnectionAsset(ConnectionAsset):
    """Connection class for Connection Asset.

    :param connection_id: connection asset ID
    :type connection_id: str
    """

    pass

@change_docstrings
class NFSConnection(NFSConnection):
    """Connection class to file storage in CP4D of NFS format.

    :param asset_id: asset ID from the project on CP4D
    :type asset_id: str
    """

    pass

@change_docstrings
class NFSLocation(NFSLocation):
    """Location class to file storage in CP4D of NFS format.

    :param path: data path form the project on CP4D
    :type path: str
    """

    pass

@change_docstrings
class CP4DAssetLocation(CP4DAssetLocation):
    """Connection class to data assets in CP4D.

    :param asset_id: asset ID from the project on CP4D
    :type asset_id: str
    """

    pass

@change_docstrings
class WMLSAssetLocation(AssetLocation):
    """Connection class to data assets in WML Server.

    :param asset_id: asset ID of the file loaded on space in WML Server
    :type asset_id: str
    """

    pass

@change_docstrings
class CloudAssetLocation(CloudAssetLocation):
    """Connection class to data assets as input data references to batch deployment job on Cloud.

    :param asset_id: asset ID of the file loaded on space on Cloud
    :type asset_id: str
    """

    pass

@change_docstrings
class DeploymentOutputAssetLocation(DeploymentOutputAssetLocation):
    """Connection class to data assets where output of batch deployment will be stored.

    :param name: name of .csv file which will be saved as data asset
    :type name: str
    :param description: description of the data asset
    :type description: str, optional
    """

    pass


@change_docstrings
class DatabaseLocation(DatabaseLocation):
    """Location class to Database.

    :param schema_name: database schema name
    :type schema_name: str
    :param table_name: database table name
    :type table_name: str
    """
    pass
