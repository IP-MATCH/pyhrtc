#!/usr/bin/env python3
"""Generates many instances of HRTC.
"""


from pyhrtc.generator import random_hrtc


def main():
    """ Generates an instance of HRTC according to the supplied parameters
    """
    for residents in range(5, 10000, 500):
        couples = int(residents/10)
        hospitals = int(residents/10)
        if hospitals < 3:
            hospitals = 3
        if hospitals < 10:
            max_pref_length = hospitals
        else:
            max_pref_length = 10
        for iteration in range(10):
            instance = random_hrtc(number_of_hospitals=hospitals,
                                   number_of_single_residents=residents,
                                   number_of_couples=couples,
                                   capacity=residents,
                                   resident_pref_length=max_pref_length,
                                   start_at_one=True)
            filename = "HRTC_r%d_h%d_c%d_p%d_i%d.instance" % (residents,
                                                              hospitals,
                                                              couples,
                                                              residents,
                                                              iteration)
            instance.write_to_file(filename)


if __name__ == "__main__":
    main()
