"""Test the thresholding functions."""

import pytest

from pyhrtc.fileio import read_hrtc
from pyhrtc.algorithms import max_card_matching


def test_max_card_matching():
    """Test that max_card_matching changes
    """
    instance = read_hrtc("tests/testfiles/smti-grp-simple.instance")
    assert max_card_matching(instance) == 3
    instance.threshold(50)
    assert max_card_matching(instance) == 2


def test_threshold_above_kept():
    """Ensure that scores above are not removed."""
    instance = read_hrtc("tests/testfiles/smti-grp-simple.instance")
    assert instance.single_agent_left("1").weight_of("1") == 48
    assert instance.single_agent_right("2").weight_of("3") == 55
    instance.threshold(50)
    assert instance.single_agent_right("2").weight_of("3") == 55


def test_empty_preferences():
    """Ensure that nothing breaks if we remove all preferences of an agent.
    """
    instance = read_hrtc("tests/testfiles/smti-grp-simple.instance")
    assert instance.number_of_single_agents_right() == 3
    assert instance.single_agent_right("2").num_preferences == 3
    instance.threshold(50)
    assert instance.number_of_single_agents_right() == 3
    assert instance.single_agent_right("2").num_preferences == 1
    instance.threshold(60)
    assert instance.number_of_single_agents_right() == 2


def test_threshold_below_removed():
    """Ensure that scores below the threshold are removed."""
    instance = read_hrtc("tests/testfiles/smti-grp-simple.instance")
    assert instance.single_agent_left("1").weight_of("1") == 48
    instance.threshold(50)
    with pytest.raises(Exception):
        assert instance.single_agent_left("1").weight_of("1") == 48
