Petrel
======

Tools for writing, submitting, debugging, and monitoring Storm topologies in pure Python.

Overview
========

While Storm has basic support for any Thrift-compatible language, that support is quite minimal:

* Storm communicates with other languages by sending JSON messages through stdin and stdout. This makes it difficult to use pdb for debugging. Also, this design may not offer the best performance.
* There is no easy way to supply configuration information when submitting a topology.
* The Storm client for Python supplied in storm-starter is very basic.
 * It supports implementing spouts and bolts but not describing topologies. Thus you have to write Java code to describe your Python topology.
 * It has little or no support for including Python packages (.tar.gz or .egg files) with a topology.
 * It has no support for testing spouts or bolts outside of Storm.
 * It has potential performance issues (e.g. building a dictionary by inserting one key at a time).
 *It has no logging. If a spout or bolt raises an exception, the task will die without capturing any information about what happened or why.

Petrel addresses these issues.

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

Execute
-------

Petrel makes it easy to run multiple versions of a topology side by side, as long as the code differences are manageable by virtualenv. Before a spout or bolt starts up, Petrel creates a new Python virtualenv and runs the topology-specific setup.sh script to install Python packages. It is shared by all the spouts or bolts from that instance of the topology on that machine.

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
