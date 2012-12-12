#!/usr/bin/env python
import os
from pkg_resources import Requirement, resource_filename
from setuptools import setup, find_packages
import shutil
import subprocess
import sys

README = os.path.join(os.path.dirname(__file__), 'README.md')
long_description = open(README).read() + '\n\n'

PACKAGE = "petrel"

def get_version(argv):
    """ Dynamically calculate the version based on VERSION."""
    if "install" in argv or "egg_info" in argv:
        #means setup.py is called from deployment process
        return "0.0.0"
    else:
        try:
            git_call = subprocess.Popen(['git','describe','--abbrev=4','HEAD'],
                                        stdout=subprocess.PIPE)
            return git_call.stdout.read().strip()
        except OSError:
            return "0.0.0"

#def copy_config():
#    """Copies the sample configuration if necessary to $PATH/etc/package"""
#    # Get the file.
#    conf_filename = "%s.conf" % PACKAGE
#    conf_dir = "etc/%s" % PACKAGE
#    conf_path = os.path.join(os.getenv("HOME"), conf_dir)
#    conf_filepath = os.path.join(conf_path, "%s.conf" % PACKAGE)
#
#    filename = resource_filename(Requirement.parse(PACKAGE),
#        os.path.join(conf_dir, conf_filename))
#    try:
#        # Create the directory.
#        if not os.path.exists(conf_path):
#            os.makedirs(conf_path)
#
#        # Copy the source file. Don't clobber existing files.
#        shutil.copyfile(filename, "%s.sample" % conf_filepath)
#        if not os.path.exists(conf_filepath):
#            shutil.copyfile(filename, conf_filepath)
#        else:
#            print "Old conf for %s exists" % conf_filepath
#    except IOError as error:
#        print "Unable to copy file %s" % error
#
#def create_dirs():
#    """Create the necesary dirs structure the package"""
#    pwd =  os.environ['PWD']
#    log_path = os.path.join(os.environ['PWD'], "var/log/", PACKAGE)
#    if not os.path.exists(log_path):
#        os.makedirs(log_path)
#
#if 'install' in sys.argv:
#    copy_config()
#    create_dirs()

setup(name=PACKAGE
    ,version=get_version(sys.argv)
    ,description=("Storm Topology Builder. AirSage, Inc")
    ,long_description=long_description
    ,classifiers=[
         "Programming Language :: Python"
        ,("Topic :: Software Development :: Libraries :: Python Modules")
    ]
    ,keywords='Storm Topology Builder'
    ,author='bhart'
    ,url='http://www.airsage.com'
    ,scripts=[
         'bin/petrel',
        ]
    ,packages=find_packages()
    ,license='Copyright AirSage, Inc'
    ,install_requires=[
        'simplejson>=2.6.0',
        # Request specific Thrift version. Storm is in Java and may be sensitive to version incompatibilities.
        'thrift==0.8.0',
        'PyYAML>=3.10',
    ]
    # Setting this flag makes Petrel easier to debug within a running topology.
    ,zip_safe=False)
