"""Read, write and inspect instances of HRTC (and specialisations like SMTI,
HRT etc.)
"""


import re

from pyhrtc.basics import Agent, Couple, Hospital

JUST_NUMBER_RE = re.compile(r'^\d+$')


class UnknownFormatException(Exception):
    """An unknown format for the instance file."""

    def __init__(self):
        super().__init__("pyhrtc either does not support or " +
                         "cannot read this file format.")


INSTANCE_READERS = {}
"""This dictionary should contain functions that, for a given variant of
instance format, takes as input a filename and returns an Instance of that
problem.
"""

INSTANCE_WRITERS = {}
"""This dictionary should contain functions that, for a given variant of
instance format, takes as input an Instance object and a filename, and writes
said instance to the file.
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
            instance.add_doctor(doc)
        for _ in range(num_couples):
            line = infile.readline()
            id1 = int(line.split()[0])
            id2 = int(line.split()[1])
            couple = Couple(id1, id2)
            couple.read_preferences(line.split()[2:])
            instance.add_couple(couple)
        for _ in range(num_hospitals):
            line = infile.readline()
            ident = int(line.split()[0])
            cap = int(line.split()[1])
            hospital = Hospital(ident, cap)
            hospital.read_preferences(line.split()[2:])
            instance.add_hospital(hospital)
    return instance


def read_smti_glasgow_nocolon(filename):
    """Reads in an instance of SMTI from filename in the usual Glasgow format,
    except that agents from the second set are actually "hospitals" with
    capacity 1.
    """
    with open(filename, "r") as infile:
        infile.readline()  # First line is just 0
        num_hospital = int(infile.readline().rstrip())
        num_doctor = int(infile.readline().rstrip())
        instance = Instance()
        for _ in range(num_hospital):
            line = infile.readline()
            ident = int(line.split()[0])
            hospital = Hospital(ident, 1)
            hospital.read_preferences(line.split()[1:])
            instance.add_hospital(hospital)
        for _ in range(num_doctor):
            line = infile.readline()
            ident = int(line.split()[0])
            doctor = Agent(ident)
            doctor.read_preferences(line.split()[2:])
            instance.add_doctor(doctor)
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
            instance.add_couple(couple)
        for _ in range(num_single_residents):
            line = infile.readline()
            ident = int(line.split()[0])
            doc = Agent(ident)
            doc.read_preferences(line.split()[1:])
            instance.add_doctor(doc)
        for _ in range(num_hospitals):
            line = infile.readline()
            ident = int(line.split()[0])
            hospital = Hospital(ident, int(line.split()[1]))
            hospital.read_preferences(line.split()[2:])
            instance.add_hospital(hospital)
    return instance


# Register the instance reader
INSTANCE_READERS["Glasgow_HRTC_nocolon"] = read_hrtc_glasgow_hrtc_nocolon
INSTANCE_READERS["Iain"] = read_iain_instance
INSTANCE_READERS["Glasgow_SMTI_extraline"] = read_smti_glasgow_nocolon


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
        outfile.write("%d\n" % instance.get_number_of_single_residents())
        outfile.write("%d\n" % instance.get_number_of_couples())
        outfile.write("%d\n" % instance.get_number_of_hospitals())
        for resident in instance.single_residents:
            outfile.write("%s%s %s\n" % (resident.ident, colon,
                                         resident.preference_string()))
        for couple in instance.couples:
            outfile.write("%s%s %s\n" % (couple.split_ident(), colon,
                                         couple.preference_string()))
        for hospital in instance.hospitals:
            outfile.write("%s%s %d%s %s\n" % (hospital.ident, colon,
                                              hospital.capacity, colon,
                                              hospital.preference_string()))


INSTANCE_WRITERS["Glasgow_HRTC_nocolon"] = write_hrtc_glasgow_hrtc_nocolon
INSTANCE_WRITERS["Glasgow_HRTC_colon"] = write_hrtc_glasgow_hrtc_colon


def read_hrtc(filename):
    """Reads an instance of HRTC from the given file and returns the resulting
    Instance object.
    """
    with open(filename, "r") as infile:
        firstline = infile.readline().rstrip()
        variant = 0
        try:
            first = int(firstline)
            if first == 0:
                variant = "Glasgow_SMTI_extraline"
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


class Instance():
    """An instance of HRTC.
    """

    def __init__(self, single_residents=None, couples=None, hospitals=None):
        """Create an Instance. Note that if any of the parameters are passed
        in, they are used as is (i.e. not copied) so don't modify the dicts
        after creating an instance.

        :param dict single_residents: A dictionary of single residents
        :param dict couples: A dictionary of couples
        :param dict hospitals: A dictionary of hospitals
        """
        super().__init__()

        # Each of these is a map from ID to the actual entity, so make sure
        # you set IDs appropriately
        if single_residents:
            self._single_doctors = single_residents
        else:
            self._single_doctors = {}
        if couples:
            self._couples = couples
        else:
            self._couples = {}
        if hospitals:
            self._hospitals = hospitals
        else:
            self._hospitals = {}

    def get_number_of_single_residents(self) -> int:
        """The number of single residents."""
        return len(self._single_doctors)

    def get_number_of_couples(self) -> int:
        """The number of couples."""
        return len(self._couples)

    def get_number_of_hospitals(self) -> int:
        """The number of hospitals."""
        return len(self._hospitals)

    @property
    def single_residents(self):
        """Returns a list of all single residents."""
        return list(self._single_doctors.values())

    @single_residents.setter
    def single_residents(self, new):
        """Not allowed."""
        raise NotImplementedError

    @property
    def couples(self):
        """Returns a list of all the couples."""
        return list(self._couples.values())

    @couples.setter
    def couples(self, new):
        """Not allowed."""
        raise NotImplementedError

    @property
    def hospitals(self):
        """Returns a list of all the hospitals."""
        return list(self._hospitals.values())

    @hospitals.setter
    def hospitals(self, new):
        """Not allowed."""
        raise NotImplementedError

    def add_doctor(self, doctor):
        """Add a doctor to this instance.
        """
        self._single_doctors[doctor.ident] = doctor

    def add_couple(self, couple):
        """Adds a couple to this instance.
        """
        self._couples[couple.ident] = couple

    def add_hospital(self, hospital):
        """Adds a hospital to this instance.
        """
        self._hospitals[hospital.ident] = hospital

    def make_couple_from_doctor_pair(self, number=1):
        """Take "number x 2" doctors, and turn them into couples by
        interleaving. Note that there is no reliable way to select which
        doctors.
        """
        while number:
            if len(self._single_doctors) < 2:
                raise LookupError("Don't have enough doctors left")
            id1, id2 = [self._single_doctors.keys()][-2:]  # pylint: disable=unbalanced-tuple-unpacking, line-too-long
            first = self._single_doctors[id1]
            second = self._single_doctors[id2]
            couple = Couple.from_two_doctors(first, second)
            self._couples[couple.ident] = couple
            del self._single_doctors[id1]
            del self._single_doctors[id2]
            number -= 1

    def is_SMTI(self):
        """Returns true if this is an instance of SMTI (aka there are no
        couples, and each "hospital" has capacity 1.
        """
        if self.get_number_of_couples() != 0:
            return False
        for hospital in self.hospitals:
            if hospital.capacity != 1:
                return False
        return True

    def write_to_file(self, filename, variant="Glasgow_HRTC_nocolon"):
        """Writes the instance to a file."""
        if variant in INSTANCE_WRITERS:
            INSTANCE_WRITERS[variant](self, filename)
        else:
            raise UnknownFormatException
