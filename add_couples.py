#!/usr/bin/env python3
"""Read in an instance of HRT (no couples) and pair up some single doctors into
couples.
"""


import sys

from pyhrtc.instance import read_hrtc

def usage(script_name):
    """Prints usage info."""
    sys.stderr.write("Usage: %s <infile> <outfile> <num_couples_to_add>\n" % script_name)
    sys.exit(-1)


def main(args):
    """Read the instance and turn single residents into couples.
    """
    if len(args) != 4:
        usage(args[0])
    instance = read_hrtc(args[1])
    instance.make_couple_from_doctor_pair(int(args[3]))
    instance.write_to_file(args[2])


if __name__ == "__main__":
    main(sys.argv)
