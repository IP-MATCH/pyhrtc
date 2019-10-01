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


def test_reads_smti_grp():
    """Test reading of SMTI-GRP instances."""
    # With column/row headers
    instance = read_hrtc("tests/testfiles/smti-grp-simple.instance")
    eq_(instance.number_of_single_agents_left(), 3)
    eq_(instance.single_agent_left("1").weight_of("1"), 48)
    eq_(instance.single_agent_right("2").weight_of("3"), 55)
    eq_(instance.number_of_single_agents_right(), 3)
    # Without the header row/column, but a header showing number of rows and
    # columns instead
    instance = read_hrtc("tests/testfiles/smti-grp-noheader.instance")
    eq_(instance.number_of_single_agents_left(), 3)
    eq_(instance.single_agent_left("1").weight_of("1"), 48)
    eq_(instance.single_agent_right("2").weight_of("3"), 55)
    eq_(instance.number_of_single_agents_right(), 3)
    # An unbalanced instance.
    instance = read_hrtc("tests/testfiles/smti-grp-noheader-unbal.instance")
    eq_(instance.number_of_single_agents_left(), 2)
    eq_(instance.single_agent_left("1").weight_of("1"), 48)
    eq_(instance.single_agent_right("3").weight_of("2"), 94)
    eq_(instance.number_of_single_agents_right(), 3)


def test_reads_iain():
    """Test reading of SMTI-GRP instances."""
    instance = read_hrtc("tests/testfiles/hrtc-iain-small.instance")
    eq_(instance.number_of_single_agents_left(), 6)
    eq_(instance.number_of_couples_left(), 2)
    eq_(instance.number_of_single_agents_right(), 5)
    instance = read_hrtc("tests/testfiles/hrtc-iain.instance")
    eq_(instance.number_of_single_agents_left(), 88)
    eq_(instance.number_of_couples_left(), 11)
    eq_(instance.number_of_single_agents_right(), 11)
