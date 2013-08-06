from petrel import storm
from collections import defaultdict
import time, logging, random


class RandomSentenceSpout(storm.Spout):
   	
	log = logging.getLogger('RandomSentenceSpout')

	def __init__(self, sentences):
		self.sentences = sentences
        
	def nextTuple(self):
		time.sleep(0.25)
		sentences = self.sentences
		sentence = sentences[random.randint(0, len(sentences) - 1)]
		self.log.debug('randomsentence emitting: %s', sentence)
		storm.emit([sentence])

	@classmethod
	def declareOutputFields(cls):
		return ['sentence']    


class SplitSentenceBolt(storm.BasicBolt):

	log = logging.getLogger('SplitSentenceBolt')

	def process(self, tup):
		self.log.debug('SplitSentenceBolt.process() called with: %s', tup)
		words = tup.values[0].split(" ")
		for word in words:
			self.log.debug('SplitSentenceBolt.process() emitting: %s', word)
			storm.emit([word])

	def declareOutputFields(self):
		return ['word']


class WordCountBolt(storm.BasicBolt):
    
    log = logging.getLogger('WordCountBolt')
    count = defaultdict(int)

    def process(self, tup):
        self.log.debug('WordCountBolt.process() called with: %s', tup)
        word = tup.values[0]
        self.count[word] += 1
        self.log.debug('WordCountBolt.process() emitting: %s', [word, self.count[word]])
        storm.emit([word, self.count[word]])

    def declareOutputFields(self):
        return ['word', 'count']


def create(builder):
	sentences = ["the cow jumped over the moon", "an apple a day keeps the doctor away", "four score and seven years ago"]

	builder.setSpout("spout", RandomSentenceSpout(sentences), 1)
	builder.setBolt("split", SplitSentenceBolt(), 1).shuffleGrouping("spout")
	builder.setBolt("count", WordCountBolt(), 1).fieldsGrouping("split", ["word"])


def test_topology():
	"""Run topology test with 'py.test wordcount.py'"""
	from petrel import mock

	mock_spout = mock.MockSpout(RandomSentenceSpout.declareOutputFields(), [["Madam, I'm Adam."]])
	split_sentence = SplitSentenceBolt()
	word_count = WordCountBolt()

	result = mock.run_simple_topology(None, [mock_spout, split_sentence, word_count], result_type=mock.LIST)

	split_sentence_result = result[split_sentence]
	word_count_result = result[word_count]

	assert len(split_sentence_result) == 3
	assert len(word_count_result) == 3

	assert split_sentence_result == [['Madam,'], ["I'm"], ['Adam.']]
	assert word_count_result == [['Madam,', 1], ["I'm", 1], ['Adam.', 1]]
