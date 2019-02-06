import glob
import os
import site
import sys
from distutils.dir_util import copy_tree

import yaml
from setuptools import Command
from setuptools import find_packages
from setuptools import setup
from setuptools.command.test import test as TestCommand


def _load_setup_info():
    with open(os.path.join(os.getcwd(), ".setup_info")) as pkg_info:
        return yaml.load(pkg_info)["package"]


SETUP_INFO = _load_setup_info()
TESTING = SETUP_INFO["tests"]
CONF_PKG = SETUP_INFO["configuration_pkg"]


class PyTest(TestCommand):
    user_options = [("pytest-args=", "a", "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = SETUP_INFO["testing"][TESTING]["args"].format(name=SETUP_INFO["name"])

    def run_tests(self):
        import shlex
        import pytest

        err_no = pytest.main(shlex.split(self.pytest_args))
        sys.exit(err_no)


class ConfigInstaller(Command):
    description = 'install configuration files'

    user_options = [('config-dir=', 'd', 'config directory'), ]

    def initialize_options(self):
        self.config_dir = None

    def finalize_options(self):
        if self.config_dir is None:
            raise Exception("Parameter --config-dir is missing")
        if not os.path.isdir(self.config_dir):
            raise Exception("Config directory does not exist: {0}".format(self.config_dir))

    def run(self):
        def install_in_target(target_config_dir):
            if not os.path.isdir(target_config_dir):
                print("!" * 16, "Skipping {dir}: not found!".format(dir=target_config_dir), "!" * 16)
                return
            print("@" * 16, "Patching the configuration in {pkg}".format(pkg=target_config_dir))
            files = [filename for filename in
                     glob.iglob(os.path.join(self.config_dir, '**/*'), recursive=True)]
            imports = [
                "from {pkg_name}.{f} import *".format(
                    f=filename.replace(self.config_dir + "/", "").replace("/", ".").replace(".py", ""),
                    pkg_name="{p}.{conf_pkg}".format(p=SETUP_INFO["name"], conf_pkg=CONF_PKG)).strip()
                for filename in
                files if os.path.splitext(filename)[1] == ".py"]

            init_py = os.path.join(target_config_dir, "__init__.py")
            if os.path.isfile(init_py):
                print("Updating {i}...".format(i=init_py))
                with open(os.path.join(target_config_dir, "__init__.py"), "a") as init_py_file:
                    init_py_file.writelines("# GENERATED AT CONFIGURATION PHASE: DO NOT EDIT!\n\n")
                    for import_statement in imports:
                        init_py_file.writelines(import_statement.strip() + "\n")
            else:
                print("Creating {i}...".format(i=init_py))
                with open(os.path.join(target_config_dir, "__init__.py"), "w") as init_py_file:
                    init_py_file.writelines("# GENERATED AT CONFIGURATION PHASE: DO NOT EDIT!\n\n")
                    for import_statement in imports:
                        init_py_file.writelines(import_statement.strip() + "\n")
            print("@" * 16, "Copying {f} to {t}".format(f=self.config_dir, t=target_config_dir))
            copy_tree(self.config_dir, target_config_dir)

        for site_package_dir in site.getsitepackages():
            # trying egg
            install_in_target(os.path.join(site_package_dir, SETUP_INFO["name"] + "-" + SETUP_INFO[
                "version"] + "-py" + ".".join(sys.version.split()[0].split(".")[:-1]) + ".egg", SETUP_INFO["name"],
                                           CONF_PKG))
            install_in_target(os.path.join(site_package_dir, SETUP_INFO["name"], CONF_PKG))


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
    cmdclass={'config': ConfigInstaller,
              "pytest": PyTest},
)
