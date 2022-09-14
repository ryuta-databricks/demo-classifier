from demo_classifier.common import Task, FeatureStoreTableConfig, LabelsTableConfig
from demo_classifier.feature_table_refresher import FeatureTableRefresher, FeatureTableRefresherConfig
from demo_classifier.featurize import FeaturizerConfig
from demo_classifier.utils.logger_utils import get_logger

_logger = get_logger()


class FeatureTableRefresherTask(Task):

    def _get_input_table(self) -> dict:
        return self.conf['input_table']

    def _get_data_prep_params(self) -> FeaturizerConfig:
        return FeaturizerConfig(**self.conf['data_prep_params'])

    def _get_feature_store_table_cfg(self) -> FeatureStoreTableConfig:
        return FeatureStoreTableConfig(database_name=self.env_vars['feature_store_database_name'],
                                       table_name=self.env_vars['feature_store_table_name'],
                                       primary_keys=self.env_vars['feature_store_table_primary_keys'],
                                       description=self.env_vars['feature_store_table_description'])

    def _get_labels_table_cfg(self) -> LabelsTableConfig:
        return LabelsTableConfig(database_name=self.env_vars['labels_table_database_name'],
                                 table_name=self.env_vars['labels_table_name'],
                                 label_col=self.env_vars['labels_table_label_col'],
                                 dbfs_path=self.env_vars['labels_table_dbfs_path'])

    def launch(self) -> None:
        """
        Launch FeatureStoreRefresherTable job
        """
        _logger.info('Launching FeatureTableRefresher job')
        _logger.info(f'Running feature-table-refresher pipeline in {self.env_vars["env"]} environment')
        cfg = FeatureTableRefresherConfig(input_table=self._get_input_table(),
                                        featurizer_cfg=self._get_data_prep_params(),
                                        feature_store_table_cfg=self._get_feature_store_table_cfg(),
                                        labels_table_cfg=self._get_labels_table_cfg())
        FeatureTableRefresher(cfg).run()
        _logger.info('FeatureTableRefresher job finished!')

# if you're using python_wheel_task, you'll need the entrypoint function to be used in setup.py
def entrypoint():  # pragma: no cover
    task = FeatureTableRefresherTask()
    task.launch()

# if you're using spark_python_task, you'll need the __main__ block to start the code execution
if __name__ == '__main__':
    entrypoint()
