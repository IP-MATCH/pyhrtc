"""Test cases for reading files."""


from nose.tools import eq_

from pyhrtc.instance import read_hrtc

def test_reads():
    """Read in test1.instance and test2.instance and check some parameters.
    """
    instance = read_hrtc("tests/testfiles/test1.instance")
    eq_(instance.get_number_of_single_residents(), 2)
    eq_(instance.get_number_of_couples(), 0)
    eq_(instance.get_number_of_hospitals(), 2)

    instance = read_hrtc("tests/testfiles/test2.instance")
    eq_(instance.get_number_of_single_residents(), 2)
    eq_(instance.get_number_of_couples(), 2)
    eq_(instance.get_number_of_hospitals(), 2)
