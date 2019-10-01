"""Test the thresholding functions."""

from nose.tools import eq_, raises

from pyhrtc.fileio import read_hrtc
from pyhrtc.algorithms import max_card_matching


def test_max_card_matching():
    """Test that max_card_matching changes
    """
    instance = read_hrtc("tests/testfiles/smti-grp-simple.instance")
    eq_(max_card_matching(instance), 3)
    instance.threshold(50)
    eq_(max_card_matching(instance), 2)


def test_threshold_above_kept():
    """Ensure that scores above are not removed."""
    instance = read_hrtc("tests/testfiles/smti-grp-simple.instance")
    eq_(instance.single_agent_left("1").weight_of("1"), 48)
    eq_(instance.single_agent_right("2").weight_of("3"), 55)
    instance.threshold(50)
    eq_(instance.single_agent_right("2").weight_of("3"), 55)


def test_empty_preferences():
    """Ensure that nothing breaks if we remove all preferences of an agent.
    """
    instance = read_hrtc("tests/testfiles/smti-grp-simple.instance")
    eq_(instance.number_of_single_agents_right(), 3)
    eq_(instance.single_agent_right("2").num_preferences, 3)
    instance.threshold(50)
    eq_(instance.number_of_single_agents_right(), 3)
    eq_(instance.single_agent_right("2").num_preferences, 1)
    instance.threshold(60)
    eq_(instance.number_of_single_agents_right(), 2)


@raises(Exception)
def test_threshold_below_removed():
    """Ensure that scores below the threshold are removed."""
    instance = read_hrtc("tests/testfiles/smti-grp-simple.instance")
    eq_(instance.single_agent_left("1").weight_of("1"), 48)
    instance.threshold(50)
    eq_(instance.single_agent_left("1").weight_of("1"), 48)
