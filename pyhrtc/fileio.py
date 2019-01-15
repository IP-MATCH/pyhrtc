"""Read, write and inspect instances of HRTC (and specialisations like SMTI,
HRT etc.)
"""


import csv
import re

from pyhrtc.basics import Agent, Couple, CapacitatedAgent, Instance
from pyhrtc.weightedinstance import WeightedAgent, WeightedInstance

JUST_NUMBER_RE = re.compile(r'^\d+$')


class UnknownFormatException(Exception):
    """An unknown format for the instance file."""

    def __init__(self):
        super().__init__("pyhrtc either does not support or "
                         "cannot read this file format.")


INSTANCE_READERS = {}
"""This dictionary should contain functions that, for a given variant of
instance format, takes as input a filename and returns an Instance of that
problem.
"""


def read_hrtc_glasgow_hrtc_nocolon(filename):
    """Reads in an instance of HRTC from filename in the usual Glasgow format,
    but with no colons.
    """
    with open(filename, "r") as infile:
        num_single_residents = int(infile.readline().rstrip())
        num_couples = int(infile.readline().rstrip())
        num_hospitals = int(infile.readline().rstrip())
        instance = Instance()
        for _ in range(num_single_residents):
            line = infile.readline()
            ident = int(line.split()[0])
            doc = Agent(ident)
            doc.read_preferences(line.split()[1:])
            instance.add_agent_left(doc)
        for _ in range(num_couples):
            line = infile.readline()
            id1 = int(line.split()[0])
            id2 = int(line.split()[1])
            couple = Couple(id1, id2)
            couple.read_preferences(line.split()[2:])
            instance.add_couple_left(couple)
        for _ in range(num_hospitals):
            line = infile.readline()
            ident = int(line.split()[0])
            cap = int(line.split()[1])
            hospital = CapacitatedAgent(ident, cap)
            hospital.read_preferences(line.split()[2:])
            instance.add_agent_right(hospital)
    return instance


def read_hrt_glasgow_nocolon(filename):
    """Reads in an instance of HRT from filename in the usual Glasgow format,
    except that the first line is a zero, the number of (single-only) residents
    is on the second line and the number of hospitals is on the third.
    """
    with open(filename, "r") as infile:
        infile.readline()  # First line is just 0
        num_doctor = int(infile.readline().rstrip())
        num_hospital = int(infile.readline().rstrip())
        instance = Instance()
        for _ in range(num_doctor):
            line = infile.readline()
            ident = int(line.split()[0])
            doctor = Agent(ident)
            doctor.read_preferences(line.split()[1:])
            instance.add_agent_left(doctor)
        for _ in range(num_hospital):
            line = infile.readline()
            ident = int(line.split()[0])
            hospital = CapacitatedAgent(ident, int(line.split()[1]))
            hospital.read_preferences(line.split()[2:])
            instance.add_agent_right(hospital)
    return instance


def read_iain_instance(filename):
    """Reads in an instance of HRTC from filename in Iain's format.
    """
    with open(filename, "r") as infile:
        total_num_residents = int(infile.readline().rstrip())
        num_hospitals = int(infile.readline().rstrip())
        num_couples = int(infile.readline().rstrip())
        num_single_residents = total_num_residents - 2*num_couples
        infile.readline()  # number jobs
        infile.readline()  # min pref list
        infile.readline()  # max pref list
        infile.readline()  # isEventDist
        infile.readline()  # res Popularity
        infile.readline()  # hos Popularity
        infile.readline()  # empty line
        instance = Instance()
        for _ in range(num_couples):
            line = infile.readline().rstrip()
            line_b = infile.readline().rstrip()
            ident = int(line.split()[0])
            ident2 = int(line_b.split()[0])
            couple = Couple(ident, ident2)
            couple.read_individual_preferences(line.split()[1:],
                                               line_b.split()[1:])
            instance.add_couple_left(couple)
        for _ in range(num_single_residents):
            line = infile.readline()
            ident = int(line.split()[0])
            doc = Agent(ident)
            doc.read_preferences(line.split()[1:])
            instance.add_agent_left(doc)
        for _ in range(num_hospitals):
            line = infile.readline()
            ident = int(line.split()[0])
            hospital = CapacitatedAgent(ident, int(line.split()[1]))
            hospital.read_preferences(line.split()[2:])
            instance.add_agent_right(hospital)
    return instance


def read_smti_grp_table(filename):
    """Reads an SMTI-GRP instance from a CSV file. The first row and column are
    expected to be identifiers.
    :param filename: The name of the file containing the instance
    :type filename: string
    :return: the instance
    :rtype: WeightedInstance
    """
    ones = {}
    twos = {}
    with open(filename, "r") as infile:
        reader = csv.DictReader(infile)
        topleft_header = reader.fieldnames[0]
        for one_id in reader.fieldnames[1:]:
            ones[one_id] = WeightedAgent(one_id)
        for row in reader:
            two_id = row[topleft_header]
            two = WeightedAgent(two_id)
            for one_id, weight in row.items():
                if one_id == topleft_header:
                    continue
                weight = float(weight)
                two.add_weight(one_id, weight)
                ones[one_id].add_weight(two.ident, weight)
            twos[two_id] = two
    return WeightedInstance(ones, twos)


# Register the instance reader
INSTANCE_READERS["Glasgow_HRTC_nocolon"] = read_hrtc_glasgow_hrtc_nocolon
INSTANCE_READERS["Iain"] = read_iain_instance
INSTANCE_READERS["Glasgow_HRT_extraline"] = read_hrt_glasgow_nocolon
INSTANCE_READERS["SMTI-GRP Table"] = read_smti_grp_table


def write_hrtc_glasgow_hrtc_nocolon(instance, filename):
    """Writes an Instance to a file in the Glasgow HRTC, without colons.
    """
    write_hrtc_glasgow_hrtc(instance, filename, False)


def write_hrtc_glasgow_hrtc_colon(instance, filename):
    """Writes an Instance to a file in the Glasgow HRTC, with colons.
    """
    write_hrtc_glasgow_hrtc(instance, filename, True)


def write_hrtc_glasgow_hrtc(instance, filename, colon):
    """Writes an Instance to a file in the Glasgow HRTC, either with or without
    colons.
    """
    if colon:
        colon = ":"
    else:
        colon = ""
    with open(filename, "w") as outfile:
        outfile.write("%d\n" % instance.number_of_single_residents_left())
        outfile.write("%d\n" % instance.number_of_couples_left())
        outfile.write("%d\n" % instance.number_of_single_agents_right())
        for agent in instance.single_agents_left:
            outfile.write("%s%s %s\n" % (agent.ident, colon,
                                         agent.preference_string()))
        for couple in instance.couples_left:
            outfile.write("%s%s %s\n" % (couple.split_ident(), colon,
                                         couple.preference_string()))
        for agent in instance.single_agents_right:
            outfile.write("%s%s %d%s %s\n" % (agent.ident, colon,
                                              agent.capacity, colon,
                                              agent.preference_string()))


Instance.add_writer("Glasgow_HRTC_nocolon", write_hrtc_glasgow_hrtc_nocolon)
Instance.add_writer("Glasgow_HRTC_colon", write_hrtc_glasgow_hrtc_colon)


def read_hrtc(filename):
    """Reads an instance of HRTC from the given file and returns the resulting
    Instance object.
    """
    with open(filename, "r") as infile:
        firstline = infile.readline().rstrip()
        variant = 0
        try:
            if "," in firstline:
                variant = "SMTI-GRP Table"
            elif int(firstline) == 0:
                variant = "Glasgow_HRT_extraline"
            else:
                #  second_line contains nothing to help us identify
                infile.readline().rstrip()
                third_line = infile.readline().rstrip()
                if ":" in third_line:
                    variant = "Glasgow_HRT_colon"
                elif JUST_NUMBER_RE.match(third_line):
                    fourth_line = infile.readline().rstrip()
                    if ":" in fourth_line:
                        variant = "Glasgow_HRTC_colon"
                    else:
                        infile.readline()  # 5th line
                        infile.readline()  # 6th line
                        seventh_line = infile.readline().rstrip()
                        if "false" in seventh_line or "true" in seventh_line:
                            variant = "Iain"
                        else:
                            variant = "Glasgow_HRTC_nocolon"
        except ValueError:
            variant = firstline

    if variant in INSTANCE_READERS:
        return INSTANCE_READERS[variant](filename)
    raise UnknownFormatException
