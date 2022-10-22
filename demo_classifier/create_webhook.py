from dataclasses import dataclass
from typing import List, Dict, Any
from demo_classifier.utils.logger_utils import get_logger
from demo_classifier.common import get_dbutils
from demo_classifier.utils.get_spark import spark
import numpy as np
import requests
import json
import mlflow
from mlflow.utils.rest_utils import http_request
from mlflow.utils.databricks_utils import get_databricks_host_creds
from mlflow.tracking import MlflowClient

_logger = get_logger()


@dataclass
class WebhookCreationConfig:
    """
    Configuration data class used to execute ModelSanityCheck pipeline.

    Attributes:
        model_name
            Name of the model.
        sanity_check_job_name
            Name of the sanity_check_job_name.
    """
    model_name: str = None
    sanity_check_job_name: str = None


class WebhookCreation:
    """
    Class to execute webhook creation.
    """
    def __init__(self, cfg: WebhookCreationConfig):
        self.cfg = cfg

    @staticmethod
    def _find_job_id(work_space, headers, job_name, offset_limit=1000) -> str:
        """
        Find job_id of a sanity check job given a job name

        Parameters
        ----------
        fs_training_set : databricks.feature_store.training_set.TrainingSet
            Feature Store TrainingSet

        Returns
        -------
        train-test splits
        """
        params = {"offset": 0}
        uri = f"{work_space}/api/2.1/jobs/list"
        done = False
        job_id = None
        while not done:
            done = True
            res = requests.get(uri, params=params, headers=headers)
            assert res.status_code == 200, f"Job list not returned; {res.content}"

            jobs = res.json().get("jobs", [])
            if len(jobs) > 0:
                for job in jobs:
                    if job.get("settings", {}).get("name", None) == job_name:
                        job_id = job.get("job_id", None)
                        break

                # if job_id not found; update the offset and try again
                if job_id is None:
                    params["offset"] += len(jobs)
                    if params["offset"] < offset_limit:
                        done = False

        return job_id

    def run(self):
        """
        Method to trigger webhook creation.
        """
        dbutils = get_dbutils(spark)
        token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().getOrElse(None)
        headers = {"Authorization": f"Bearer {token}"}
        name = self.cfg.model_name
        work_space = "https://" + spark.conf.get("spark.databricks.workspaceUrl")
        job_name = self.cfg.sanity_check_job_name
        job_id = self._find_job_id(work_space, headers, job_name)
        if job_id is None:
            raise Exception(f"Sanity check job doesn't exist!")

        endpoint = f"/api/2.0/mlflow/registry-webhooks/list/?model_name={name.replace(' ', '%20')}"
        host_creds = get_databricks_host_creds("databricks")
        response = http_request(
            host_creds=host_creds,
            endpoint=endpoint,
            method="GET"
        )
        assert response.status_code == 200, f"Expected HTTP 200, received {response.status_code}"

        if not response.json():
            endpoint = "/api/2.0/mlflow/registry-webhooks/create"
            job_json = {"model_name": name,
                        "events": ["MODEL_VERSION_CREATED"],
                        "description": "Job webhook trigger",
                        "status": "Active",
                        "job_spec": {"job_id": job_id,
                                     "workspace_url": work_space,
                                     "access_token": token}
                        }
            response = http_request(
                host_creds=host_creds,
                endpoint=endpoint,
                method="POST",
                json=job_json
            )
            assert response.status_code == 200, f"Expected HTTP 200, received {response.status_code}"
            _logger.info("Webhook for this model created.")
        else:
            _logger.info("Webhook for this model already exists.")
