#!/usr/bin/env python3
"""Print the density of each file given on the command line."""


import sys

from pyhrtc.instance import read_hrtc


def main(files):
    for filename in files:
        instance = read_hrtc(filename)
        doc_tie, hosp_tie = instance.tie_density()
        print("%s: %f %f" % (filename, doc_tie, hosp_tie))


if __name__ == "__main__":
    main(sys.argv[1:])

