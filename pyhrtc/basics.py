"""Basic elements of HRTC problems."""


import random


def grouped(things):
    """Given some iterable object, returns an iterator that goes through the
    things in the object two at a time.
    """
    return zip(*[iter(things)]*2)


class Agent():
    """An agent."""

    def __init__(self, ident):
        self._ident = ident
        self._prefs = []
        self._num_prefs = None
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
    def num_preferences(self):
        """The number of preferences of this agent, aka the length of its
        preference list.
        """
        if self._num_prefs is None:
            self._num_prefs = sum([len(x) for x in self.preferences])
        return self._num_prefs

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
        self._num_prefs = None

    def rank_of(self, other):
        """Find the rank of other according to this agent.
        """
        for index, group in enumerate(self._prefs):
            if other.id in group:
                return index
        return -1

    def position_of(self, other):
        """Find the position of other in this preference list. Note that this
        is not the same as rank, this function assumes an ordering on the
        elements within a tie, and gives an absolute count on the number of
        agents before it.
        """
        count = 0
        for group in self._prefs:
            for item in group:
                if item == other.id:
                    return count
                count += 1
        return -1

    def make_random_preferences(self, options, tie_density=0, length=None):
        """Create a random preference list from the list options, with the
        given tie density. If length is given, then stop assigning preferences
        once "length" items have been added.
        """
        if length:
            chosen = random.sample(options, length)
        else:
            chosen = list(options)  # Copy so we don't shuffle the original
        random.shuffle(chosen)
        # Reset preferences
        self._prefs = []
        current_tie = []
        for item in chosen:
            # If there is a tie, and we want to end it, do so;
            if current_tie and random.random() >= tie_density:
                # Start a new tie group
                self._prefs.append(current_tie)
                current_tie = []
            current_tie.append(item)
        # Don't forget to add the last tie
        self._prefs.append(current_tie)

    def make_master_list_preferences(self, options, master_list, length=None):
        """Create a preference list from the list options, with the given tie
        density and master list. If length is given, then stop assigning
        preferences once "length" items have been added.
        """
        chosen = []
        for item in master_list:
            if item in options:
                chosen.append(item)
                if length and len(chosen) == length:
                    break
        # Reset preferences
        self._prefs = []
        for item in chosen:
            self._prefs.append([item])

    def acceptable_agents(self):
        """Get the list of acceptable agents for this Agent."""
        agents = []
        for tie in self._prefs:
            agents.extend(tie)
        return agents

    def is_acceptable(self, ident):
        """Is the given agent (as identified by their identifier) acceptable
        for this Agent?
        """
        for tie in self._prefs:
            if ident in tie:
                return True
        return False

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
                if token[0] == "(" and token[-1] != ")":
                    in_tie = True
                    current.append(int(token[1:]))
                else:
                    # Not at all a tie
                    if token[0] == "(" and token[-1] == ")":
                        token = token[1:-1]
                    self._prefs.append([int(token)])
            else:
                # Inside a tie
                if token[-1] == ")":
                    # Tie ends here
                    current.append(int(token[:-1]))
                    self._prefs.append(current)
                    in_tie = False
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

    def read_individual_preferences(self, tokens_a, tokens_b):
        """Read in and assign preferences, when preferences are given in two
        distinct lists of strings.
        """
        self._prefs = []
        for one, two in zip(tokens_a, tokens_b):
            self._prefs.append([int(one), int(two)])

    def read_preferences(self, tokens):
        """Read in and assign preferences based on the given string.
        """
        # First reset preferences
        self._prefs = []
        in_tie = False
        current = []
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
            return "(%s)" % (" ".join(["%s %s" % (c[0], c[1])
                                       for c in tie_as_list]))
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
                    raise NotImplementedError("pyhrtc can't interleave " +
                                              "from doctors with ties")
                if first_ind == second_ind:
                    new_prefs.append([(first_pref[0], second_pref[0])])
                else:
                    first_alt = doc1.preferences[second_ind]
                    second_alt = doc2.preferences[first_ind]
                    new_prefs.append([(first_pref[0], second_pref[0]),
                                      (first_alt[0], second_alt[0])])
        couple.preferences = new_prefs
        return couple
