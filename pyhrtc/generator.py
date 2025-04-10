"""Different ways of generating a random instance of HRTC."""

import random

from pyhrtc.basics import Agent, Couple, Instance

SCORE_MU = 80
SCORE_SIGMA = 5


def make_master_list(options, rounding=None):
    """Given a set of options, make a master list from the set. This will be
    done by assigning scores to each of the options, using the rounding
    function (if supplied) to round the scores, and finally sorting the options
    based on this score.
    """
    scores = {}
    for option in options:
        score = random.normalvariate(SCORE_MU, SCORE_SIGMA)
        if rounding:
            score = rounding(score)
        scores[option] = score
    return sorted(options, key=lambda x: scores[x])


def gen_capacities(total, hospitals, even_posts):
    """Generate capacities for a number of hospitals
    :param int hospitals: The number of hospitals
    :param int total: The number of posts to generate
    :param bool even_posts: are the posts distributed evenly (True) or randomly
                            (False)

    :return: the capacities of hospitals as a list
    :rtype: List
    """
    if even_posts:
        share = int(total / hospitals)
        excess = total - share * hospitals
        capacities = [share] * hospitals
        for hosp in range(excess):
            capacities[hosp] += 1
    else:
        capacities = [1] * hospitals
        for _ in range(total - hospitals):
            capacities[random.randrange(hospitals)] += 1
    return capacities


def random_hrtc(
    number_of_hospitals,
    number_of_single_residents,
    number_of_couples=0,
    resident_pref_length=None,
    hospital_pref_length=None,
    capacity=None,
    even_posts=False,
    resident_tie_density=0,
    hospital_tie_density=0,
    master_list=False,
    start_at_one=False,
):
    """Generates a random instance of HRTC, with the given properties.
    Note that couples are generated by interleaving two single residents.

    :param int number_of_hospitals: the number of hospitals
    :param int number_of_single_residents: the number of single residents
    :param int number_of_couples: the number of couples
    :param int resident_pref_length: how many preferences does each resident
                                     have
    :param int hospital_pref_length: how many preferences does each hospital
                                     have
    :param float resident_tie_density: the tie density of the residents
    :param float hospital_tie_density: the tie density of the hospitals
    :param bool master_list: are hospital preferences decided by a master list?
    :param int capacity: how many posts in total are there
    :param bool even_posts: are the posts distributed evenly (True) or randomly
    (False) :param bool start_at_one: do agent IDs have to start at 1. Needed
    for some solvers.

    """
    if resident_pref_length and hospital_pref_length:
        # I don't have a good way of doing this.
        raise NotImplementedError
    if not capacity:
        capacity = number_of_single_residents + 2 * number_of_couples
    capacities = gen_capacities(capacity, number_of_hospitals, even_posts)
    # Generate all the hospitals and agents
    hospitals = {
        ident + start_at_one: Agent(ident + start_at_one, capacities[ident])
        for ident in range(number_of_hospitals)
    }
    single_residents = {
        ident + start_at_one: Agent(ident + start_at_one)
        for ident in range(number_of_single_residents)
    }
    couple_doctors = {}
    for ident in range(number_of_couples):
        offset = number_of_single_residents + 2 * ident + start_at_one
        couple_doctors[2 * ident + start_at_one] = Agent(offset)
        couple_doctors[2 * ident + 1 + start_at_one] = Agent(offset + 1)
    # Generate a master list
    if master_list:
        master_list = [doctor.ident for doctor in single_residents.values()]
        master_list.extend(doctor.ident for doctor in couple_doctors.values())
        master_list = make_master_list(master_list)
    if not hospital_pref_length:
        for doctor in single_residents.values():
            doctor.make_random_preferences(
                hospitals.keys(),
                length=resident_pref_length,
                tie_density=resident_tie_density,
            )
        for doctor in couple_doctors.values():
            doctor.make_random_preferences(
                hospitals.keys(),
                length=resident_pref_length,
                tie_density=resident_tie_density,
            )
        for hospital in hospitals.values():
            options = [
                doctor.ident
                for doctor in single_residents.values()
                if doctor.is_acceptable(hospital.ident)
            ]
            options.extend(
                [
                    doctor.ident
                    for doctor in couple_doctors.values()
                    if doctor.is_acceptable(hospital.ident)
                ]
            )
            if master_list:
                hospital.make_master_list_preferences(options, master_list)
            else:
                hospital.make_random_preferences(
                    options, tie_density=hospital_tie_density
                )
    else:
        # Hospital preference list lengths are not implemented
        raise NotImplementedError
    couples = {}
    for ident in range(number_of_couples):
        offset = 2 * ident + start_at_one
        couple = Couple.from_two_doctors(
            couple_doctors[offset], couple_doctors[offset + 1]
        )
        couples[couple.ident] = couple
    instance = Instance(
        single_agents_left=single_residents,
        couples_left=couples,
        single_agents_right=hospitals,
    )
    return instance
