"""Test cases for stability checking."""

import pytest

from pyhrtc.basics import STABILITY, Instance, Matching, Agent, Couple

def test_stable_no_couples():
    def mk_agent(ident, prefs):
        a = Agent(ident)
        a.preferences = prefs
        return a
    left = [
            mk_agent("1", [["a"], ["b"], ["c"]]),
            mk_agent("2", [["a"], ["b"], ["c"]]),
            mk_agent("3", [["a"], ["b"], ["c"]]),
    ]
    right = [
            mk_agent("a", [["1"], ["2"], ["3"]]),
            mk_agent("b", [["1"], ["2"], ["3"]]),
            mk_agent("c", [["1"], ["2"], ["3"]]),
    ]
    m = {
            "1": "a",
            "2": "b",
            "3": "c",
    }
    match = Matching(m)
    i = Instance()
    for l in left:
        i.add_agent_left(l)
    for r in right:
        i.add_agent_right(r)
    assert match.is_stable(i, stability_type=None)
    m2 = {
            "1": "c",
            "2": "b",
            "3": "a",
    }
    match2 = Matching(m2)
    assert not match2.is_stable(i, stability_type=None)


def test_stable_couples():
    def mk_agent(ident, prefs):
        a = Agent(ident)
        a.preferences = prefs
        return a
    def mk_pair(ident_a, ident_b, pref_str):
        a = Agent(ident_a)
        b = Agent(ident_b)
        c = Couple(a, b)
        c.read_preferences(pref_str)
        print(c)
        return c
    left = [
            mk_pair("1a", "1b", [[("a", "a")], [("a", "b")], [("b", "c")]]),
            mk_agent("2", [["a"], ["b"], ["c"]]),
            mk_agent("3", [["a"], ["b"], ["c"]]),
    ]
    right = [
            mk_agent("a", [["1a", "1b"], ["2"], ["3"]]),
            mk_agent("b", [["1b"], ["1a", "2"], ["3"]]),
            mk_agent("c", [["1a"], ["2"], ["1b", "3"]]),
    ]
    m = {
            "1": "a",
            "2": "b",
            "3": "c",
    }
    match = Matching(m)
    i = Instance()
    for l in left:
        i.add_agent_left(l)
    for r in right:
        i.add_agent_right(r)
    assert match.is_stable(i, stability_type=None)
    m2 = {
            "1": "c",
            "2": "b",
            "3": "a",
    }
    match2 = Matching(m2)
    assert not match2.is_stable(i, stability_type=None)
