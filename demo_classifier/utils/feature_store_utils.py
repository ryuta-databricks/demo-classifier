from typing import Union, List

import pyspark

import databricks
from databricks.feature_store import FeatureStoreClient
from demo_classifier.utils.get_spark import spark


def create_and_write_feature_table(df: pyspark.sql.DataFrame,
                                   feature_table_name: str,
                                   database_name: str,
                                   primary_keys: Union[str, List[str]],
                                   description: str) -> databricks.feature_store.entities.feature_table.FeatureTable:
    """
    Create and return a feature table with the given name and primary keys, writing the provided Spark DataFrame to the
    feature table

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Data to create this feature table
    feature_table_name : str
        A feature table name of the form <table_name>, for example user_features.
    database_name : str
        A database name of the form <database_name>, for example dev.
    primary_keys : Union[str, List[str]]
        The feature table’s primary keys. If multiple columns are required, specify a list of column names, for example
        ['customer_id', 'region'].
    description : str
        Description of the feature table.
    Returns
    -------
    databricks.feature_store.entities.feature_table.FeatureTable
    """
    fs = FeatureStoreClient()
    full_feature_table_name = f'{database_name}.{feature_table_name}'
    if not spark.catalog.tableExists(feature_table_name, database_name):
        feature_table = fs.create_table(
            name=full_feature_table_name,
            primary_keys=primary_keys,
            schema=df.schema,
            description=description
        )

    fs.write_table(df=df, name=full_feature_table_name, mode='overwrite')

    return full_feature_table_name
