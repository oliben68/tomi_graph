from setuptools import setup
import sys

from setuptools.command.test import test as TestCommand

PACKAGE_NAME="hopla"


class PyTest(TestCommand):
    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = "--disable-pytest-warnings --cov-report term-missing --cov={name} -s -v".format(name=PACKAGE_NAME)

    def run_tests(self):
        import shlex
        import pytest

        err_no = pytest.main(shlex.split(self.pytest_args))
        sys.exit(err_no)

setup(
    name=PACKAGE_NAME,
    version='0.0.1',
    packages=['hopla',
              'hopla.documents',
              'hopla.documents.core',
              'hopla.documents.schema_based',
              'hopla.events',
              'hopla.logging',
              'hopla.model',
              'hopla.model.config',
              'hopla.model.core', ],
    url='',
    license='',
    author='Olivier Steck',
    author_email='osteck@gmail.com',
    description='Headless CMS',
    install_requires=['PyDispatcher',
                      'attrs',
                      'chardet',
                      'jsonschema',
                      'neo4j',
                      'objectpath',
                      'testfixtures',
                      'ujson', ],
    extras_require=dict(
        test=['testfixtures'],
        ),
    setup_requires=["pytest", ],
    tests_require=["pytest",
                   "pytest_cov", ],
    cmdclass={"pytest": PyTest},
)
