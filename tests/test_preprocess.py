"""Test cases for reading files."""


from nose.tools import eq_

from pyhrtc.fileio import read_hrtc


def test_trims():
    """Test the trimming of preference lists
    """
    instance = read_hrtc("tests/testfiles/test1.instance")
    eq_(instance.number_of_single_agents_left(), 2)
    eq_(instance.number_of_couples_left(), 0)
    eq_(instance.number_of_single_agents_right(), 2)
    one = instance.single_agent_left(1)
    eq_(len(one.acceptable_agents()), 2)
    one.trim_after_worst([1])
    eq_(len(one.acceptable_agents()), 1)


def test_preprocess():
    instance = read_hrtc("tests/testfiles/test1.instance")
    eq_(instance.number_of_single_agents_left(), 2)
    eq_(instance.number_of_couples_left(), 0)
    eq_(instance.number_of_single_agents_right(), 2)
    one = instance.single_agent_left(1)
    eq_(len(one.acceptable_agents()), 2)
    count = instance.preprocess()
    eq_(len(one.acceptable_agents()), 1)
    eq_(count, 2)
    eq_(len(instance.single_agent_left(2).acceptable_agents()), 1)
    eq_(len(instance.single_agent_right(1).acceptable_agents()), 2)
    eq_(len(instance.single_agent_right(2).acceptable_agents()), 0)
