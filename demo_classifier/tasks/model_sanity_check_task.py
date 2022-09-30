from demo_classifier.common import Task
from demo_classifier.model_sanity_check import ModelSanityCheck, ModelSanityCheckConfig
from demo_classifier.utils.logger_utils import get_logger

_logger = get_logger()


class ModelSanityCheckTask(Task):

    def launch(self):
        _logger.info('Starting ModelSanityCheck task')
        _logger.info(f'Running model-sanity-check pipeline in {self.env_vars["env"]} environment')
        cfg = ModelSanityCheckConfig(model_name=self.env_vars["model_name"],
                                     conf=self.conf,
                                     env_vars=self.env_vars)
        ModelSanityCheck(cfg).run()
        _logger.info('All tests passed!')


def entrypoint():  # pragma: no cover
    task = ModelSanityCheckTask()
    task.launch()

# if you're using spark_python_task, you'll need the __main__ block to start the code execution
if __name__ == '__main__':
    entrypoint()
