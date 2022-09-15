import unittest
import sys
import yaml
import pathlib
from pyspark.dbutils import DBUtils  # noqa
from argparse import ArgumentParser
from demo_classifier.tasks.feature_table_refresh_task import FeatureTableRefresherTask
from demo_classifier.tasks.model_train_task import ModelTrainTask
from demo_classifier.tasks.model_deployment_task import ModelDeploymentTask
from demo_classifier.tasks.model_inference_batch_task import ModelInferenceTask


def _get_conf(conf: str):
    p = ArgumentParser()
    p.add_argument('--' + conf, required=False, type=str)
    namespace = p.parse_known_args(sys.argv[1:])[0]
    conf_file = vars(namespace)[conf]
    return yaml.safe_load(pathlib.Path(conf_file).read_text())


class IntegrationTest(unittest.TestCase):

    def setUp(self):
        self.feature_table_refresher_task = FeatureTableRefresherTask(init_conf=_get_conf('feature_table_refresh_config'))
        self.model_train_task = ModelTrainTask(init_conf=_get_conf('model_train_config'))
        self.model_deployment_task = ModelDeploymentTask(init_conf=_get_conf('model_deployment_config'))
        self.model_inference_task = ModelInferenceTask(init_conf=_get_conf('model_inference_batch_config'))

    def test_sample(self):
        self.feature_table_refresher_task.launch()
        self.model_train_task.launch()
        self.model_deployment_task.launch()
        self.model_inference_task.launch()

if __name__ == '__main__':
    # please don't change the logic of test result checks here
    # it's intentionally done in this way to comply with pipelines run result checks
    # for other tests, please simply replace the SampleJobIntegrationTest with your custom class name
    loader = unittest.TestLoader()
    tests = loader.loadTestsFromTestCase(IntegrationTest)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(tests)
    if not result.wasSuccessful():
        raise RuntimeError(
            'One or multiple tests failed. Please check job logs for additional information.'
        )
