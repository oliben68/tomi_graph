##!/usr/bin/env bash
#
#ROOT=tomi
#COMPONENT=base
#PROJECT=${ROOT}_${COMPONENT}
#
#rm -rf /Users/oliviersteck/Documents/sources/python/${ROOT}/${PROJECT}/build
#
#echo "vanilla env"
#echo
#python_bin=/usr/local/anaconda3/envs/vanilla/bin/python
#pip_bin=/usr/local/anaconda3/envs/vanilla/bin/pip
#${pip_bin} uninstall ${PROJECT} -y
#${pip_bin} install .
#${python_bin} setup.py install --force; python setup.py test
#echo "---------------------------------------------------------------------------------------------------------------------------------------"
#
#echo
#
#echo "hopla env"
#echo
#python_bin=/usr/local/anaconda3/envs/hopla/bin/python
#pip_bin=/usr/local/anaconda3/envs/hopla/bin/pip
#${pip_bin} uninstall ${PROJECT} -y
#${pip_bin} install .
#${python_bin} setup.py install --force; python setup.py test
#echo "---------------------------------------------------------------------------------------------------------------------------------------"

#!/usr/bin/env bash

ROOT=tomi
COMPONENT=base
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