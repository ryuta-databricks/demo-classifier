from demo_classifier.common import Task, MLflowTrackingConfig
from demo_classifier.model_deployment import ModelDeployment, ModelDeploymentConfig
from demo_classifier.utils.logger_utils import get_logger

_logger = get_logger()


class ModelDeploymentTask(Task):

    def _get_mlflow_tracking_cfg(self):
        return MLflowTrackingConfig(experiment_path=self.env_vars['model_deploy_experiment_path'],
                                    run_name='staging_vs_prod_comparison',
                                    model_name=self.env_vars['model_name'])

    def _get_reference_data(self) -> str:
        reference_table_database_name = self.env_vars['reference_table_database_name']
        reference_table_name = self.env_vars['reference_table_name']
        return f'{reference_table_database_name}.{reference_table_name}'

    def _get_reference_data_label_col(self) -> str:
        return self.env_vars['reference_table_label_col']

    def _get_model_comparison_params(self) -> dict:
        return self.conf['model_comparison_params']

    def launch(self):
        _logger.info('Launching ModelDeploymentJob job')
        _logger.info(f'Running model-deployment pipeline in {self.env_vars["env"]} environment')
        cfg = ModelDeploymentConfig(mlflow_tracking_cfg=self._get_mlflow_tracking_cfg(),
                                    reference_data=self._get_reference_data(),
                                    label_col=self._get_reference_data_label_col(),
                                    comparison_metric=self._get_model_comparison_params()['metric'],
                                    higher_is_better=self._get_model_comparison_params()['higher_is_better'])
        ModelDeployment(cfg).run()
        _logger.info('Launching ModelDeploymentJob job finished!')


# if you're using python_wheel_task, you'll need the entrypoint function to be used in setup.py
def entrypoint():  # pragma: no cover
    task = ModelDeploymentTask()
    task.launch()

# if you're using spark_python_task, you'll need the __main__ block to start the code execution
if __name__ == '__main__':
    entrypoint()
