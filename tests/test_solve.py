"""Test cases for solving SMTI instances."""


from nose.tools import eq_

from pyhrtc.fileio import read_hrtc
from pyhrtc.models import MAX_SMTI_IP

def test_solve():
    """Solve simple instance
    """
    instance = read_hrtc("tests/testfiles/smti-simple.instance")
    model = MAX_SMTI_IP(instance)
    matching = model.solve()
    eq_(len(matching), 3)
    instance = read_hrtc("tests/testfiles/smti-nocomplete.instance")
    model = MAX_SMTI_IP(instance)
    matching = model.solve()
    eq_(len(matching), 2)
