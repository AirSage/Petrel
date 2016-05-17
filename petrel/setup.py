#!/usr/bin/env python
import os
from pkg_resources import Requirement, resource_filename
from setuptools import setup, find_packages
import shutil
import subprocess
import sys
import urllib2
import re

README = os.path.join(os.path.dirname(__file__), 'README.txt')
long_description = open(README).read() + '\n\n'

PACKAGE = "petrel"

PETREL_VERSION = '0.3'

def get_storm_version():
    version_output = [s.strip() for s in subprocess.check_output(['storm', 'version']).split('\n')]
    for line in version_output:
        m = re.search(r'^(Storm )?(\d+\.\d+\.\d+)(-(\w+))?$', line)
        if m is not None:
            break
    return m.group(0), m.group(2)


def get_version(argv):
    """ Dynamically calculate the version based on VERSION."""
    return '%s.%s' % (get_storm_version()[1], PETREL_VERSION)


def build_petrel():
    version_string, version_number = get_storm_version()
    
    # Generate Thrift Python wrappers.
    if os.path.isdir('petrel/generated'):
        shutil.rmtree('petrel/generated')
    os.mkdir('petrel/generated')
    version_tuple = tuple([int(s) for s in version_number.split('.')[:3]])
    if version_tuple <= (0, 9, 0):
        path = '%s/src/storm.thrift' % version_string
        f_url = urllib2.urlopen('https://raw.github.com/apache/incubator-storm/%s' % path)
    elif version_tuple <= (0, 9, 1):
        path = 'apache-%s/storm-core/src/storm.thrift' % version_number
        f_url = urllib2.urlopen('https://raw.github.com/apache/incubator-storm/%s' % path)
    elif version_tuple == (0, 9, 2):
        f_url = urllib2.urlopen('https://raw.githubusercontent.com/apache/storm/v0.9.2-incubating/storm-core/src/storm.thrift')
    elif version_tuple[:2] == (1, 0):
        f_url = urllib2.urlopen('https://raw.githubusercontent.com/HeartSaVioR/storm/ad46a470c173c8daf2bd76bc10ecbfc6fd08865b/storm-core/src/storm.thrift')
    else:
        f_url = urllib2.urlopen('https://raw.githubusercontent.com/apache/storm/v%s/storm-core/src/storm.thrift' % version_number)

    with open('storm.thrift', 'w') as f:
        f.write(f_url.read())
    f_url.close()
    old_cwd = os.getcwd()
    os.chdir('petrel/generated')
    
    subprocess.check_call(['thrift', '-gen', 'py', '-out', '.', '../../storm.thrift'])    
    os.chdir(old_cwd)
    os.remove('storm.thrift')
    
    # Build JVMPetrel.
    os.chdir('../jvmpetrel')
    subprocess.check_call(['mvn', '-Dstorm_version=%s' % version_number, 'assembly:assembly'])
    os.chdir(old_cwd)
    shutil.copyfile(
        '../jvmpetrel/target/storm-petrel-%s-SNAPSHOT-jar-with-dependencies.jar' % version_number,
        'petrel/generated/storm-petrel-%s-SNAPSHOT-jar-with-dependencies.jar' % version_number)

if 'bdist_egg' in sys.argv or 'develop' in sys.argv:
    build_petrel()

setup(name=PACKAGE
    ,version=get_version(sys.argv)
    ,description=("Storm Topology Builder")
    ,long_description=long_description
    ,classifiers=[
         "Programming Language :: Python"
        ,"Operating System :: POSIX :: Linux"
        ,"Development Status :: 5 - Production/Stable"
        ,"Intended Audience :: Developers"
        ,"License :: OSI Approved :: BSD License"
        ,"Topic :: Software Development :: Libraries :: Python Modules"
        ,"Topic :: System :: Distributed Computing"
    ]
    ,keywords='Storm Topology Builder'
    ,author='bhart'
    ,url='https://github.com/AirSage/Petrel'
    ,scripts=[
         'bin/petrel',
        ]
    ,packages=find_packages()
    ,package_data={'': ['*.jar']}
    ,license='BSD 3-clause'
    ,install_requires=[
        'simplejson==2.6.1',
        # Request specific Thrift version. Storm is in Java and may be sensitive to version incompatibilities.
        'thrift==0.8.0',
        'PyYAML==3.10',
    ]
    # Setting this flag makes Petrel easier to debug within a running topology.
    ,zip_safe=False)
