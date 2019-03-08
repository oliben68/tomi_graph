#!/usr/bin/env bash

ROOT=tomi
COMPONENT=graph
PROJECT=${ROOT}_${COMPONENT}

rm -rf /Users/oliviersteck/Documents/sources/python/${ROOT}/${PROJECT}/build


function install_env {
    ENV_NAME=$1
    echo "${ENV_NAME} env"
    echo
    python_bin=/usr/local/anaconda3/envs/${ENV_NAME}/bin/python
    pip_bin=/usr/local/anaconda3/envs/${ENV_NAME}/bin/pip
    ${pip_bin} uninstall ${PROJECT} -y
    ${python_bin} setup.py install --force; python setup.py test
}

install_env "vanilla"
echo "---------------------------------------------------------------------------------------------------------------------------------------"

install_env "hopla"
echo "---------------------------------------------------------------------------------------------------------------------------------------"