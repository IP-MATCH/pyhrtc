"""Test functions relating to couples."""

from pyhrtc.fileio import read_hrtc


def test_make_couple():
    """Create a couple in an instance, ensure numbers change.
    """
    instance = read_hrtc("tests/testfiles/test1.instance")
    assert instance.number_of_single_agents_left() == 2
    assert instance.number_of_couples_left() == 0
    assert instance.number_of_single_agents_right() == 2
    instance.make_couple_from_agent_pair_on_left()
    assert instance.number_of_single_agents_left() == 0
    assert instance.number_of_couples_left() == 1
    assert instance.number_of_single_agents_right() == 2
