"""Test cases for stability checking."""

import logging

logger = logging.getLogger(__name__)

from pyhrtc.basics import STABILITY, Instance, Matching, Agent, Couple, PreferencePair


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
    m = [
        ("1", "a"),
        ("2", "b"),
        ("3", "c"),
    ]
    i = Instance()
    match = Matching(i, m)
    for l in left:
        i.add_agent_left(l)
    for r in right:
        i.add_agent_right(r)
    for left in i.left_agents():
        print(left)
    assert match.is_stable(stability_type=None)
    m2 = [
        ("1", "c"),
        ("2", "b"),
        ("3", "a"),
    ]
    match2 = Matching(i, m2)
    assert not match2.is_stable(stability_type=None)


def test_stable_couples():
    def mk_agent(ident, prefs, capacity=1):
        a = Agent(ident, capacity=capacity)
        a.preferences = prefs
        return a

    def mk_pair(ident_a, ident_b, prefs):
        a = Agent(ident_a)
        b = Agent(ident_b)
        c = Couple(a, b)
        c.preferences = prefs
        logger.debug(c)
        return c

    left = [
        mk_pair("1a", "1b", [["a,a"], ["a,b"], ["b,c"]]),
        mk_agent("2", [["a"], ["b"], ["c"]]),
        mk_agent("3", [["a"], ["b"], ["c"]]),
    ]
    right = [
        mk_agent("a", [["1a", "1b"], ["2"], ["3"]], capacity=2),
        mk_agent("b", [["1b"], ["1a", "2"], ["3"]]),
        mk_agent("c", [["1a"], ["2"], ["1b", "3"]]),
    ]
    m = [
        ("1a", "a"),
        ("1b", "a"),
        ("2", "b"),
        ("3", "c"),
    ]
    i = Instance()
    for l in left:
        i.add_agent_left(l)
    for r in right:
        i.add_agent_right(r)
    match = Matching(i, m)
    assert match.is_stable(stability_type=STABILITY.KPR)
    m2 = {
        ("1a", "a"),
        ("1b", "b"),
        ("2", "a"),
        ("3", "c"),
    }
    match2 = Matching(i, m2)
    assert not match2.is_stable(stability_type=STABILITY.KPR)


def test_stable_from_paper_table2_row1():
    def mk_agent(ident, prefs, capacity=1):
        a = Agent(ident, capacity=capacity)
        a.preferences = prefs
        return a

    def mk_pair(ident_a, ident_b, prefs):
        a = Agent(ident_a)
        b = Agent(ident_b)
        c = Couple(a, b)
        c.preferences = prefs
        logger.debug(c)
        return c

    left = [
        mk_pair("A", "a", [["h1,h1"], ["h1,N"], ["N,h1"]]),
        mk_agent("B", [["h1"]]),
    ]
    right = [
        mk_agent("h1", [["A"], ["a"], ["B"]], capacity=2),
        mk_agent("N", [["A", "a", "B"]], capacity=3),
    ]
    i = Instance()
    for l in left:
        i.add_agent_left(l)
    for r in right:
        i.add_agent_right(r)
    m = [
        ("A", "h1"),
        ("a", "h1"),
    ]
    match = Matching(i, m)
    assert match.is_stable(stability_type=STABILITY.KPR)
    assert match.is_stable(stability_type=STABILITY.BIS)
    assert match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("A", "h1"),
        ("B", "h1"),
    ]
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("a", "h1"),
        ("B", "h1"),
    ]
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("B", "h1"),
    ]
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("A", "h1"),
    ]
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("a", "h1"),
    ]
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)
    m = []
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)


def test_stable_from_paper_table2_row1_unsplit():
    def mk_agent(ident, prefs, capacity=1):
        a = Agent(ident, capacity=capacity)
        a.preferences = prefs
        return a

    def mk_pair(ident_a, ident_b, prefs):
        a = Agent(ident_a)
        b = Agent(ident_b)
        c = Couple(a, b)
        c.preferences = prefs
        logger.debug(c)
        return c

    left = [
        mk_pair("A", "a", [["h1,h1"], ["N,N"]]),
        mk_agent("B", [["h1"]]),
    ]
    right = [
        mk_agent("h1", [["A"], ["a"], ["B"]], capacity=2),
        mk_agent("N", [["A", "a", "B"]], capacity=3),
    ]
    i = Instance()
    for l in left:
        i.add_agent_left(l)
    for r in right:
        i.add_agent_right(r)
    m = [
        ("A", "h1"),
        ("a", "h1"),
    ]
    match = Matching(i, m)
    assert match.is_stable(stability_type=STABILITY.KPR)
    assert match.is_stable(stability_type=STABILITY.BIS)
    assert match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("B", "h1"),
    ]
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)
    m = []
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)


def test_stable_from_paper_table2_row2():
    def mk_agent(ident, prefs, capacity=1):
        a = Agent(ident, capacity=capacity)
        a.preferences = prefs
        return a

    def mk_pair(ident_a, ident_b, prefs):
        a = Agent(ident_a)
        b = Agent(ident_b)
        c = Couple(a, b)
        c.preferences = prefs
        logger.debug(c)
        return c

    left = [
        mk_pair("A", "a", [["h1,h1"], ["h1,N", "N,h1"], ["N,N"]]),
        mk_agent("B", [["h1"]]),
    ]
    right = [
        mk_agent("h1", [["A"], ["B"], ["a"]], capacity=2),
        mk_agent("N", [["A", "a", "B"]], capacity=3),
    ]
    i = Instance()
    for l in left:
        i.add_agent_left(l)
    for r in right:
        i.add_agent_right(r)
    m = [
        ("A", "h1"),
        ("a", "h1"),
    ]
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("A", "h1"),
        ("B", "h1"),
        ("a", "N"),
    ]
    match = Matching(i, m)
    assert match.is_stable(stability_type=STABILITY.KPR), f"{m} not stable under KPR"
    assert match.is_stable(stability_type=STABILITY.BIS)
    assert match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("a", "h1"),
        ("B", "h1"),
        ("A", "N"),
    ]
    match = Matching(i, m)
    assert match.is_stable(stability_type=STABILITY.KPR), f"{m} isn't stable under KPR"
    assert match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("B", "h1"),
        ("A", "N"),
        ("a", "N"),
    ]
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("A", "h1"),
        ("a", "N"),
    ]
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("a", "h1"),
        ("A", "N"),
    ]
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("A", "N"),
        ("a", "N"),
    ]
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)


def test_stable_from_paper_table2_row2_unsplit():
    def mk_agent(ident, prefs, capacity=1):
        a = Agent(ident, capacity=capacity)
        a.preferences = prefs
        return a

    def mk_pair(ident_a, ident_b, prefs):
        a = Agent(ident_a)
        b = Agent(ident_b)
        c = Couple(a, b)
        c.preferences = prefs
        logger.debug(c)
        return c

    left = [
        mk_pair("A", "a", [["h1,h1"]]),
        mk_agent("B", [["h1"]]),
    ]
    right = [
        mk_agent("h1", [["A"], ["B"], ["a"]], capacity=2),
        mk_agent("N", [["A", "a", "B"]], capacity=3),
    ]
    i = Instance()
    for l in left:
        i.add_agent_left(l)
    for r in right:
        i.add_agent_right(r)
    m = [
        ("A", "h1"),
        ("a", "h1"),
    ]
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("B", "h1"),
    ]
    match = Matching(i, m)
    assert match.is_stable(stability_type=STABILITY.KPR)
    assert match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)
    m = []
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)


def test_stable_from_paper_table2_row3():
    def mk_agent(ident, prefs, capacity=1):
        a = Agent(ident, capacity=capacity)
        a.preferences = prefs
        return a

    def mk_pair(ident_a, ident_b, prefs):
        a = Agent(ident_a)
        b = Agent(ident_b)
        c = Couple(a, b)
        c.preferences = prefs
        logger.debug(c)
        return c

    left = [
        mk_pair("A", "a", [["h1,h1"], ["h1,N", "N,h1"], ["N,N"]]),
        mk_agent("B", [["h1"]]),
    ]
    right = [
        mk_agent("h1", [["B"], ["A"], ["a"]], capacity=2),
        mk_agent("N", [["A", "a", "B"]], capacity=3),
    ]
    i = Instance()
    for l in left:
        i.add_agent_left(l)
    for r in right:
        i.add_agent_right(r)
    m = [
        ("A", "h1"),
        ("a", "h1"),
    ]
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("A", "h1"),
        ("B", "h1"),
        ("a", "N"),
    ]
    match = Matching(i, m)
    assert match.is_stable(stability_type=STABILITY.KPR), f"{m} not stable under KPR"
    assert match.is_stable(stability_type=STABILITY.BIS)
    assert match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("a", "h1"),
        ("B", "h1"),
        ("A", "N"),
    ]
    match = Matching(i, m)
    assert match.is_stable(stability_type=STABILITY.KPR), f"{m} isn't stable under KPR"
    assert match.is_stable(stability_type=STABILITY.BIS)
    assert match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("B", "h1"),
        ("A", "N"),
        ("a", "N"),
    ]
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("A", "h1"),
        ("a", "N"),
    ]
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("a", "h1"),
        ("A", "N"),
    ]
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("A", "N"),
        ("a", "N"),
    ]
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)


def test_stable_from_paper_table2_row3_unsplit():
    def mk_agent(ident, prefs, capacity=1):
        a = Agent(ident, capacity=capacity)
        a.preferences = prefs
        return a

    def mk_pair(ident_a, ident_b, prefs):
        a = Agent(ident_a)
        b = Agent(ident_b)
        c = Couple(a, b)
        c.preferences = prefs
        logger.debug(c)
        return c

    left = [
        mk_pair("A", "a", [["h1,h1"]]),
        mk_agent("B", [["h1"]]),
    ]
    right = [
        mk_agent("h1", [["B"], ["A"], ["a"]], capacity=2),
        mk_agent("N", [["B", "A", "a"]], capacity=3),
    ]
    i = Instance()
    for l in left:
        i.add_agent_left(l)
    for r in right:
        i.add_agent_right(r)
    m = [
        ("A", "h1"),
        ("a", "h1"),
    ]
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("B", "h1"),
    ]
    match = Matching(i, m)
    assert match.is_stable(stability_type=STABILITY.KPR)
    assert match.is_stable(stability_type=STABILITY.BIS)
    assert match.is_stable(stability_type=STABILITY.MM)
    m = []
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)


def test_stable_from_paper_table2_row4():
    def mk_agent(ident, prefs, capacity=1):
        a = Agent(ident, capacity=capacity)
        a.preferences = prefs
        return a

    def mk_pair(ident_a, ident_b, prefs):
        a = Agent(ident_a)
        b = Agent(ident_b)
        c = Couple(a, b)
        c.preferences = prefs
        logger.debug(c)
        return c

    left = [
        mk_pair("A", "a", [["h1,h1"], ["h1,N", "N,h1"], ["N,N"]]),
        mk_agent("B", [["h1"]]),
    ]
    right = [
        mk_agent("h1", [["A", "a", "B"]], capacity=2),
        mk_agent("N", [["A", "a", "B"]], capacity=3),
    ]
    i = Instance()
    for l in left:
        i.add_agent_left(l)
    for r in right:
        i.add_agent_right(r)
    m = [
        ("A", "h1"),
        ("a", "h1"),
    ]
    match = Matching(i, m)
    assert match.is_stable(stability_type=STABILITY.KPR)
    assert match.is_stable(stability_type=STABILITY.BIS)
    assert match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("A", "h1"),
        ("B", "h1"),
        ("a", "N"),
    ]
    match = Matching(i, m)
    assert match.is_stable(stability_type=STABILITY.KPR), f"{m} not stable under KPR"
    assert match.is_stable(stability_type=STABILITY.BIS)
    assert match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("a", "h1"),
        ("B", "h1"),
        ("A", "N"),
    ]
    match = Matching(i, m)
    assert match.is_stable(stability_type=STABILITY.KPR), f"{m} isn't stable under KPR"
    assert match.is_stable(stability_type=STABILITY.BIS)
    assert match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("B", "h1"),
        ("A", "N"),
        ("a", "N"),
    ]
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("A", "h1"),
        ("a", "N"),
    ]
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("a", "h1"),
        ("A", "N"),
    ]
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("A", "N"),
        ("a", "N"),
    ]
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)


def test_stable_from_paper_table2_row4_unsplit():
    def mk_agent(ident, prefs, capacity=1):
        a = Agent(ident, capacity=capacity)
        a.preferences = prefs
        return a

    def mk_pair(ident_a, ident_b, prefs):
        a = Agent(ident_a)
        b = Agent(ident_b)
        c = Couple(a, b)
        c.preferences = prefs
        logger.debug(c)
        return c

    left = [
        mk_pair("A", "a", [["h1,h1"]]),
        mk_agent("B", [["h1"]]),
    ]
    right = [
        mk_agent("h1", [["A", "a", "B"]], capacity=2),
        mk_agent("N", [["B", "A", "a"]], capacity=3),
    ]
    i = Instance()
    for l in left:
        i.add_agent_left(l)
    for r in right:
        i.add_agent_right(r)
    m = [
        ("A", "h1"),
        ("a", "h1"),
    ]
    match = Matching(i, m)
    assert match.is_stable(stability_type=STABILITY.KPR)
    assert match.is_stable(stability_type=STABILITY.BIS)
    assert match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("B", "h1"),
    ]
    match = Matching(i, m)
    assert match.is_stable(stability_type=STABILITY.KPR)
    assert match.is_stable(stability_type=STABILITY.BIS)
    assert match.is_stable(stability_type=STABILITY.MM)
    m = []
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)


def test_stable_from_paper_table2_row5():
    def mk_agent(ident, prefs, capacity=1):
        a = Agent(ident, capacity=capacity)
        a.preferences = prefs
        return a

    def mk_pair(ident_a, ident_b, prefs):
        a = Agent(ident_a)
        b = Agent(ident_b)
        c = Couple(a, b)
        c.preferences = prefs
        logger.debug(c)
        return c

    left = [
        mk_pair("A", "a", [["h1,h1"], ["h1,N", "N,h1"], ["N,N"]]),
        mk_agent("B", [["h1"]]),
    ]
    right = [
        mk_agent("h1", [["A"], ["a", "B"]], capacity=2),
        mk_agent("N", [["A", "a", "B"]], capacity=3),
    ]
    i = Instance()
    for l in left:
        i.add_agent_left(l)
    for r in right:
        i.add_agent_right(r)
    m = [
        ("A", "h1"),
        ("a", "h1"),
    ]
    match = Matching(i, m)
    assert match.is_stable(stability_type=STABILITY.KPR)
    assert match.is_stable(stability_type=STABILITY.BIS)
    assert match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("A", "h1"),
        ("B", "h1"),
        ("a", "N"),
    ]
    match = Matching(i, m)
    assert match.is_stable(stability_type=STABILITY.KPR), f"{m} not stable under KPR"
    assert match.is_stable(stability_type=STABILITY.BIS)
    assert match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("a", "h1"),
        ("B", "h1"),
        ("A", "N"),
    ]
    match = Matching(i, m)
    assert match.is_stable(stability_type=STABILITY.KPR), f"{m} isn't stable under KPR"
    assert match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("B", "h1"),
        ("A", "N"),
        ("a", "N"),
    ]
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("A", "h1"),
        ("a", "N"),
    ]
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("a", "h1"),
        ("A", "N"),
    ]
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("A", "N"),
        ("a", "N"),
    ]
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)


def test_stable_from_paper_table2_row5_unsplit():
    def mk_agent(ident, prefs, capacity=1):
        a = Agent(ident, capacity=capacity)
        a.preferences = prefs
        return a

    def mk_pair(ident_a, ident_b, prefs):
        a = Agent(ident_a)
        b = Agent(ident_b)
        c = Couple(a, b)
        c.preferences = prefs
        logger.debug(c)
        return c

    left = [
        mk_pair("A", "a", [["h1,h1"]]),
        mk_agent("B", [["h1"]]),
    ]
    right = [
        mk_agent("h1", [["A"], ["a", "B"]], capacity=2),
        mk_agent("N", [["B", "A", "a"]], capacity=3),
    ]
    i = Instance()
    for l in left:
        i.add_agent_left(l)
    for r in right:
        i.add_agent_right(r)
    m = [
        ("A", "h1"),
        ("a", "h1"),
    ]
    match = Matching(i, m)
    assert match.is_stable(stability_type=STABILITY.KPR)
    assert match.is_stable(stability_type=STABILITY.BIS)
    assert match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("B", "h1"),
    ]
    match = Matching(i, m)
    assert match.is_stable(stability_type=STABILITY.KPR)
    assert match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)
    m = []
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)


def test_stable_from_paper_table2_row6():
    def mk_agent(ident, prefs, capacity=1):
        a = Agent(ident, capacity=capacity)
        a.preferences = prefs
        return a

    def mk_pair(ident_a, ident_b, prefs):
        a = Agent(ident_a)
        b = Agent(ident_b)
        c = Couple(a, b)
        c.preferences = prefs
        logger.debug(c)
        return c

    left = [
        mk_pair("A", "a", [["h1,h1"], ["h1,N", "N,h1"], ["N,N"]]),
        mk_agent("B", [["h1"]]),
    ]
    right = [
        mk_agent("h1", [["A", "B"], ["a"]], capacity=2),
        mk_agent("N", [["A", "a", "B"]], capacity=3),
    ]
    i = Instance()
    for l in left:
        i.add_agent_left(l)
    for r in right:
        i.add_agent_right(r)
    m = [
        ("A", "h1"),
        ("a", "h1"),
    ]
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("A", "h1"),
        ("B", "h1"),
        ("a", "N"),
    ]
    match = Matching(i, m)
    assert match.is_stable(stability_type=STABILITY.KPR), f"{m} not stable under KPR"
    assert match.is_stable(stability_type=STABILITY.BIS)
    assert match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("a", "h1"),
        ("B", "h1"),
        ("A", "N"),
    ]
    match = Matching(i, m)
    assert match.is_stable(stability_type=STABILITY.KPR), f"{m} isn't stable under KPR"
    assert match.is_stable(stability_type=STABILITY.BIS)
    assert match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("B", "h1"),
        ("A", "N"),
        ("a", "N"),
    ]
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("A", "h1"),
        ("a", "N"),
    ]
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("a", "h1"),
        ("A", "N"),
    ]
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("A", "N"),
        ("a", "N"),
    ]
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)


def test_stable_from_paper_table2_row6_unsplit():
    def mk_agent(ident, prefs, capacity=1):
        a = Agent(ident, capacity=capacity)
        a.preferences = prefs
        return a

    def mk_pair(ident_a, ident_b, prefs):
        a = Agent(ident_a)
        b = Agent(ident_b)
        c = Couple(a, b)
        c.preferences = prefs
        logger.debug(c)
        return c

    left = [
        mk_pair("A", "a", [["h1,h1"]]),
        mk_agent("B", [["h1"]]),
    ]
    right = [
        mk_agent("h1", [["A", "B"], ["a"]], capacity=2),
        mk_agent("N", [["B", "A", "a"]], capacity=3),
    ]
    i = Instance()
    for l in left:
        i.add_agent_left(l)
    for r in right:
        i.add_agent_right(r)
    m = [
        ("A", "h1"),
        ("a", "h1"),
    ]
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)
    m = [
        ("B", "h1"),
    ]
    match = Matching(i, m)
    assert match.is_stable(stability_type=STABILITY.KPR)
    assert match.is_stable(stability_type=STABILITY.BIS)
    assert match.is_stable(stability_type=STABILITY.MM)
    m = []
    match = Matching(i, m)
    assert not match.is_stable(stability_type=STABILITY.KPR)
    assert not match.is_stable(stability_type=STABILITY.BIS)
    assert not match.is_stable(stability_type=STABILITY.MM)
