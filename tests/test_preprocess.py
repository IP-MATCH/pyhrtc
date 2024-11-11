"""Test cases for preprocessing."""


from pyhrtc.fileio import read_hrtc


def test_trims():
    """Test the trimming of preference lists
    """
    instance = read_hrtc("tests/testfiles/test1.instance")
    assert instance.number_of_single_agents_left() == 2
    assert instance.number_of_couples_left() == 0
    assert instance.number_of_single_agents_right() == 2
    one = instance.single_agent_left("1")
    assert len(list(one.acceptable_agents())) == 2
    one.trim_after_worst(["1"])
    assert len(list(one.acceptable_agents())) == 1


def test_preprocess():
    """Test that preprocessing works as expected.
    """
    instance = read_hrtc("tests/testfiles/test1.instance")
    assert instance.number_of_single_agents_left() == 2
    assert instance.number_of_couples_left() == 0
    assert instance.number_of_single_agents_right() == 2
    one = instance.single_agent_left("1")
    assert len(list(one.acceptable_agents())) == 2
    count = instance.preprocess()
    assert len(list(one.acceptable_agents())) == 1
    assert count == 2
    assert len(list(instance.single_agent_left("2").acceptable_agents())) == 1
    assert len(list(instance.single_agent_right("1").acceptable_agents())) == 2
    assert len(list(instance.single_agent_right("2").acceptable_agents())) == 0
