#!/usr/bin/env bash

# TODO: We could also loop over Storm versions and modify pom.xml accordingly.
for version in 2.7.13 3.5.3
do
    virtualenv_name=Petrel-${version}
    pyenv uninstall -f ${virtualenv_name}
    pyenv virtualenv ${version} ${virtualenv_name}
    source /home/barry/.pyenv/versions/Petrel-2.7.13/bin/activate
    pip install -U pip setuptools wheel
    pushd jvmpetrel
    mvn clean
    popd
    pushd petrel
    python setup.py bdist_wheel
    popd
done

