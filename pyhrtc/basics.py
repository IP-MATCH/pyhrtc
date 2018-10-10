"""Basic elements of HRTC problems."""


def grouped(things):
    """Given some iterable object, returns an iterator that goes through the
    things in the object two at a time.
    """
    return zip(*[iter(things)]*2)


class Agent(object):
    """An agent."""

    def __init__(self, ident):
        self._ident = ident
        self._prefs = []
        # This will be a list of lists, with each inner list corresponding to a
        # tie group

    @property
    def ident(self):
        """The ID of this agent."""
        return self._ident

    @ident.setter
    def ident(self, new):
        """We cannot change the ID of an agent"""
        raise NotImplementedError

    @property
    def preferences(self):
        """Return the preferences, as a list of tie groups. Entries which are
        not in a tie at all still appear by themselvs in a list (i.e. 1 (2 3)
        is [[1], [2, 3]]).
        """
        return self._prefs

    @preferences.setter
    def preferences(self, new):
        """Set the preferences of this agent. This must be a list of lists,
        such that each tie group is a list. For instance, 1 (2 3) should be
        passed in as [[1], [2, 3]].
        """
        self._prefs = new

    def preference_string(self):
        """Returns the string of preferences for this agent."""
        def format_tie(tie_as_list):
            """Given a set of tied elements, returns a string representing
            them, by surrounding with brackets if there is more than one item.
            """
            if not tie_as_list:
                return ""
            if len(tie_as_list) == 1:
                return "%s" % tie_as_list[0]
            return "(%s)" % (" ".join(tie_as_list))
        return " ".join([format_tie(tie) for tie in self.preferences])

    def read_preferences(self, tokens):
        """Read in and assign preferences based on the given string.
        """
        # First reset preferences
        self._prefs = []
        in_tie = False
        current = []
        for token in tokens:
            if not in_tie:
                # Tie starting
                if token[0] == "(":
                    in_tie = True
                    current.append(int(token[1:]))
                else:
                    # Not at all a tie
                    self._prefs.append([int(token)])
            else:
                # Inside a tie
                if token[-1] == ")":
                    # Tie ends here
                    current.append(int(token[:-1]))
                    self._prefs.append(current)
                    current = []
                else:
                    # Tie keeps going
                    current.append(int(token))



class Hospital(Agent):
    """An agent with capacity."""

    def __init__(self, ident, capacity):
        super().__init__(ident)
        self._capacity = capacity

    @property
    def capacity(self):
        """How many doctors this hospital can support."""
        return self._capacity

    @capacity.setter
    def capacity(self, new):
        """Not supported."""
        raise NotImplementedError

class Couple(Agent):
    """Two agents together."""

    def __init__(self, first, second):
        super().__init__("(%s,%s)" % (first, second))
        self._first = first
        self._second = second

    def split_ident(self):
        """Returns a string representation of the two individual doctors,
        rather than the combined couple.
        """
        return "%s %s" % (self._first, self._second)

    def read_preferences(self, tokens):
        """Read in and assign preferences based on the given string.
        """
        # First reset preferences
        self._prefs = []
        in_tie = False
        current = []
        print(tokens)
        for token1, token2 in grouped(tokens):
            if not in_tie:
                # Tie starting
                if token1[0] == "(":
                    in_tie = True
                    pref = (int(token1[1:]), int(token2))
                    current.append(pref)
                else:
                    # Not at all a tie
                    self._prefs.append([(int(token1), int(token2))])
            else:
                # Inside a tie
                if token2[-1] == ")":
                    # Tie ends here
                    current.append((int(token1), int(token2[:-1])))
                    self._prefs.append(current)
                    current = []
                else:
                    # Tie keeps going
                    current.append((int(token1), int(token2)))

    def preference_string(self):
        """Returns the string of preferences for this agent."""
        def format_tie(tie_as_list):
            """Given a set of tied elements, returns a string representing
            them, by surrounding with brackets if there is more than one item.
            """
            if not tie_as_list:
                return ""
            if len(tie_as_list) == 1:
                return "%s %s" % (tie_as_list[0][0], tie_as_list[0][1])
            return "(%s)" % (" ".join(["%s %s" % (c[0], c[1]) for c in tie_as_list]))
        return " ".join([format_tie(tie) for tie in self.preferences])

    @staticmethod
    def from_two_doctors(doc1: Agent, doc2: Agent):
        """Given two doctors, create a Couple from them.
        """
        couple = Couple(doc1.ident, doc2.ident)
        new_prefs = []
        for second_ind, second_pref in enumerate(doc2.preferences):
            for first_ind, first_pref in enumerate(doc1.preferences):
                if second_ind < first_ind:
                    continue
                if len(first_pref) != 1 or len(second_pref) != 1:
                    raise NotImplementedError("pyhrtc can't interleave from doctors with ties")
                if first_ind == second_ind:
                    new_prefs.append([(first_pref[0], second_pref[0])])
                else:
                    first_alt = doc1.preferences[second_ind]
                    second_alt = doc2.preferences[first_ind]
                    new_prefs.append([(first_pref[0], second_pref[0]),
                                      (first_alt[0], second_alt[0])])
        couple.preferences = new_prefs
        return couple
