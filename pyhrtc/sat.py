"""Encode an instance of SMTI as SAT in CNF, potentially with weights.
"""


def create_sat_smti(instance):
    """Creates a CNF SAT encoding of an SMTI instance.
    :raises NotImplementedError: Raised if the instance is not an SMTI instance
    """
    if not instance.is_SMTI():
        raise NotImplementedError

    varmap = {}
    var_count = 1
    for agent in instance.single_residents:
        pref_length = 1
        for pref_group in agent.preferences:
            for pref in pref_group:
                varmap[("r", agent.id, pref_length)] = var_count
                var_count += 1
                pref_length += 1
        varmap[("r", agent.id, pref_length)] = var_count
        var_count += 1
    for agent in instance.single_residents:
        pref_length = 1
        for pref_group in agent.preferences:
            for pref in pref_group:
                varmap[("h", agent.id, pref_length)] = var_count
                var_count += 1
                pref_length += 1
        varmap[("h", agent.id, pref_length)] = var_count
        var_count += 1

    encoding = ""
    # Clause 1
    for resident in instance.single_residents:
        encoding += "%d 0" % varmap[("r", resident.id, 1)]
    # Clause 2
    for hospital in instance.hospitals:
        encoding += "%d 0" % varmap[("h", hospital.id, 1)]
    # Clause 3
    for resident in instance.single_residents:
        for pref in range(resident.num_preferences):
            encoding += "%d -%d 0" % (varmap[("r", resident.id, pref)],
                                      varmap[("r", resident.id, pref)]+1)
    # Clause 4
    for hospital in instance.single_hospitals:
        for pref in range(hospital.num_preferences):
            encoding += "%d -%d 0" % (varmap[("h", hospital.id, pref)],
                                      varmap[("h", hospital.id, pref)]+1)
    for hospital in instance.hospitals:
        for resident in instance.single_residents:
            # Clause 5
            # Note that position_of and rank_of are two different things.
            p = resident.position_of(hospital)
            q = hospital.position_of(resident)
            encoding += "-%d %d %d 0" % (varmap[("r", resident.id, p)],
                                         varmap[("r", resident.id, p)]+1,
                                         varmap[("h", hospital.id, q)])
            encoding += "-%d %d -%d 0" % (varmap[("r", resident.id, p)],
                                          varmap[("r", resident.id, p)]+1,
                                          varmap[("h", hospital.id, q)]+1)
            # Clause 6
            encoding += "-%d %d %d 0" % (varmap[("h", hospital.id, q)],
                                         varmap[("h", hospital.id, q)]+1,
                                         varmap[("r", resident.id, p)])
            encoding += "-%d %d -%d 0" % (varmap[("h", hospital.id, q)],
                                          varmap[("h", hospital.id, q)]+1,
                                          varmap[("r", resident.id, p)]+1)


