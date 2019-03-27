import os
import sys

import yaml
from setuptools import find_packages
from setuptools import setup
from setuptools.command.test import test as test_command


def _load_setup_info():
    with open(os.path.join(os.getcwd(), ".setup_info")) as pkg_info:
        return yaml.load(pkg_info, Loader=yaml.FullLoader)["package"]


SETUP_INFO = _load_setup_info()
TESTING = SETUP_INFO["tests"]
CONF_PKG = SETUP_INFO["configuration_pkg"]


class PyTest(test_command):
    user_options = [("pytest-args=", "a", "Arguments to pass to pytest")]

    def initialize_options(me):
        test_command.initialize_options(me)
        me.pytest_args = SETUP_INFO["testing"][TESTING]["args"].format(name=SETUP_INFO["name"])

    def run_tests(self):
        import shlex
        import pytest

        err_no = pytest.main(shlex.split(self.pytest_args))
        sys.exit(err_no)


setup(
    name=SETUP_INFO["name"],
    version=SETUP_INFO["version"],
    packages=find_packages(),
    url='',
    license='',
    author='Olivier Steck',
    author_email='osteck@gmail.com',
    description='TBD',
    install_requires=['PyDispatcher',
                      'attrs',
                      'chardet',
                      'jsonschema',
                      'neo4j',
                      'morph',
                      'objectpath',
                      'py',
                      'python_cypher',
                      'testfixtures',
                      'ujson',
                      'uri',
                      'pyyaml', 'neobolt'],
    extras_require=dict(
        test=['testfixtures', ],
    ),
    setup_requires=["pytest",
                    "pyyaml", ],
    tests_require=["pytest",
                   "pytest_cov", ],
    cmdclass={"pytest": PyTest},
)
