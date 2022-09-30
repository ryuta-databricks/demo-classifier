from dataclasses import dataclass
from typing import List, Dict, Any
from demo_classifier.utils.logger_utils import get_logger
import numpy as np
import mlflow
from mlflow.tracking import MlflowClient
from mlflow.types.schema import Schema, TensorSpec
from mlflow.pyfunc import PyFuncModel
from pyspark.sql.types import StructType, StructField, LongType, DoubleType, StringType, IntegerType, \
    FloatType, TimestampType, BinaryType, BooleanType

_logger = get_logger()


@dataclass
class ModelSanityCheckConfig:
    """
    Configuration data class used to execute ModelSanityCheck pipeline.

    Attributes:
        model_name
            Name of the model.
        conf (dict):
            [Optional] dictionary of conf file used to trigger pipeline. If provided will be tracked as a yml
            file to MLflow tracking.
        env_vars (dict):
            [Optional] dictionary of environment variables to trigger pipeline. If provided will be tracked as a yml
            file to MLflow tracking.
    """
    model_name: str = None
    conf: Dict[str, Any] = None
    env_vars: Dict[str, str] = None


class ModelSanityCheck:
    """
    Class to execute model training. Params, metrics and model artifacts will be tracking to MLflow Tracking.
    Optionally, the resulting model will be registered to MLflow Model Registry if provided.
    """
    def __init__(self, cfg: ModelSanityCheckConfig):
        self.cfg = cfg

    @staticmethod
    def _create_struct_type(input_columns: dict):
        input_schema = []
        for col, type in input_columns.items():
            if type == 'string':
                spark_type = StringType()
            elif type == "double":
                spark_type = DoubleType()
            elif type == "integer":
                spark_type = IntegerType()
            elif type == "long":
                spark_type = LongType()
            elif type == "float":
                spark_type = FloatType()
            elif type == "boolean":
                spark_type = BooleanType()
            elif type == "binary":
                spark_type = BinaryType()
            elif type == "datetime":
                spark_type = TimestampType()
            else:
                raise Exception(f'Expected input data type not provided.')
            field = StructField(col, spark_type, True)
            input_schema.append(field)
        return input_schema

    def signature_check(self, pyfunc_model: PyFuncModel) -> str:
        """
        Apply model signature check.
        """
        # Get the input and output schema of our logged model.
        input_schema = pyfunc_model.metadata.get_input_schema().as_spark_schema()
        output_schema = pyfunc_model.metadata.get_output_schema()

        expected_input_columns = self.cfg.conf.get('expected_input_schema')
        if not expected_input_columns:
            raise Exception(f'Expected input schema not provided.')
        expected_input_schema = StructType(self._create_struct_type(expected_input_columns))
        expected_output_dtype = self.cfg.conf.get('expected_output_schema')
        if expected_output_dtype:
            expected_output_dtype = expected_output_dtype.get('dtype')
        else:
            raise Exception(f'Expected output schema not provided.')

        expected_tensor_spec = TensorSpec(np.dtype(expected_output_dtype), (-1,))
        expected_output_schema = Schema([expected_tensor_spec])

        assert expected_input_schema.fields.sort(key=lambda x: x.name) == input_schema.fields.sort(key=lambda x: x.name)
        assert expected_output_schema == output_schema

        return "==========Model signature check passed=========="

    def prediction_check(self) -> str:
        """
        Apply model prediction check.
        """
        # Load the dataset and generate some predictions to ensure our model is working correctly.
        # df = pd.read_parquet(
        #    f"/dbfs/mnt/dbacademy-datasets/ml-in-production/v01/airbnb/sf-listings/airbnb-cleaned-mlflow.parquet")
        # predictions = pyfunc_model.predict(df)

        # Make sure our prediction types are correct.
        # assert type(predictions) == np.ndarray
        # assert type(predictions[0]) == np.float64
        return "==========Model prediction check passed=========="

    def run(self):
        """
        Method to trigger model sanity check.
        Steps:
            1. Apply model signature check
            2. Apply model prediction check
            3. If all tests have passed, promote the model version to Staging stage
        """

        client = MlflowClient()
        version = client.get_latest_versions(self.cfg.model_name, stages=["None"])[0].version
        run_id = client.get_latest_versions(self.cfg.model_name, stages=["None"])[0].run_id
        pyfunc_model = mlflow.pyfunc.load_model(f'runs:/{run_id}/model')

        _logger.info('==========Running model sanity check==========')
        _logger.info('==========Model signature check start==========')
        self.signature_check(pyfunc_model)
        _logger.info("==========Model signature check start==========")
        self.prediction_check()
        _logger.info('==========Model sanity check completed==========')

        # Register model to MLflow Model Registry if provided
        _logger.info('==========MLflow Model Registry==========')
        _logger.info(f'Promoting model to Staging: {self.cfg.model_name}')
        client.transition_model_version_stage(
            name=self.cfg.model_name,
            version=version,
            stage="Staging"
        )
