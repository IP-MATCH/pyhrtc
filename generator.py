#!/usr/bin/env python3
"""Generates instances of HRTC.
"""


from argparse import ArgumentParser

from pyhrtc.generator import random_hrtc


def main():
    """ Generates an instance of HRTC according to the supplied parameters
    """
    parser = ArgumentParser(description="Generate an instance of HRTC")
    # -h is for help, so use -p for programmes
    parser.add_argument("--programmes", "-p", type=int, required=True,
                        metavar='P',
                        help="Number of programmes (hospitals)")
    parser.add_argument("--residents", "-r", type=int, required=True,
                        metavar='R',
                        help="Number of (single) residents")
    parser.add_argument("--couples", "-c", type=int, required=True,
                        metavar='C',
                        help="Number of couples")
    parser.add_argument("--master", "-m", required=False,
                        action='store_true',
                        help="Do hospitals use a master list of scores to rank doctors")
    parser.add_argument("--output", "-o", type=str, required=True,
                        metavar='FILE',
                        help="Name of output file")
    options = parser.parse_args()
    instance = random_hrtc(number_of_hospitals=options.programmes,
                           number_of_single_residents=options.residents,
                           number_of_couples=options.couples,
                           master_list=options.master)
    instance.write_to_file(options.output)


if __name__ == "__main__":
    main()
