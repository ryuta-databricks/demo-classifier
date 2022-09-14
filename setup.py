"""
This file configures the Python package with entrypoints used for future runs on Databricks.

Please follow the `entry_points` documentation for more details on how to configure the entrypoint:
* https://setuptools.pypa.io/en/latest/userguide/entry_point.html
"""

from setuptools import find_packages, setup
from demo_classifier import __version__

PACKAGE_REQUIREMENTS = ["pyyaml"]

# packages for local development and unit testing
# please note that these packages are already available in DBR, there is no need to install them on DBR.
LOCAL_REQUIREMENTS = [
    "pyspark==3.2.1",
    "delta-spark==1.1.0",
    "scikit-learn",
    "pandas",
    "mlflow",
    "python-dotenv",
]

TEST_REQUIREMENTS = [
    # development & testing tools
    "coverage[toml]",
    "setuptools==58.0.4",
    "wheel==0.37.0",
    "pyspark",
    "numpy==1.20.3",
    "pandas==1.3.4",
    "scikit-learn==0.24.2",
    "pyyaml==6.0",
    "pytest==7.1.2",
    "pytest-cov==3.0.0",
    "dbx>=0.7,<0.8"
    "delta-spark",
    "python-dotenv",
]

setup(
    name="demo_classifier",
    packages=find_packages(exclude=["tests", "tests.*"]),
    setup_requires=["setuptools","wheel"],
    install_requires=PACKAGE_REQUIREMENTS,
    extras_require={"local": LOCAL_REQUIREMENTS, "test": TEST_REQUIREMENTS},
    entry_points = {
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
