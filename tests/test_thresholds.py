"""Test the thresholding functions."""

from nose.tools import eq_, raises

from pyhrtc.fileio import read_hrtc
from pyhrtc.algorithms import max_card_matching

def test_max_card_matching_():
    """This is a simple instance of SMTI-GRP.
    """
    instance = read_hrtc("tests/testfiles/smti-grp-simple.instance")
    eq_(max_card_matching(instance), 3)
    instance.threshold(50)
    eq_(max_card_matching(instance), 2)
