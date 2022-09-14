"""
This file configures the Python package with entrypoints used for future runs on Databricks.

Please follow the `entry_points` documentation for more details on how to configure the entrypoint:
* https://setuptools.pypa.io/en/latest/userguide/entry_point.html
"""

from setuptools import find_packages, setup
from demo_classifier import __version__

setup(
    name="demo_classifier",
    packages=find_packages(exclude=["tests", "tests.*"]),
    setup_requires=["setuptools","wheel"],
    entry_points={
        "console_scripts": [
            "feature_table_refresh = demo_classifier.tasks.feature_table_refresh_task:entrypoint",
            "model_train = demo_classifier.tasks.model_train_task:entrypoint",
            "model_deployment = demo_classifier.tasks.model_deployment_task:entrypoint",
            "model_inference_batch = demo_classifier.tasks.model_inference_batch_task:entrypoint",
    ]},
    version=__version__,
    description="",
    author="",
)
