import unittest
from cStringIO import StringIO

from petrel.topologybuilder import TopologyBuilder, BaseRichSpout, BaseRichBolt
from petrel.generated.storm.ttypes import Bolt, SpoutSpec

class RandomSentenceSpout(BaseRichSpout):
    def __init__(self, execution_command=None):
        super(RandomSentenceSpout, self).__init__(script='randomsentence.py', execution_command=execution_command)

    def declareOutputFields(self):
        return ['sentence']

class SplitSentence(BaseRichBolt):
    def __init__(self, execution_command=None):
        super(SplitSentence, self).__init__(script='splitsentence.py', execution_command=execution_command)

    def declareOutputFields(self):
        return ['word']

class WordCount(BaseRichBolt):
    def __init__(self, execution_command=None):
        super(WordCount, self).__init__(script='wordcount.py', execution_command=execution_command)

    def declareOutputFields(self):
        return ['word', 'count']

class TestTopology(unittest.TestCase):
    def test1(self):
        # Build a topology
        builder = TopologyBuilder()
        builder.setSpout("spout", RandomSentenceSpout(), 5)
        builder.setBolt("split", SplitSentence(), 8).shuffleGrouping("spout")
        builder.setBolt("count", WordCount(), 12).fieldsGrouping("split", ["word"])

        # Save the topology.        
        io_out = StringIO()
        builder.write(io_out)
        
        # Read the topology.
        io_in = StringIO(io_out.getvalue())
        topology = builder.read(io_in)
        
        # Verify the topology settings were saved and loaded correctly.
        self.assertEqual(['spout'], topology.spouts.keys())
        self.assertEqual(['count', 'split'], sorted(topology.bolts.keys()))

        spout = topology.spouts['spout']
        self.assertEqual('python', spout.spout_object.shell.execution_command)
        self.assertEqual('randomsentence.py', spout.spout_object.shell.script)
        self.assertEqual(['default'], sorted(spout.common.streams.keys()))
        self.assertEqual(['sentence'], spout.common.streams['default'].output_fields)
        self.assertEqual(False, spout.common.streams['default'].direct)

        bolt = topology.bolts['split']
        self.assertEqual('python', bolt.bolt_object.shell.execution_command)
        self.assertEqual('splitsentence.py', bolt.bolt_object.shell.script)
        self.assertEqual(['default'], sorted(bolt.common.streams.keys()))
        self.assertEqual(['word'], bolt.common.streams['default'].output_fields)
        self.assertEqual(False, bolt.common.streams['default'].direct)

        bolt = topology.bolts['count']
        self.assertEqual('python', bolt.bolt_object.shell.execution_command)
        self.assertEqual('wordcount.py', bolt.bolt_object.shell.script)
        self.assertEqual(['default'], sorted(bolt.common.streams.keys()))
        self.assertEqual(['count'], bolt.common.streams['default'].output_fields)
        self.assertEqual(False, bolt.common.streams['default'].direct)
