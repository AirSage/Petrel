Petrel
======

Tools for writing, submitting, debugging, and monitoring Storm topologies in pure Python.

NOTE: Unlike the base Storm package, which only requires Python 2.6, Petrel requires Python 2.7.

Overview
========

Petrel offers some important improvements over the storm.py module provided with Storm:

* Topologies are implemented in 100% Python
* Petrel's packaging support automatically sets up a Python virtual environment for your topology and makes it easy to install additional Python packages.
* "petrel.mock" allows testing of single components or single chains of related components.
* Petrel automatically sets up logging for every spout or bolt and logs a stack trace on unhandled errors.

Topology definition
===================

<pre>
import randomsentence
import splitsentence
import wordcount

def create(builder):
    builder.setSpout("spout", randomsentence.RandomSentenceSpout(), 1)
    builder.setBolt("split", splitsentence.SplitSentenceBolt(), 1).shuffleGrouping("spout")
    builder.setBolt("count", wordcount.WordCountBolt(), 1).fieldsGrouping("split", ["word"])
</pre>

setup.sh
--------

A topology may optionally include a setup.sh script. If present, Petrel will execute it before launching the spout or bolt. Typically this script is used for installing additional Python libraries. Here's an example setup.sh script:

<pre>
set -e

# $1 will be non-zero if creating a new virtualenv, zero if reusing an existing one.
if [ $1 -ne 0 ]; then
    for f in Shapely==1.2.15 pyproj==1.9.0 pycassa==1.7.0 \
             configobj==4.7.2 greenlet==0.4.0 gevent==1.0b3
    do
        echo "Installing $f"
        pip install $f
    done
fi
</pre>

Topology Configuration
----------------------

Petrel's "--config" parameter accepts a YAML file with standard Storm configuration options. Petre also provides some Petrel-specific settings. See below.

```
topology.message.timeout.secs: 150
topology.ackers: 1
topology.workers: 5
topology.max.spout.pending: 1
worker.childopts: "-Xmx4096m"
topology.worker.childopts: "-Xmx4096m"

# Controls how Petrel installs its own dependencies, e.g. simplejson, thrift, PyYAML.
petrel.pip_options: "--no-index -f http://10.255.3.20/pip/"

# If you prefer, you can configure parallelism here instead of in setSpout() or
# setBolt().
petrel.parallelism.splitsentence: 1
```

Building and submitting topologies
==================================

Use the following command to package and submit a topology to Storm:

<pre>
petrel submit --sourcejar ../../jvmpetrel/target/storm-petrel-*-SNAPSHOT.jar --config localhost.yaml wordcount
</pre>

This command builds and submits a topology.

Build
-----

* Get the topology definition by loading the create.py script and calling create().
* Package a JAR containing the topology definition, code, and configuration.
* Files listed in manifest.txt, e.g. additional configuration files

Deploy and Run
--------------

To deploy and run a Petrel topology on a Storm cluster, each Storm worker must have the following installed:

* Python 2.7
* setuptools
* virtualenv

Note that the worker machines don't require Petrel itself to be installed. Only the *submitting* machine needs to have Petrel. Each time you submit a topology using Petrel, it creates a custom jar file with the Petrel egg and and your Python spout and bolt code. These files in the wordcount example show how this works:

* buildandrun
* manifest.txt

Because Petrel topologies are self contained, it is easy to run multiple versions of a topology on the same cluster, as long as the code differences are contained within virtualenv. Before a spout or bolt starts up, Petrel creates a new Python virtualenv and runs the optional topology-specific setup.sh script to install Python packages. This virtual environment is shared by all the spouts or bolts from that instance of the topology on that machine.

Monitoring
==========

Petrel provides a "status" command which lists the active topologies and tasks on a cluster. You can optionally filter by task name and Storm port (i.e. worker slot) number.

<pre>
petrel status 10.255.1.58
</pre>

Logging
=======

Petrel redirects stdout and stderr to the Python logger.

When Storm is running on a cluster, it can be nice to send certain messages (e.g. errors) to a central machine. Petrel provides the NIMBUS_HOST environment variable to help support this. For example, the following configuration declares a log handler which sends any worker log messages INFO or higher to the Nimbus host.

<pre>
[handler_hand02]
class=handlers.SysLogHandler
level=INFO
formatter=form02
args=((os.getenv('NIMBUS_HOST') or 'localhost',handlers.SYSLOG_UDP_PORT),handlers.SysLogHandler.LOG_USER)
</pre>

Petrel also has a "StormHandler" class sends messages to the Storm logger. This feature is currently not "released", but can be enabled by uncommenting the following line in petrel/util.py:

<pre>
#logging.StormHandler = StormHandler
</pre>


Testing
=======

Petrel provides a "mock" module which mocks some of Storm's features. This makes it possible to test individual components and simple topologies in pure Python, without relying on the Storm runtime.

<pre>
def test():
    bolt = WordCountBolt()
    
    from petrel import mock
    from randomsentence import RandomSentenceSpout
    mock_spout = mock.MockSpout(RandomSentenceSpout.declareOutputFields(), [
        ['word'],
        ['other'],
        ['word'],
    ])
    
    result = mock.run_simple_topology([mock_spout, bolt], result_type=mock.LIST)
    assert_equal(2, bolt._count['word'])
    assert_equal(1, bolt._count['other'])
    assert_equal([['word', 1], ['other', 1], ['word', 2]], result[bolt])
</pre>

In Petrel terms, a "simple" topology is one which only outputs to the default stream and has no branches or loops. run_simple_topology() assumes the first component in the list is a spout, and it passes the output of each component to the next component in the list.

License
=======

The use and distribution terms for this software are covered by the BSD 3-clause license 1.0 (http://opensource.org/licenses/BSD-3-Clause) which can be found in the file LICENSE.txt at the root of this distribution. By using this software in any fashion, you are agreeing to be bound by the terms of this license. You must not remove this notice, or any other, from this software.

Installing Petrel as an egg
===========================

Before installing Petrel, make sure Storm is installed and in your path. Run the following command:

    storm version
    
This will print the version of Storm active on your system, a number such as "0.7.4". You must use a version of Petrel whose first 3 digits match this version.

Install the egg:

easy_install petrel*.egg

This will download a few dependencies and then print a message like:

    Finished processing dependencies for petrel==0.7.4.0.1

Setting up Petrel from source
=============================

If you plan to use use Petrel by cloning its source code repository from github.com, follow these instructions.

Ensure the following tools are installed:

* Storm
    * Test with "storm version"
    * Should print something like "0.7.4"
* Thrift compiler
    * Test with "thrift -version"
    * Should print "Thrift version 0.7.0"
* Maven (test with "mvn -version")

Clone Petrel from github. Then run:

    cd Petrel/petrel
    python setup.py develop

This will download a few dependencies and then print a message like:

    Finished processing dependencies for petrel==0.7.4.0.1

Running the word count example
==============================

From the base Petrel directory, run:

    cd samples/wordcount
    ./buildandrun --config topology.yaml

This will run the topology in local mode. You can run it on a real cluster by providing an additional parameter, the name of the topology:

    ./buildandrun --config topology.yaml wordcount
