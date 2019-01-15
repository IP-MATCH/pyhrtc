"""Test cases for reading files."""


from nose.tools import eq_

from pyhrtc.fileio import read_hrtc

def test_reads():
    """Read in test1.instance and test2.instance and check some parameters.
    """
    instance = read_hrtc("tests/testfiles/test1.instance")
    eq_(instance.number_of_single_agents_left(), 2)
    eq_(instance.number_of_couples_left(), 0)
    eq_(instance.number_of_single_agents_right(), 2)

    instance = read_hrtc("tests/testfiles/test2.instance")
    eq_(instance.number_of_single_agents_left(), 2)
    eq_(instance.number_of_couples_left(), 2)
    eq_(instance.number_of_single_agents_right(), 2)
