#!/usr/bin/env python3
"""Generates instances of HRTC.
"""


import sys

from pyhrtc.generator import random_hrtc


def main(args):
    """ Generates an instance of HRTC according to the supplied parameters
    """
    instance = random_hrtc(
    instance.make_couple_from_doctor_pair(int(args[3]))
    instance.write_to_file(args[2])


if __name__ == "__main__":
    main(sys.argv)
