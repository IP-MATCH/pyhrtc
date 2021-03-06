"""Test cases for maximum size matching algorithms."""


from nose.tools import eq_, raises

from pyhrtc.fileio import read_hrtc
from pyhrtc.algorithms import max_card_matching, max_weight_matching


def test_max_card_matching_simple():
    """test1 is a simple instance of SMTI.
    """
    instance = read_hrtc("tests/testfiles/test1.instance")
    eq_(max_card_matching(instance), 2)


def test_max_card_matching_smti():
    """This is a much larger SMTI instance.
    """
    instance = read_hrtc("tests/testfiles/smti.instance")
    eq_(max_card_matching(instance), 9941)


def test_max_card_matching_hrt():
    """An instance with capacities.
    """
    instance = read_hrtc("tests/testfiles/hrt.instance")
    eq_(max_card_matching(instance), 759)


@raises(Exception)
def test_max_card_matching_hrct():
    """An instance with couples. Note that this isn't implemented.
    """
    instance = read_hrtc("tests/testfiles/test2.instance")
    eq_(max_card_matching(instance), -1)

def test_max_card_matching_smti_grp():
    """This is a simple instance of SMTI-GRP.
    """
    instance = read_hrtc("tests/testfiles/smti-grp-simple.instance")
    eq_(max_card_matching(instance), 3)


def test_max_weight_matching():
    """A simple SMTI-GRP instance.
    """
    instance = read_hrtc("tests/testfiles/smti-grp-simple.instance")
    eq_(max_weight_matching(instance), 200)
    instance.threshold(30)
    eq_(max_weight_matching(instance), 197)
    instance.threshold(50)
    eq_(max_weight_matching(instance), 177)
